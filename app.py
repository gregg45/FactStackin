from flask import Flask, jsonify, abort, make_response, request
from pymongo import MongoClient
import uuid

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.factstack
collection = db.development



"""
	TODO:
		1. Get question and assign it an ID.
		2. Someone must provide the question ID and their Answer
		3. The question holder can provide an answer ID + fav/nah (favourite answer/junk answer[flag red])
		4. 


"""


def insert(kind, user_name, team_domain, channel_name, text, q_id, a_id=None):
	collection.insert_one({'kind' : kind,
						   'user_name': user_name,
						   'team_domain' : team_domain,
						   'channel_name' : channel_name,
						   'text' : text,
						   	'q_id' : q_id,
						   	'a_id' : a_id})


def valid_question(q_id):
	return bool(collection.find_one({'q_id' : q_id}))


def question_owner(a_id, user_name):
	ans_info = collection.find_one({'a_id' : a_id})


	if ans_info:

		q_id = ans_info['q_id']
		q_own = collection.find_one({'kind' : 'question',
						 			 'q_id' : q_id})
		return q_own['user_name'], q_own['user_name'] == user_name

	else:
		return False


#Generates 4 char ID
gen_id = lambda: str(uuid.uuid1())[19:23]


TOKEN = "Tfo1UrMzZLtI2k9hJUWj1EBC"

"""
#Checks for auth token.
def valid_token(f):
	def wrapped(*args, **kwargs):
		print request.values['token']
		if all(request, request.values['token'] == "sefeg"):
			return f
		else:
			abort(404)
	return wrapped
"""

@app.route('/ask', methods=['POST'])
def ask():
	if request and request.values['token'] == TOKEN:
		user_name = request.values['user_name']
		team_domain = request.values['team_domain']
		channel_name = request.values['channel_name']
		text = request.values['text']
		q_id = gen_id()

		#Inserting the question into the DB and assigning it an ID.
		insert('question',user_name, team_domain, channel_name, text, q_id)


		return "{} asked `{}` - Question ID: `{}`".format(user_name, text, q_id), 200

	return "Invalid TOKEN.", 200


@app.route('/ans', methods=['POST'])
def ans():
	#check for auth token.

	#Python3 version
	#q_id, *text = request.values['text'].split()

	q_id = request.values['text'].split()[0]
	

	if valid_question(q_id):
		user_name = request.values['user_name']
		team_domain = request.values['team_domain']
		channel_name = request.values['channel_name']
		text = " ".join(request.values['text'].split()[1:])
		a_id = gen_id()		
	
		insert('answer', user_name, team_domain, channel_name, text, q_id, a_id)

		return "{}'s answer to question `{}` is `{}` - Answer ID: `{}`".format(user_name, q_id, text, a_id), 200

	else:
		return "No question with the ID `{}` exists!".format(q_id), 200


@app.route('/fav', methods=['POST'])
def fav():
	ans_user_name = request.values['user_name']
	a_id = request.values['text']
	q_user_name, result = question_owner(a_id, ans_user_name) #returns false fix this....


	if result:
		#return "{} has favourited {}'s answer!".format(q_user_name, ans_user_name), 200

		return jsonify({"response_type" : "in_channel",
						"text" : "{} has favourited {}'s answer!".format(q_user_name, ans_user_name),
						"attachments" : [
							{
								"text" : "placeholder"
							}
						]}), 200


	else:
		return "Only the questions owner can favourite this answer!", 200





@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)		


if __name__ == "__main__":
	app.run(debug=True)
