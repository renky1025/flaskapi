#!/usr/bin/env python
import os
from flask import Flask, jsonify, abort, make_response, request, json, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.hash import sha256_crypt
import uuid
from datetime import datetime

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:100200@localhost/pythontest'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

class Tasks(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.String(64), primary_key=True)
    title = db.Column(db.String(255), index=True)
    description = db.Column(db.Text)
    done = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow(), onupdate=datetime.utcnow())
    
    def __init__(self,id, title, description, done=False, created=datetime.utcnow()):
        self.id = id
        self.title = title
        self.description = description
        self.done = done
        self.created = created

    def toJSON(self):
        return {'id': self.id,
                 'title': self.title,
                 'description': self.description,
                 'done': self.done,
                 'created': self.created,
                 }
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(255))

    def hash_password(self, password):
        self.password_hash = sha256_crypt.hash(password).split('$')[-1]

    def verify_password(self, password):
        return sha256_crypt.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

@app.route('/todo/api/v1/tasks', methods=['GET'])
def get_tasks():
    tasks_list = iterate_cursor()
    return jsonify({'tasks': tasks_list})


@app.route('/todo/api/v1/tasks/<string:task_id>', methods=['GET'])
def get_task(task_id):
    """
    get request for a single task that matches
    task_id to current id and returns matching task
    curl -i http://localhost:5000/todo/api/v1.0/tasks/<string:task_id>
    """
    task_list = iterate_cursor()
    if len(task_list) == 0:  # error if no match to task
        abort(404)

    return json.dumps(task_list[0])  # returns matched task


@app.route('/todo/api/v1/tasks', methods=['POST'])
def create_task():
    """
    post method to create a new task
    insert into mongo collection and returns
    json object by grabbing the last inserted document
    from collection
    """
    id = str(uuid.uuid1())
    task = Tasks(id=id, title=request.get_json()['title'], description=request.get_json()['description'], done=False )
    db.session.add(task)
    db.session.commit()
    return jsonify({'task': {"id": id}}), 201


@app.route('/todo/api/v1/tasks/<string:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Updates a single task in mongo database matching _id
    passed in URI returns a jsonify'd object
    Test with curl where string is the mongodb "_id":
    curl -i -H "Content-Type: application/json" -X PUT -d "{\"done\":\"True\"}" http://localhost:5000/todo/api/v1/tasks/<ObjectId:task_id>
    """

    # pymongo find_one grabs single matching document searching by _id
    task_dict = Tasks.query.get(task_id)

    if len(task_dict) == 0:
        abort(404)
    if not request.get_json:
        abort(400)

    # update task attributes
    task_dict['title'] = request.get_json('title', task_dict['title'])
    task_dict['description'] = request.get_json(
        'description', task_dict['description'])
    task_dict['done'] = request.get_json('done', task_dict['description'])

    # update todo collection from http request
    if 'title' in request.get_json() & type(request.get_json()) == str:
        Tasks.query().filter(Tasks.id==task_id).update(title= task_dict['title'])
    if 'description' in request.get_json():
        Tasks.query().filter(Tasks.id==task_id).update(description= task_dict['description'])

    if 'done' in request.get_json() & type(request.get_json()) == str:
        Tasks.query().filter(Tasks.id==task_id).update(done= task_dict['done'])
    else:
        abort(404)

    # get updated data from mongodb
    task_list = iterate_cursor()
    return jsonify({'task': task_list})


@app.route('/todo/api/v1/tasks/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task_dict = Tasks.query.filter(Tasks.id==task_id)
    if not task_dict:
        abort(404)

    Tasks.query.filter(Tasks.id==task_id).delete()
    db.session.commit()
    return jsonify({'message': 'delete success: '+ str(task_id), 'result': True})


def iterate_cursor():
    try:
        cursor = Tasks.query.all()
    except:
        print "error", sys.exc_info()[0]

    # iterate over mongodb cursor
    result = []
    for i in cursor:
        result.append(i.toJSON())
    return result


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route("/")
def home():
    return "Tutsplus : Welcome to PyGal Charting Library !! "

# -------------------------------------------
# Charting route which displays the bar chart
# -------------------------------------------
import pygal
from pygal.style import Style
import json
import time
from flask import render_template

@app.route("/bar")
def bar():
    with open('bar.json','r') as bar_file:
        data = json.load(bar_file)
    custom_style = Style(
        colors=('#991515','#1cbc7c'),
        background='#d2ddd9'
        )
    
    chart = pygal.Bar(style = custom_style)
    mark_list = [x['mark'] for x in data]
    chart.add('Annual Mark List',mark_list)
    tourn_list = [x['tournament'] for x in data]
    chart.add('Tournament Score',tourn_list)

    chart.x_labels = [x['year'] for x in data]
    chart.render_to_file('static/images/bar_chart.svg')
    img_url = 'static/images/bar_chart.svg?cache=' + str(time.time())
    return render_template('app.html',image_url = img_url)

if __name__ == '__main__':
    if not os.path.exists('db.mysql'):
        db.create_all()
    app.run(debug=True)


