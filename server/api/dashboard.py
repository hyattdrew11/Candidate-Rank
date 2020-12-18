#! CANDIDATE API 
import os
import uuid
import requests
import base64 
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from flask import Flask, Blueprint, jsonify, request, current_app, json, send_from_directory, jsonify, make_response

import http.client
import jwt
import requests
import secrets
import json
from time import time
from time import sleep

from server.controllers.organizationController 	import OrganizationController
from server.controllers.userController   		import UserController
from server.controllers.surveyController   		import SurveyController
from server.controllers.candidateController 	import CandidateController
from server.controllers.taskController 			import TaskController
from server.controllers.emailController import EmailController
from flask_jwt_extended import (JWTManager, jwt_required)
import s3fs
from werkzeug.utils import secure_filename
# GLOBAL VARIABLES
fs 						= s3fs.S3FileSystem(anon=False)
basedir 				= os.path.abspath(os.path.dirname(__file__))
OrganizationController 	= OrganizationController()
UserController 			= UserController()
SurveyController 		= SurveyController()
CandidateController 	= CandidateController()
TaskController 			= TaskController()
EmailController 		= EmailController()
# INITIALIZE ROUTE BLUEPRINT
mod = Blueprint('dashboard', __name__)

zoom_client = 'SekFiZ4yTliCtLOT1BjwOQ'
zoom_secret = 'BP5IOQtWwkmyPQAHQjIpH0sQSOFdiw1xHinP'

def token_required(f):
	@wraps(f)
	def _verify(*args, **kwargs):
		print("TOKEN REQUIRED")
		auth_headers = request.headers.get('Authorization', '').split()
		invalid_msg = {
			'message': 'Invalid token. Registeration and / or authentication required',
			'authenticated': False
		}
		expired_msg = {
			'message': 'Expired token. Reauthentication required.',
			'authenticated': False
		}

		if len(auth_headers) != 2:
			print("INVALID TOKEN !=2")
			return jsonify(invalid_msg), 401

		try:
			token = auth_headers[1]
			print(token)
			data = jwt.decode(token, current_app.config['SECRET_KEY'])
			print(data)
			print(data['identity'])
			user = UserController.getUser(data['identity'],'')
			if not user:
				print("USER NOT FOUND")
				raise RuntimeError('User not found')
			return f(data, *args, **kwargs)
		except jwt.ExpiredSignatureError:
			print("EXPIRED SIGNATURE ERROR")
			print(expired_msg)
			return jsonify(expired_msg), 401 # 401 is Unauthorized HTTP status code
		except (jwt.InvalidTokenError, Exception) as e:
			print("INVALID TOKEN InvalidTokenError")
			print(e)
			return jsonify(invalid_msg), 401

	return _verify

def generateToken():
    token = jwt.encode(
        # Create a payload of the token containing API Key & expiration time
        {"iss": zoom_client, "exp": time() + 5000},
        # Secret used to generate token signature
        zoom_secret,
        # Specify the hashing alg
        algorithm='HS256'
        # Convert token to utf-8
    ).decode('utf-8')

    return token


@mod.route('/admin/<organization>', methods=('GET',) )
# @token_required
# def admin(data, organization):
def admin(organization):
	# GET ALL FILES FOR THIS ORGANIZATION
	files = []
	read  = fs.find(''+current_app.config['S3_BUCKET']+'/'+organization+'/')
	for x in read:
		if x.endswith('/'):
			print("SKIP DIRECTORY")
		else:
			nameArray = x.rsplit('/', 2)
			fObj = {
				"year" : nameArray[1],
				"name" : nameArray[2],
				"url"  : fs.url(x),
				"path" : x,
			}
			files.append(fObj)

	organization = OrganizationController.getOrganization(organization)
	# GET ALL ORGINIZATION FACULTY AS AN ARRAY OF JSON OBJECTS
	faculty    = UserController.getFaculty(organization)
	# GET ALL ORGINIZATION SURVEYS AS AN ARRAY OF JSON OBJECTS
	surveys    = SurveyController.getSurveys(organization)
	
	response = {
		"success"		: True,
		"error"   		: False,
		"errMsg"  		: '',
		"organization"	: organization,
		"faculty" 		: faculty,
		"surveys" 		: surveys,
		"files" 		: files,
		"tasks" 		: []
	}
	return jsonify(response)



