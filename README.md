# Smartnews

#Application for recommending live news obtained from news api 

libraries and api's used -

News Api , Newspaper library for natural language processing and article curation 

Web application built in flask 

[Register for news api access here](https://newsapi.org/register "News Api")

[Link to the newspaper library](https://github.com/codelucas/newspaper "Newspaper library")

**Steps to run the application -**

1)fork the repository 

2)python db_create.py to create user  login database 

3)python run.py to run the application

**Currently completed features -**

1)login(based on openid)

2)news api data extraction

3)passing news api data to curate and process articles

**To be implemented(soon)**

1)curate and process obtained data using newspaper article

2)Ui features 

3)use amazon s3 to store recommended data in  json format 
