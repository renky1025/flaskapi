## Install libary
* basic libary: `pip install Flask`
* for password : `pip install passlib`
* get uuid: `pip install uuid`
* format datetimes: `pip install datetime`
* support cross domain api: `pip install flask_cors`
* support monogodb: `pip install flask_pymongo`

## details 
* curl -u test:python -i -X GET http://127.0.0.1:5000/api/resource
* curl -u test:python -i -X GET http://127.0.0.1:5000/api/token
* curl -i -X POST -H "Content-Type: application/json" -d '{"title":"userx1","description":"python is a good language."}' http://127.0.0.1:5000/todo/api/v1/tasks

## docs
* http://blog.csdn.net/kaku21/article/details/42489953
* http://docs.sqlalchemy.org/en/latest/orm/query.html?highlight=filter_by#sqlalchemy.orm.query.Query.first
* https://github.com/miguelgrinberg/REST-auth/blob/master/requirements.txt

## html template

* http://flask.pocoo.org/docs/0.12/quickstart/#rendering-templates

## A Python SVG Charts Creator
* `pip install pygal`

## Docker
* build docker image:
`docker build -t flask-tutorial .`

* run docker image:
`docker run -p 8080:8080 flask-tutorial` or run in backend `docker run -p 8080:8080 -d flask-tutorial`