@mod.route('/admin/file/delete', methods=['GET', 'POST'])
def delete():
	data  = request.get_json()
	path = data['path']
	try:
		fs.rm(path)
		response = { 'data' : 'success' }
		return jsonify(response)
	except OSError:
		return make_response(("Error deleting file", 500))



def addFile(s3Path, organization, year, extension):
	q = current_app.task_queue
	job_id = uuid.uuid4()
	job_id = str(job_id)
	if extension == '.zip':
		print(".zip")
		job = q.enqueue('tasks.unzip',job_id, s3Path, organization, year, job_id=job_id, job_timeout=300)
		pjob = q.fetch_job(job_id)
		print(job_id)
		dbjob = TaskController.createTask(job_id, 'unzip', organization, year, 'started', s3Path)
		print(dbjob)
	if extension == '.pdf':
		print(".pdf")
		job = q.enqueue('tasks.getPhoto',job_id,  s3Path, organization, year,  job_id=job_id, job_timeout=300)
		pjob = q.fetch_job(job_id)
		print(job_id)
		dbjob = TaskController.createTask(job_id, 'importing pdf', organization, year, 'started', s3Path)
		print(dbjob)
	if extension == '.csv':
		print(".csv")
		job = q.enqueue('tasks.importCSV', job_id,  s3Path, organization, year,  job_id=job_id, job_timeout=2000)
		pjob = q.fetch_job(job_id)
		print(job_id)
		dbjob = TaskController.createTask(job_id, 'csv validation andimport', organization, year, 'started', s3Path)
		print(dbjob)
	if extension == '.xml':
		print(".xml")
		job = q.enqueue('tasks.importXML', job_id,  s3Path, organization, year,  job_id=job_id, job_timeout=2000)
		pjob = q.fetch_job(job_id)
		print(job_id)
		dbjob = TaskController.createTask(job_id, 'xml validation and import', organization, year, 'started', s3Path)
		print(dbjob)
	else:
		pass
		# job = q.enqueue('worker-queue.tasks.test',job_id,  s3Path, organization, job_id=job_id, job_timeout=300)
		# pjob = q.fetch_job(job_id)
		# print(job_id)
		# dbjob = TaskController.createTask(job_id, 'other', organization, year, 'started', s3Path)
		# print(dbjob)

@mod.route('/admin/upload', methods=['GET', 'POST'])
def upload():
	print("UPLOAD")
	file   = request.files['file']
	org    = request.form['organization']
	year   = request.form['year']

	save_path = os.path.join(current_app.config['UPLOAD_DIR'], secure_filename(file.filename))
	s3Path 	= current_app.config['S3_BUCKET']+'/'+org+'/'+year+'/'+file.filename
	current_chunk = int(request.form['dzchunkindex'])
	# If the file already exists it's ok if we are appending to it,
	# but not if it's new file that would overwrite the existing one
	if os.path.exists(save_path) and current_chunk == 0:
		os.remove(save_path)
		return make_response(("Chunk upload successful", 200))

	try:
		with open(save_path, 'ab') as f:
			f.seek(int(request.form['dzchunkbyteoffset']))
			f.write(file.stream.read())
	except OSError as e:
		print(e)
		return make_response(("Not sure why,but we couldn't write the file to disk", 500))

	total_chunks = int(request.form['dztotalchunkcount'])

	if current_chunk + 1 == total_chunks:
		# 
		print(os.path.getsize(save_path))
		print(int(request.form['dztotalfilesize']))
		# if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
		# 	return make_response(('Size mismatch', 500))
		# else:
		# COPY FILE FROM LOCAL TO S3
		fs.put(save_path, s3Path)
		# RUN ADD FILE FUNCTION TO ADD TASK TO QUEUE 
		ext = os.path.splitext(save_path)
		addFile(s3Path, org, year, ext[1])
		# DELETE LOCAL COPY
		os.remove(save_path)

	else:
		print("chunk complete")

	return make_response(("Chunk upload successful", 200))


