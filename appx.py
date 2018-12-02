import os
import datetime
import json
from flask import Flask, render_template,request,redirect,url_for,make_response,jsonify # For flask implementation
from pymongo import MongoClient # Database connector
from bson.objectid import ObjectId # For ObjectId to work
from bson.errors import InvalidId # For catching InvalidId exception for ObjectId

class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)

# Get OS ENV
if os.environ.get('APP_PORT') is not None:
	APP_PORT = os.environ.get('APP_PORT')
else:
	APP_PORT = 5000

if os.environ.get('APP_SERVER') is not None:
	APP_SERVER = os.environ.get('APP_SERVER')
else:
	APP_SERVER = '0.0.0.0'

if os.environ.get('MONGODB_SERVER') is not None:
	MONGODB_SERVER = os.environ.get('MONGODB_SERVER')
else:
	print("No MONGODB server specified")

if os.environ.get('MONGODB_PORT') is not None:
	MONGODB_PORT = os.environ.get('MONGODB_PORT')
else:
	MONGODB_PORT = 27017

# Define variables
client = MongoClient(MONGODB_SERVER, int(MONGODB_PORT)) #Configure the connection to the database
db = client.germanov #Select the database
todos = db.todo #Select the collection
author = "Vladimir Germanov"
description = "Python TODO demo app with Flask and Mongodb"
version = "v0.3"

app = Flask(__name__)
title = "Python TODO demo app with Flask and Mongodb - Vladimir Germanov"
heading = "TODO Reminder"

# use the modified encoder class to handle ObjectId & datetime object while jsonifying the response.
app.json_encoder = JSONEncoder

def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('index')


@app.route("/list")
def lists ():
	#Display the all Tasks
	todos_l = todos.find()
	a1="active"
	return render_template('index.html',a1=a1,todos=todos_l,t=title,h=heading)


@app.route("/api/v1/list", methods=['GET'])
def api_lists ():
        result = { "todos" : [] }
        #Display the all Tasks
        todos_l = todos.find()
        if todos_l.count() != 0:
            for todo in todos_l:
                result['todos'].append(todo)
            return jsonify(result)
        else:
            return jsonify( { "result": "No Tasks!" } )


@app.route("/")


@app.route("/uncompleted")
def uncompleted ():
	#Display the Uncompleted Tasks
	todos_l = todos.find({"done":"no"})
	a2="active"
	return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading)


@app.route("/api/v1/uncompleted", methods=['GET'])
def api_uncompleted ():
	result = { "todos" : [] }
	#Display the Uncompleted Tasks
	todos_l = todos.find({"done":"no"})
	if todos_l.count() != 0:
		for todo in todos_l:
			result['todos'].append(todo)
		return jsonify(result)
	else:
		return jsonify( { "result": "No UnCompleted Tasks!" } )


@app.route("/completed")
def completed ():
	#Display the Completed Tasks
	todos_l = todos.find({"done":"yes"})
	a3="active"
	return render_template('index.html',a3=a3,todos=todos_l,t=title,h=heading)


@app.route("/api/v1/completed", methods=['GET'])
def api_completed ():
	result = { "todos" : [] }
	#Display the Completed Tasks
	todos_l = todos.find({"done":"yes"})
	if todos_l.count() != 0:
		for todo in todos_l:
				result['todos'].append(todo)
		return jsonify(result)
	else:
		return jsonify( { "result": "No Completed Tasks!" } )


@app.route("/done")
def done ():
	#Done-or-not ICON
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	if(task[0]["done"]=="yes"):
		todos.update({"_id":ObjectId(id)}, {"$set": {"done":"no"}})
	else:
		todos.update({"_id":ObjectId(id)}, {"$set": {"done":"yes"}})
	redir=redirect_url()	# Re-directed URL i.e. PREVIOUS URL from where it came into this one
	return redirect(redir)


@app.route("/action", methods=['POST'])
def action ():
	#Adding a Task
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	todos.insert({ "name":name, "desc":desc, "date":date, "pr":pr, "done":"no"})
	return redirect("/list")


@app.route("/remove")
def remove ():
	#Deleting a Task with various references
	key=request.values.get("_id")
	todos.remove({"_id":ObjectId(key)})
	return redirect("/")


@app.route("/update")
def update ():
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	return render_template('update.html',tasks=task,h=heading,t=title)


@app.route("/action3", methods=['POST'])
def action3 ():
	#Updating a Task with various references
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	id=request.values.get("_id")
	todos.update({"_id":ObjectId(id)}, {'$set':{ "name":name, "desc":desc, "date":date, "pr":pr }})
	return redirect("/")


@app.route("/search", methods=['GET'])
def search():
	#Searching a Task with various references
	key=request.values.get("key")
	refer=request.values.get("refer")
	if(refer=="id"):
		a2="active"
		try:
			todos_l = todos.find({refer:ObjectId(key)})
			if not todos_l:
				return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading,error="No such ObjectId is present")
		except InvalidId as err:
			pass
			return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading,error="Invalid ObjectId format given\n" + err)
	else:
		todos_l = todos.find({refer:key})
	return render_template('searchlist.html',todos=todos_l,t=title,h=heading)


@app.route("/about")
def about():
	return render_template('about.html',t=title,h=heading,author=author,desc=description,ver=version)


@app.route("/api/v1/about", methods=['GET'])
def api_about():
	return jsonify( { "Author": author, "Description": description, "Version": version } )


@app.route("/api/v1/app_ping", methods=['GET'])
def api_app_ping():
	return "APPPONG"


@app.errorhandler(400)
def not_found_400(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found_404(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)


if __name__ == "__main__":
    app.run(host=APP_SERVER, port=int(APP_PORT), debug=True)
	# Careful with the debug mode...