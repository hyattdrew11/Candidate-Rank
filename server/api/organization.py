#! USER API 
import logging
import time
import uuid
from functools 									import wraps
from datetime 									import datetime, timedelta
from flask 										import Flask, Blueprint, jsonify, request, current_app, json
from server.controllers.organizationController 	import OrganizationController
from server.controllers.emailController 		import EmailController
from server.controllers.candidateController 	import CandidateController
from server.controllers.userController 			import UserController
from elasticsearch 								import Elasticsearch

OrganizationController 	= OrganizationController()
EmailController 		= EmailController()
CandidateController 	= CandidateController()
UserController 			= UserController()

mod = Blueprint('organization', __name__)

@mod.route('/test', methods=['GET'])
def test():
        return "Success organization"


@mod.route('/admin', methods=('GET',))
def adminOrgs():
	orgs	= OrganizationController.getAll()
	users	= UserController.getAll()
	response = {}
	if orgs and users:
		response['users'] 	= users
		response['orgs'] 	= orgs 
		return jsonify(response), 201
	else:
		return "Record not found", 500

@mod.route('/update', methods=('POST',))
def updateOrganization():
	organization  = request.get_json()
	item	= OrganizationController.updateOrganization(organization)
	if item:
		print(item)
		return jsonify(item), 201
	else:
		return "Record not found", 500

@mod.route('/delete/term/<year>', methods=('POST',))
def delteTerm(year):
	organization  = request.get_json()
	# # CREATE RESULT ARRAY
	res = []
	# # CREATE ELASTICSEARCH NAMESPACE
	es = Elasticsearch([{ 'host': current_app.config['ES_CLUSTER'], 'port': current_app.config['ES_PORT'],  'use_ssl': True }])
	QS = '(Organization:"' + organization['name'] + '") AND (Rank-Term:' + year + ')'
	# # SEARCH FOR CANDIDATES
	candidates = es.search(
		index="candidates", 
		body={ 
			"query": 
				{  
				"query_string": {  "query": QS } 
				} 
		},
		size=10000
	)
	# # ADD LOGIN FOR MORE THAN 1000 CANDIDATES
	if not candidates:
		res = []
		# RETURN RESPONSE
		return jsonify(res), 201
	# CREATE SECURE S3 LINKS FOR CANDIDATE PHOTOS AND PDF APPLICAITONS
	for x in candidates['hits']['hits']:
		candR = CandidateController.deleteCandidate(x)
		es.delete(index='candidates', id=x['_source']['uuid'])

	return jsonify(organization), 201


@mod.route('/update/terms/<organization>', methods=('POST',))
def updateTerms(organization):
	data 	= request.get_json()
	item	= OrganizationController.updateTerms(data)
	if item:
		return jsonify(item), 201
	else:
		return "Record not found", 500

@mod.route('/notification/test', methods=('POST',))
def notificationTest():
	data = request.get_json()
	print(data)
	if "attachments" in data:
		attachments = data['attachments']
	else:
		attachments = []

	notification = EmailController.sendTest(attachments, data['address'], data['header'], data['body'], data['subject'])

	if notification:
		return "success", 201
	else:
		return "Record not found", 500


@mod.route('/notification/send', methods=('POST',))
def inviteCandidate():
	try:
		print("Invite Candidate")
		data = request.get_json()
		data['header'] = data['header']
		if "attachments" in data:
			attachments = data['attachments']
		else:
			attachments = []

		print("TIME SLEEP")
		time.sleep(1)
		notification = EmailController.inviteCandidate(attachments, data['address'], data['header'], data['body'], data['subject'])
		# notification = True
		
		if notification:
			# DYNAMO CREATES CANDIDATE FROM POST DATA
			print("CANDIDATE UPDATE API")
			candidate = data['candidate']
			candidate['invited'] = True
			c = CandidateController.updateCandidate(candidate)
			if c:
				return jsonify(candidate), 201
			else:
				return 500
		else:
			return "Record not found", 500

	except IndexError as e:
		print("============== ERROR INVITING CANDIATE ==============")
		logging.exception(e)

# API ENDPOINT FOR FILE UPLOADS - ONLY ADMIN WILL HAVE UPLOAD CAPABILITES ALLOW ON .PNG TO START
@mod.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return render_template('index.html')