@mod.route('/admin/upload/attachment', methods=['GET', 'POST'])
def uploadAttachment():
	file   = request.files['file']
	org    = request.form['organization']
	year   = request.form['year']
	save_path = os.path.join(current_app.config['UPLOAD_DIR'], secure_filename(file.filename))
	s3Path 	= current_app.config['S3_BUCKET']+'/'+org+'/'+year+'/attachments/'+file.filename
	current_chunk = int(request.form['dzchunkindex'])
	# If the file already exists it's ok if we are appending to it,
	# but not if it's new file that would overwrite the existing one
	if os.path.exists(save_path) and current_chunk == 0:
		os.remove(save_path)
		return make_response(("Chunk upload successful", 200))

	try:
		with open(save_path, 'ab') as f:
			f.seek(int(request.form['dzchunkbyteoffset']))
			f.write(file.stream.read())
	except OSError as e:
		print(e)
		return make_response(("Not sure why,but we couldn't write the file to disk", 500))

	total_chunks = int(request.form['dztotalchunkcount'])

	if current_chunk + 1 == total_chunks:

		if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
			return make_response(('Size mismatch', 500))
		else:
			# COPY FILE FROM LOCAL TO S3
			fs.put(save_path, s3Path)
			# DELETE LOCAL COPY
			os.remove(save_path)

	else:
		print("chunk complete")

	return make_response(("Chunk upload successful", 200))


@mod.route('/faculty/<organization>', methods=('GET',) )
# @token_required
# def faculty(data, organization):
def faculty(organization):
	# GET THE ORGANIZATION
	organization = OrganizationController.getOrganization(organization)
	# GET ALL ORGINIZATION CANDIDATES AS AN ARRAY OF JSON OBJECTS
	response = {
		"success"		: True,
		"error"   		: False,
		"organization"	: organization,
	}
	return jsonify(response)


def getZoomUsers():
	userIDS = []
	zUsers 	= []
	conn = http.client.HTTPSConnection("api.zoom.us")
	body = {
  		"page_count": 1,
  		"page_number": 1,
  		"page_size": 45
  	}
	headers = {'authorization': 'Bearer %s' % generateToken(),
               'content-type': 'application/json'}
	r = requests.get('https://api.zoom.us/v2/users/', headers=headers, params=body)
	res = r.json()
	for x in res['users']:
		if x['email'] == "support@candidate-rank.com":
			print("DO NOTHING")
		else:
			zUsers.append(x)
	return zUsers

