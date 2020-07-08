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

# @mod.route('/sync/pdf/<organization>/<year>', methods=['POST'])
# def syncPDF(organization, year):
# 	try:
# 		data = request.get_json()
# 		print(data['path'])
# 		s3Path = data['path']
# 		candidate = data['candidate']
# 		candidate['application'] = s3Path
# 		# JPG FROM PDF LOGIC
# 		pages = convert_from_bytes(fs.open(s3Path, 'rb').read())
# 		for i , page in enumerate(pages):
# 			if i == 0:
# 				save_path = os.path.join(current_app.config['UPLOAD_DIR'], secure_filename(candidate['AAMC ID']+'.jpg'))
# 				s3P = current_app.config['S3_BUCKET']+'/'+organization+'/'+year+'/photos/'+candidate['AAMC ID']+'.jpg'
# 				page.save(save_path, 'JPEG')
# 				print(s3P)
# 				fs.put(save_path, s3P)
# 				os.remove(save_path)
# 				candidate['photo'] = s3P

# 		newCandidates 		   		 = []
# 		newCandidates.append(candidate)
# 		query =  controller.updateCandidates(newCandidates)
# 		if query:
# 			res = candidate
# 			fa =  res['application']
# 			res['application'] = fs.url(fa)
# 			fp =  res['photo']
# 			res['photo'] = fs.url(fa)
# 			return jsonify(res), 201
# 		else:
# 			return make_response(("Sync Error", 500))
# 	except OSError as e:
# 		print(e)
# 		return make_response(("Sync Error", 500))

# @mod.route('/add/csv/<organization>/<year>', methods=['POST'])
# def addCSV(organization, year):
# 	# DYNAMO CREATES CANDIDATE FROM POST DATA
# 	try:
# 		data   = request.get_json()
# 		s3Path = data['path']
# 		reader = csv.reader(fs.open(s3Path, "r", encoding="utf-8"))
# 		candidates = []
# 		newCandidates = []
# 		oldCandidates = []
# 		fields = []
# 		count = 0 
# 		for row in reader:
# 			if count == 0:
# 				count += 1
# 				fields = row
# 			else:
# 				candidate = {}
# 				for i, x in enumerate(fields):
# 					try:
# 						if x == '':
# 							print("EMPTY COLMEN")
# 						else:
# 							candidate[''+x+''] = row[i]
# 					except IndexError:
# 						candidate[''+x+''] = ' '

# 				candidate['Organization']	= organization
# 				candidate['photo']			= 'null'
# 				candidate['application']	= 'null'
# 				candidate['Rank-Term']		= year
# 				candidate['interview']		= { 'status' : 'incomplete' }
# 				candidate['survey_1']		= { 'status' : 'incomplete' }
# 				candidate['survey_2']		= { 'status' : 'incomplete' }
# 				candidates.append(candidate)

# 		for i, c in enumerate(candidates):
# 			candidate = controller.getCandidate(organization, year, candidates[i]['AAMC ID'])
# 			if candidate:
# 				print("Skip existing candidate")
# 				oldCandidates.append(c)
# 			else:
# 				print("New candidates")
# 				newCandidates.append(c)

# 		query =  controller.createNewCandidates(newCandidates)
# 		if query:
# 			res = {
# 				'count': count ,
# 				'message': "Import Successful",
# 				'candidates': candidates,
# 				'newCandidates': newCandidates,
# 				'oldCandidates': oldCandidates
# 			}
# 			return jsonify(res), 201
# 		else:
# 			return make_response(("Sync Error", 500))

# 		return jsonify(candidates), 201
# 	except OSError as e:
# 		print(e)
# 		return make_response(("Error  importing candidates", 500))
	# candidates = controller.createNewCandidates(data)
	# if candidates:
	# 	return jsonify(data), 201
	# else:
	# 	return 500
# ADD A CANDIDATE TO AN ORGANIZATION
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
@mod.route('/all/<organization>/<year>', methods=('GET',))
def allCandidates(organization, year):
	# CREATE RESULT ARRAY
	res = []
	# CREATE ELASTICSEARCH NAMESPACE
	es = Elasticsearch([{ 'host': current_app.config['ES_CLUSTER'], 'port': current_app.config['ES_PORT'] }])
	# SEARCH FOR CANDIDATES
	candidates = es.search(
		index="candidates", 
		body={ "query": {  "bool": {  "must": [ { "match": { "Rank-Term":   year } }, { "match": { "Organization": organization } } ] } } },
		size=1000
	)
	# IF NO CANDIDATES RETURN EMPTY ARRAY 
	if not candidates:
		x = []
		# RETURN RESPONSE
		return jsonify(x), 201

	# CREATE SECURE S3 LINKS FOR CANDIDATE PHOTOS AND PDF APPLICAITONS
	for x in candidates['hits']['hits']:
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

	# RETURN RESPONSE
	return jsonify(res)