pip install Flask
pip install Flask-HTTPAuth
pip install Flask-SQLAlchemy
pip install passlib
pip install uuid
pip install datetime


curl -u test:python -i -X GET http://127.0.0.1:5000/api/resource

curl -u test:python -i -X GET http://127.0.0.1:5000/api/token

curl -i -X POST -H "Content-Type: application/json" -d '{"title":"userx1","description":"python is a good language."}' http://127.0.0.1:5000/todo/api/v1/tasks


docs:
http://blog.csdn.net/kaku21/article/details/42489953
http://docs.sqlalchemy.org/en/latest/orm/query.html?highlight=filter_by#sqlalchemy.orm.query.Query.first
https://github.com/miguelgrinberg/REST-auth/blob/master/requirements.txt
html template:
https://www.quora.com/How-do-I-display-a-list-in-HTML5-from-Python-code-using-Flask