@mod.route('/finalize-schedule/<organization>', methods=['POST'])
def finalizeSchedule(organization):
	try:
		data 		= request.get_json()
		print("FINALIZE SCHEDULE")
		zoomUsers = getZoomUsers()
		print("SET ORGANIZATION")
		cti 		= int(data['currentTermIndex'])
		candidates 	= data['candidates']
		org 		= OrganizationController.getOrganization(organization)
		print("SET TERM")
		DTE = data['date']
		term 		= org['terms'][cti]
		if zoomUsers and org:
			# FINDATE TERM AND TERM DATE
			print("SET DATES")
			dates = term['dates']
			for di, x in enumerate(dates):
				NEWDTE = x['startDate']
				print(x['startDate'])
				if DTE == NEWDTE:
					print("DATE FOUND")
					dateIndex = di
					rooms = x['rooms']
					interviewLength = x['interviewLength']
					for rInx, room in enumerate(rooms):
						print(len(zoomUsers))
						zoomUser = zoomUsers[rInx]
						# MAKE ZOOM LINKS FOR ALL ACTIVE EVENTS 
						events = room['events']
						evaluators = []
						for ev in room['evaluators']:
							evaluators.append(ev)

						for eInx, event in enumerate(events):
							if 'candidate' in event:
								print("MAKE A ZOOM MEETING")
								EVT = event
								print(EVT['time'])
								Etime = DTE+"T"+EVT['time']+":00+06:00"
								print(Etime)

								meeting = createMeeting(zoomUser, evaluators, Etime, interviewLength)
								events[eInx]['zoom_link'] = meeting['join_url']
								events[eInx]['zoomUser'] = zoomUser

								if meeting:
									print("MEETING TRUE")
								else:
									print("MEETING FALSE")
									# return jsonify(org), 500
									# return 500
							else:
								print("NO CANDIDATE IN EVENT")
								# return jsonify(org), 500
								# return 500
				else:
					# return jsonify(org), 500
					# return 500
					print("DATE != NEWDATE")

			newEvents = events
			org['terms'][cti]['dates'][dateIndex]['finalized'] = True
			org['terms'][cti]['dates'][dateIndex]['events'] = newEvents
			updateOrg = OrganizationController.updateTerms(org)
			# updateOrg = True

			if updateOrg:
				print(org['terms'][cti]['dates'][dateIndex])
				# NOTIFY CANDIDATES
				for x in candidates:
					sleep(1)
					confirmCandidate = EmailController.confirmCandidate(data['date'], x['email'], org)

				return jsonify(org), 201

		else:
			# return 500
			print("ELSE")

	except Exception as e:
		print(e)
		# return 500

@mod.route('/candidate-date/<organization>', methods=['POST'])
def chooseDate(organization):
	# DYNAMO CREATES CANDIDATE FROM POST DATA
	data 		= request.get_json()
	print(data['date'])
	zoomUsers 	= False 
	cti 		= int(data['currentTermIndex'])
	candidate 	= CandidateController.getCandidate(organization, data['uuid'])
	org 		= OrganizationController.getOrganization(organization)
	term 		= org['terms'][cti]
	lastTimeIndex = 0 
	timeSlots 	= []
	newEvents 	= []
	candEvents 	= []
	if candidate and org:
		# GET THE ORGANIZATIONS ADMIN USER FOR ZOOM API CALLS
		user = UserController.getUser(org['admin'], 'password')
		if user:
			zoomUsers = getZoomUsers()
			# SET DATES FOR CURRENT TERM TO DATES VARIABLE
			dates = term['dates']
			checkSlots(dates, data['uuid'])
			for di, x in enumerate(dates):
				if x['startDate'] == data['date']:
					print("START DATE FOUND")
					print(x['startDate'])
					dateIndex = di
					interviewLength = x['interviewLength']
					print(x)
					
					if 'numCandidates' in x:
						print("NUMBER OF CANDIDATES EXISTS")
					else:
						org['terms'][cti]['dates'][dateIndex]['numCandidates'] = 0

					if 'maxCandidates' in x and 'numCandidates' in x:
						numCandidates =  x['numCandidates'] + 1
						maxCandidates =  x['maxCandidates']
						print(numCandidates, maxCandidates)
						if numCandidates > maxCandidates:
							print("TERM HAS MAX CANDIDATES")
							return 500
						else:
							print("DATE IS STILL AVAILABLE")

					else:
						print("NUMBER OF CANDIDATES AND MAX CANDIDATES NOT IN DATE")
						return 500

				else:
					print("DATE NOT FOUND")
					continue
		org['terms'][cti]['dates'][dateIndex]['events'] = newEvents
		candEvents = sorted(candEvents, key=lambda k: k['time'])
		print("•••••••••••••••••••••••••••••••••••••••")
		print("•••••••••••••••••••••••••••••••••••••••")
		print(len(candEvents))
		print("•••••••••••••••••••••••••••••••••••••••")
		print("•••••••••••••••••••••••••••••••••••••••")
		candidate['interview-date'] = data['date']
		updateCandidate = CandidateController.updateCandidate(candidate)
		# confirmCandidate = EmailController.confirmCandidate(data['date'], candidate['email'], org)
		if updateCandidate:
			if 'numCandidates' in org['terms'][cti]['dates'][dateIndex]:
				print("ADD TO NUM CANDIDATES")
				org['terms'][cti]['dates'][dateIndex]['numCandidates'] = org['terms'][cti]['dates'][dateIndex]['numCandidates'] + 1
			else:
				print("DO NOTHING")
			updateOrg = OrganizationController.updateTerms(org)
			if updateOrg:
				return jsonify(updateOrg), 201
			else:
				return 500
		else:
			return 500

	else:
		return 500

