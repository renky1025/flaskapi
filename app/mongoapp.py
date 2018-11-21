from flask import Flask, jsonify, abort, make_response, request, json, g, url_for
from bson import json_util
from bson.json_util import dumps
import json
from bson import ObjectId
from pymongo import MongoClient
import os

app = Flask(__name__)

client = MongoClient("mongodb://127.0.0.1:27017") #host uri
db = client.mymongodb #Select the database
todos = db.todo #Select the collection name
users = db.users #Select the collection name

def convertMongoDataToJson(doclist):
    docs = [doc for doc in doclist]
    if docs and len(docs)>0:
        for doc in docs:
            doc["_id"] = str(doc["_id"])
    return docs


def convertResponseJson(data, errcode = 0, message = "Ok"):
    return {
        'data': data,
        "status": {
            "code": errcode,
            "message": message
        }
        # "paging": {
        #     "offset": 0,
        #     "limit": 10,
        #     "total": 10
        # }
    }


@app.route('/user', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def user():
    if request.method == 'GET':
        query = request.args
        data = users.find_one(query)
        return jsonify(data), 200

    data = request.get_json()
    if request.method == 'POST':
        if data.get('name', None) is not None and data.get('email', None) is not None:
            users.insert_one(data)
            return jsonify({'ok': True, 'message': 'User created successfully!'}), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400

    if request.method == 'DELETE':
        if data.get('email', None) is not None:
            db_response = users.delete_one({'email': data['email']})
            if db_response.deleted_count == 1:
                response = {'ok': True, 'message': 'record deleted'}
            else:
                response = {'ok': True, 'message': 'no record found'}
            return jsonify(response), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400

    if request.method == 'PATCH':
        if data.get('query', {}) != {}:
            users.update_one(
                data['query'], {'$set': data.get('payload', {})})
            return jsonify({'ok': True, 'message': 'record updated'}), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400

@app.route("/list/users")
def userlists ():
    #Display the all Tasks
    offset = request.args.get('offset') or 0
    limit = request.args.get('limit') or 10
    users_l = users.find().skip(int(offset)).limit(int(limit))
    docs = convertMongoDataToJson(users_l)
    a1="active"
    return jsonify(convertResponseJson(docs)), 200

@app.route("/list/todos")
def todolists ():
    #Display the all Tasks
    todos_l = todos.find()
    docs = convertMongoDataToJson(todos_l)
    a1="active"
    return jsonify(convertResponseJson(docs)), 200


@app.route("/")
@app.route("/uncompleted")
def tasks ():
    #Display the Uncompleted Tasks
    todos_l = todos.find({"done":"no"})
    docs = [doc for doc in todos_l]
    a2="active"
    return jsonify({'data': docs, 'status': {'code':0, 'message': ''}}), 200


@app.route("/completed")
def completed ():
    #Display the Completed Tasks
    todos_l = todos.find({"done":"yes"})
    a3="active"
    return jsonify({'data':todos_l, 'status': {'code':0, 'message': ''}}), 200

@app.route("/done")
def done ():
    #Done-or-not ICON
    id=request.values.get("_id")
    task=todos.find({"_id":ObjectId(id)})
    if(task[0]["done"]=="yes"):
        todos.update({"_id":ObjectId(id)}, {"$set": {"done":"no"}})
    else:
        todos.update({"_id":ObjectId(id)}, {"$set": {"done":"yes"}})
    redir=redirect_url()    
    return redirect(redir)

@app.route("/action", methods=['POST'])
def action ():
    #Adding a Task
    name=request.values.get("name")
    desc=request.values.get("desc")
    date=request.values.get("date")
    pr=request.values.get("pr")
    todos.insert({ "name":name, "desc":desc, "date":date, "pr":pr, "done":"no"})
    return jsonify({'data':{ "name":name, "desc":desc, "date":date, "pr":pr, "done":"no"}, 'status': {'code':0, 'message': ''}}), 200

@app.route("/remove")
def remove ():
    #Deleting a Task with various references
    key=request.values.get("_id")
    todos.remove({"_id":ObjectId(key)})
    return jsonify({'data':{"_id":ObjectId(key)}, 'status': {'code':0, 'message': ''}}), 200


@app.route("/update")
def update ():
    id=request.values.get("_id")
    task=todos.find({"_id":ObjectId(id)})
    return jsonify({'data':task, 'status': {'code':0, 'message': ''}}), 200

@app.route("/action3", methods=['POST'])
def action3 ():
    #Updating a Task with various references
    name=request.values.get("name")
    desc=request.values.get("desc")
    date=request.values.get("date")
    pr=request.values.get("pr")
    id=request.values.get("_id")
    todos.update({"_id":ObjectId(id)}, {'$set':{ "name":name, "desc":desc, "date":date, "pr":pr }}), 200
    return redirect("/")

@app.route("/search", methods=['GET'])
def search():
    #Searching a Task with various references
    key=request.values.get("key")
    refer=request.values.get("refer")
    if(key=="_id"):
        todos_l = todos.find({refer:ObjectId(key)})
    else:
        todos_l = todos.find({refer:key})
    return jsonify({'data':todos_l, 'status': {'code':0, 'message': ''}}), 200

 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)