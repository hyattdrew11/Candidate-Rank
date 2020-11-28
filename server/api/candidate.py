#! CANDIDATE API 
import 	os
import 	uuid
import 	csv
import 	s3fs
from 	functools 								import wraps
from 	datetime 								import datetime, timedelta
from 	werkzeug.security 						import generate_password_hash
from 	flask 									import Flask, Blueprint, jsonify, request, current_app, json, make_response
from 	server.controllers.candidateController  import CandidateController
from 	server.models.candidate               	import Candidate
from 	flask_jwt_extended 						import (JWTManager, jwt_required)
from 	elasticsearch 							import Elasticsearch
from 	werkzeug.utils 							import secure_filename
from 	pdf2image 								import convert_from_bytes

fs = s3fs.S3FileSystem(anon=False)
basedir = os.path.abspath(os.path.dirname(__file__))
controller = CandidateController()
mod = Blueprint('candidate', __name__)

# ADD A CANDIDATE TO AN ORGANIZATION
@mod.route('/update', methods=['POST'])
def update():
	# DYNAMO CREATES CANDIDATE FROM POST DATA
	print("CANDIDATE UPDATE API")
	data = request.get_json()
	c = controller.updateCandidate(data)
	if c:
		return jsonify(data), 201
	else:
		return 500

@mod.route('/add/<organization>', methods=['POST'])
def create(organization):
	# DYNAMO CREATES CANDIDATE FROM POST DATA
	data = request.get_json()
	candidates = controller.createNewCandidates(data)
	if candidates:
		return jsonify(data), 201
	else:
		return 500

# get
@mod.route('/get/<organization>/<uuid>', methods=['POST'])
def get(organization, uuid):
	candidate = controller.getCandidate(organization, uuid)
	if candidate:
		return jsonify(candidate), 201
	else:
		return 500

@mod.route('/all/<organization>/<year>', methods=('GET',))
def allCandidates(organization, year):
	print("GET ALL CANDIDATES FROM ORG")
	# CREATE RESULT ARRAY
	res = []
	# CREATE ELASTICSEARCH NAMESPACE
	es = Elasticsearch([{ 'host': current_app.config['ES_CLUSTER'], 'port': current_app.config['ES_PORT'],  'use_ssl': True  }])
	# SEARCH FOR CANDIDATES
	QS = '(Organization:"' + organization + '") AND (Rank-Term:' + year + ')'
	print(QS)
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
	# print("CANDIDATES")
	# print(candidates)
	# IF NO CANDIDATES RETURN EMPTY ARRAY 
	if not candidates:
		x = []
		# RETURN RESPONSE
		return jsonify(x), 201

	# CREATE SECURE S3 LINKS FOR CANDIDATE PHOTOS AND PDF APPLICAITONS
	for x in candidates['hits']['hits']:
		if x['_source']['Organization'] == organization:
			if "application" in x['_source']:
				if x['_source']['application'] != 'null':
					fa =  x['_source']['application']
					x['_source']['application'] = fs.url(fa, expires=7200)

			if "photo" in x['_source']:
				if x['_source']['photo'] != 'null':
					fp =  x['_source']['photo']
					x['_source']['photo'] = fs.url(fp, expires=7200)
			# APPEND CANDIDATE OBJECTS TO RESPONSE ARRAY 
			res.append(x)

		else:
			print("NOT A CANDIDATE")

	# RETURN RESPONSE
	return jsonify(res)