def checkSlots(dates, uuid):
	print("CHECK SLOTS FOR RESCHEDULE")
	print(dates)
	for di, x in enumerate(dates):
		rooms = x['rooms']
		for roomIndex, e in enumerate(rooms):
			events = e['events']
			# LOOP THROUGH THE DAYS EVENTS TO FIND OPEN TIME SLOTS FOR CANDIDATE
			for eInx, event in enumerate(events):
				print(roomIndex, len(rooms) - 1)
				if 'candidate' in event and event['candidate']['uuid'] == uuid:
					print("RESETTING EVENT")
					print(uuid)
					newEvt = { "time": event['time'], "zoom_link": "Not Set" }
					events[eInx] = newEvt
					print(events[eInx])
				else:
					print("NO DATES TO RESET")

	return True


def findSlot(events, slots):
	print("FIND A SLOT")
	indices = []
	finalIndex = 0
	print(slots)
	for inx, i in enumerate(events):
		if i['time'] not in slots and i['zoom_link'] == "Not Set":
			print("TIME NOT IN SLOTS AND ZOOM LINK NOT SET")
			print(i)
			finalIndex = inx
			break
		else:
			continue

	if finalIndex > len(events):
		return False
	else: 
		return finalIndex

# def createWaitingRoom(start, end):
# 	print("CREATE WAITING ROOM")
# 	conn = http.client.HTTPSConnection("api.zoom.us")
# 	headers = {'authorization': 'Bearer %s' % generateToken(),
#                'content-type': 'application/json'}
# 	r = requests.get('https://api.zoom.us/v2/users/', headers=headers)
# 	res = r.json()
# 	for x in res['users']:
# 		if x['email'] == "support@candidate-rank.com":
# 			print("DO NOTHING")
# 			body = {
# 				"topic": "Candidate Rank Interview",
# 				"type": 2,
# 				"start_time": time,
# 				"duration": interviewLength,
# 				"schedule_for": zoomUser['id'],
# 				"timezone": "America/Chicago",
# 				"agenda": "Candidate Rank Interview",
# 				"settings": {
# 					"host_video": True,
# 					"waiting_room": False,
# 					"participant_video": True,
# 					"meeting_authentication" : False,
# 					"cn_meeting": False,
# 					"in_meeting": False,
# 					"join_before_host": True,
# 					"mute_upon_entry": False,
# 					"watermark": False,
# 					"use_pmi": False,
# 					"approval_type": 2,
# 					"audio": "both",
# 					"auto_recording": "none",
# 					"registrants_email_notification": True,
# 					# "alternative_hosts" : "support@candidate-rank.com"
# 				}
# 			}
# 			meeting = requests.post('https://api.zoom.us/v2/users/'+zoomUser['id']+'/meetings', 
# 				headers=headers, json=body)
# 			if meeting.ok:
# 				print("MEETING CREATED")
# 				res = meeting.json()
# 				print(res)
# 				res['evaluators'] = evals
# 				return res
# 			else:
# 				print("ERROR CREATING MEETING")
# 				return False

# 			return False
# 		else:
# 			continue

