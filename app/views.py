from flask import json,url_for,render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm
from .models import User
from newspaper import Article
from xml.etree  import ElementTree
from nytimesarticle import articleAPI
import requests
from itertools import repeat
api = articleAPI('your ny times api key')
apikey='Your news api  key'

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    r=requests.get("https://newsapi.org/v1/articles?source=techcrunch&apiKey="+apikey)

    resp=r.json()
    l=len(resp['articles'])
    d = [[] for i in repeat(None, l)]
    p=0
    for i in resp['articles']:
	d[p].append (i['title'])
	d[p].append (i['url'])
       	d[p].append (i['urlToImage'])
       	p=p+1

    return render_template('index.html',
                           title='Home',
                           user=user,
                           tags=d)

@app.route('/recommendation', methods=['POST'])
def recommendation():
    checked = request.form.getlist('channel')
    url_to_clean = checked[0]
    if not url_to_clean:
        return redirect(url_for('index'))

    article = Article(url_to_clean)
    article.download()
    article.parse()

    try:
      html_string = ElementTree.tostring(article.clean_top_node)
    except:
      html_string = "Error converting html to string."

    try:
      article.nlp()
    except:
      artstr="nlp not done"

    a = {
          
         'keywords': str(', '.join(article.keywords)),
         
         }
    
    # do something with checked array
    articles = api.search( q = article.keywords[1], fq = {'headline':article.keywords[1], 'source':['Reuters','AP', 'The New York Times']},begin_date = 20111231 )
    
    news = []
    for i in articles['response']['docs']:
        dic = {}
        dic['id'] = i['_id']
        if i['abstract'] is not None:
            dic['abstract'] = i['abstract'].encode("utf8")
        dic['headline'] = i['headline']['main'].encode("utf8")
        dic['desk'] = i['news_desk']
        dic['date'] = i['pub_date'][0:10] # cutting time of day.
        dic['section'] = i['section_name']
        if i['snippet'] is not None:
            dic['snippet'] = i['snippet'].encode("utf8")
        dic['source'] = i['source']
        dic['type'] = i['type_of_material']
        dic['url'] = i['web_url']
        dic['word_count'] = i['word_count']
        # locations
        locations = []
        for x in range(0,len(i['keywords'])):
            if 'glocations' in i['keywords'][x]['name']:
                locations.append(i['keywords'][x]['value'])
        dic['locations'] = locations
        # subject
        subjects = []
        for x in range(0,len(i['keywords'])):
            if 'subject' in i['keywords'][x]['name']:
                subjects.append(i['keywords'][x]['value'])
        dic['subjects'] = subjects   
        news.append(dic)     								
    
    
    
    return render_template('recommendation.html',tags = checked,dat=news)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.before_request
def before_request():
    g.user = current_user


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])
@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