def createMeeting(zoomUser, evaluators, startTime, interviewLength):
	print("CREATE MEETING")
	print(startTime)
	evals = []
	altHosts = ''
	headers = {'authorization': 'Bearer %s' % generateToken(),
               'content-type': 'application/json'}
	for x in evaluators:
		evaluator = UserController.getUser(x['email'], 'password')
		if evaluator:
			print(evaluator)
			altHosts += x['email']
			altHosts += ','
			evals.append(evaluator)
	# zoomID = x['id']
	# zoomUser = secrets.choice(zoomUsers)
	body = {
		"topic": "Candidate Rank Interview",
		"type": 2,
		"start_time": startTime,
		"duration": interviewLength,
		"schedule_for": zoomUser['id'],
		# "timezone": "America/Chicago",
		"agenda": "Candidate Rank Interview",
		"settings": {
			"host_video": True,
			"waiting_room": False,
			"participant_video": True,
			"meeting_authentication" : False,
			"cn_meeting": False,
			"in_meeting": False,
			"join_before_host": True,
			"mute_upon_entry": False,
			"watermark": False,
			"use_pmi": False,
			"approval_type": 2,
			"audio": "both",
			"auto_recording": "none",
			"registrants_email_notification": True,
			# "alternative_hosts" : "support@candidate-rank.com"
		}
	}
	meeting = requests.post('https://api.zoom.us/v2/users/'+zoomUser['id']+'/meetings', 
		headers=headers, json=body)
	if meeting.ok:
		print("MEETING CREATED")
		res = meeting.json()
		res['evaluators'] = evals
		print(res)
		return res
	else:
		print("ERROR CREATING MEETING")
		return False

	return False
			

def refreshZoomApi(data):
    print("REFRESH ZOOM TOKEN")
    print(data)
    error       = None
    email       = data['email']
    user        = UserController.getUser(email,"password")
    if not user:
        print("USER NOT FOUND")
        return "Record not found", 500
    else:
        me      = requests.get('https://api.zoom.us/v2/users/me', headers={'Authorization': 'Bearer ' + user['access_token'] })
        if me.ok:
            print("CONNECTED TO ZOOM")
            # print(me.content)
            return user['access_token']
        else: 
            print("REFRESH ZOOM TOKEN")
            auth_url       = "https://zoom.us/oauth/token?grant_type=refresh_token&refresh_token=" +  user['refresh_token']
            zoom64         = zoom_client+":"+zoom_secret
            # Standard Base64 Encoding
            encodedBytes = base64.b64encode(zoom64.encode("utf-8"))
            encodedStr = str(encodedBytes, "utf-8")
            response = requests.post(auth_url, headers={'Authorization': 'Basic ' + encodedStr})
            if response.ok:
                print("REFRESH TOKEN FOUND UPDATE USER")
                # print(response.content)
                body                    =  json.loads(response.content)
                user['access_token']    =  body['access_token']
                user["token_type"]      =  body['token_type']
                user["refresh_token"]   =  body['refresh_token']
                user["expires_in"]      =  body['expires_in']
                user["scope"]           =  body['scope']
                updatedUser             =  UserController.updateUser(user)
                if updatedUser:
                    return body['access_token']
                else:
                	print(updatedUser)
                	return False
            else:
                print("ZOOM RESPONSE NOT OK")
                return False




# @mod.route('/candidate-date/<organization>', methods=['POST'])
# def chooseDate(organization):
# 	# DYNAMO CREATES CANDIDATE FROM POST DATA
# 	data 		= request.get_json()
# 	zoomUsers 	= False 
# 	cti 		= int(data['currentTermIndex'])
# 	candidate 	= CandidateController.getCandidate(organization, data['uuid'])
# 	org 		= OrganizationController.getOrganization(organization)
# 	term 		= org['terms'][cti]
# 	lastTimeIndex = 0 
# 	timeSlots 	= []
# 	newEvents 	= []
# 	candEvents 	= []
# 	if candidate and org:
# 		# GET THE ORGANIZATIONS ADMIN USER FOR ZOOM API CALLS
# 		user = UserController.getUser(org['admin'], 'password')
# 		if user:
# 			zoomUsers = getZoomUsers()
# 			# SET DATES FOR CURRENT TERM TO DATES VARIABLE
# 			dates = term['dates']
# 			for di, x in enumerate(dates):
# 				if x['startDate'] == data['date']:
# 					print(x['startDate'])
# 					dateIndex = di
# 					rooms = x['rooms']
# 					interviewLength = x['interviewLength']
# 					for roomIndex, e in enumerate(rooms):
# 						zoomUser = zoomUsers[roomIndex]
# 						events = e['events']
# 						evaluators = []
# 						# CONVERT EVALUATOR EMAIL ADDRESSES TO LOWERCASE
# 						for ev in e['evaluators']:
# 							evaluators.append(ev)
# 						# LOOP THROUGH THE DAYS EVENTS TO FIND OPEN TIME SLOTS FOR CANDIDATE
# 						for eInx, event in enumerate(events):
# 							# IF SLOT IS OPEN CONTINUE ON LOOP
# 							if event['zoom_link'] == "Not Set":
# 								# IF THIS TIME SLOT HAS BEEN ASSINED TO CANDIDATE FIND NEXT EARLIEST SLOT AVAILABLE 
# 								if event['time'] in timeSlots:
# 									print("FIND NEXT AVAILABLE SLOT")
# 									print(timeSlots)
# 									# GET THE NEXT AVAILABLE TIME SLOT IN THIS ROOM
# 									lastTimeIndex = findSlot(events , timeSlots)
# 									time = x['startDate']+"T"+events[lastTimeIndex]['time']
# 									timeSlots.append(events[lastTimeIndex]['time'])
# 									meeting = createMeeting(zoomUser, evaluators, time, interviewLength)
# 									if meeting:
# 										print(meeting['join_url'])
# 										# ADD MEETING ID AND PASSOWRD 
# 										newEvent = {
# 											"date": data['date'], 
# 											"time" : events[lastTimeIndex]['time'], 
# 											"zoom_link" : meeting['join_url'], 
# 											"candidate": candidate, 
# 											"evaluators": meeting['evaluators'] 
# 										}
# 										candEvents.append(newEvent)
# 										events[lastTimeIndex] = newEvent
# 										break
# 									else:
# 										return 500
# 								else:
# 									time = x['startDate']+"T"+event['time']
# 									timeSlots.append(event['time'])
# 									meeting = createMeeting(zoomUser, evaluators, time, interviewLength)
# 									if meeting:
# 										print(meeting['join_url'])
# 										newEvent = {
# 											"date": data['date'], 
# 											"time" : event['time'], 
# 											"zoom_start" : meeting['start_url'], 
# 											"zoom_link" : meeting['join_url'], 
# 											"candidate": candidate, 
# 											"evaluators": meeting['evaluators'] 
# 										}
# 										candEvents.append(newEvent)
# 										events[eInx] = newEvent
# 										break
# 									else:
# 										return 500
# 								continue
# 							else:
# 								print("Else")
# 					newEvents = events
# 				else:
# 					print("DATE NOT FOUND")
# 					continue

# 		org['terms'][cti]['dates'][dateIndex]['events'] = newEvents
# 		candEvents = sorted(candEvents, key=lambda k: k['time'])
# 		print("•••••••••••••••••••••••••••••••••••••••")
# 		print("•••••••••••••••••••••••••••••••••••••••")
# 		print(len(candEvents))
# 		print("•••••••••••••••••••••••••••••••••••••••")
# 		print("•••••••••••••••••••••••••••••••••••••••")
# 		candidate['interview-date'] = data['date']
# 		updateCandidate = CandidateController.updateCandidate(candidate)
# 		confirmCandidate = EmailController.confirmCandidate(data['date'], candEvents, candidate['email'], org, interviewLength)
# 		if confirmCandidate and updateCandidate:
# 			updateOrg = OrganizationController.updateTerms(org)
# 			return jsonify(candEvents), 201
# 		else:
# 			return 500

# 	else:
# 		return 500