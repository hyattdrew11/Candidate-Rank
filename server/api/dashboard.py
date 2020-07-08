#! CANDIDATE API 
import os
import uuid
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from flask import Flask, Blueprint, jsonify, request, current_app, json, send_from_directory, jsonify, make_response
import jwt
from server.controllers.organizationController import OrganizationController
from server.controllers.userController   	import UserController
from server.controllers.surveyController   	import SurveyController
from server.controllers.candidateController import CandidateController
from server.controllers.taskController import TaskController

from flask_jwt_extended import (JWTManager, jwt_required)
import s3fs
fs = s3fs.S3FileSystem(anon=False)

from werkzeug.utils import secure_filename
basedir = os.path.abspath(os.path.dirname(__file__))

OrganizationController 	= OrganizationController()
UserController 			= UserController()
SurveyController 		= SurveyController()
CandidateController 	= CandidateController()
TaskController 			= TaskController()

mod = Blueprint('dashboard', __name__)


def token_required(f):
	@wraps(f)
	def _verify(*args, **kwargs):
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
			return jsonify(invalid_msg), 401

		try:
			token = auth_headers[1]
			data = jwt.decode(token, current_app.config['SECRET_KEY'])
			user = UserController.getUser(data['identity'],'')
			if not user:
				raise RuntimeError('User not found')
			return f(data, *args, **kwargs)
		except jwt.ExpiredSignatureError:
			return jsonify(expired_msg), 401 # 401 is Unauthorized HTTP status code
		except (jwt.InvalidTokenError, Exception) as e:
			print(e)
			return jsonify(invalid_msg), 401

	return _verify



@mod.route('/admin/<organization>/tasks', methods=('GET',) )
def getTasks(organization):
	print('CHECKING TASKS')
	tasks =[]
	myTasks = TaskController.getTasks(organization)
	taskIDS = []
	# PUT MY TASK IDS IN ARRAY
	for x in myTasks:
		taskIDS.append(x['uuid'])

	# GET ID OF TASKS CURRENTLY IN QUEUE
	q = current_app.task_queue
	currentTasks = []
	for x in q.jobs:
		currentTasks.append(x.id)

	# COMPARE ID ARRAY AND APPEND IF ANY CURRENT TASKS
	compare = set(taskIDS) & set(currentTasks)
	for x in myTasks:
		if x['uuid'] in compare:
			tasks.append(x)

	# BUILD SUCCESSFUL JSON RESPONSE
	response = {
		"tasks" : tasks
	}
	return jsonify(response)


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
	# GET MY TASKS FROM DYNAMO
	# tasks =[]
	# myTasks = TaskController.getTasks(organization)
	# taskIDS = []
	# # PUT MY TASK IDS IN ARRAY
	# for x in myTasks:
	# 	taskIDS.append(x['uuid'])

	# # GET ID OF TASKS CURRENTLY IN QUEUE
	# q = current_app.task_queue
	# currentTasks = []
	# for x in q.jobs:
	# 	print(x)
	# 	currentTasks.append(x.id)

	# # COMPARE ID ARRAY AND APPEND IF ANY CURRENT TASKS
	# compare = set(taskIDS) & set(currentTasks)
	# for x in myTasks:
	# 	if x['uuid'] in compare:
	# 		tasks.append(x)

	# BUILD SUCCESSFUL JSON RESPONSE

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
	print("DELETING FILE")
	data  = request.get_json()
	path = data['path']
	print(path)
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
		job = q.enqueue('tasks.unzip',job_id, s3Path, organization, year, job_id=job_id, job_timeout=300)
		pjob = q.fetch_job(job_id)
		print(job_id)
		dbjob = TaskController.createTask(job_id, 'unzip', organization, year, 'started', s3Path)
		print(dbjob)
	if extension == '.pdf':
		job = q.enqueue('tasks.getPhoto',job_id,  s3Path, organization, year,  job_id=job_id, job_timeout=300)
		pjob = q.fetch_job(job_id)
		print(job_id)
		dbjob = TaskController.createTask(job_id, 'importing pdf', organization, year, 'started', s3Path)
		print(dbjob)
	if extension == '.csv':
		job = q.enqueue('tasks.importCSV', job_id,  s3Path, organization, year,  job_id=job_id, job_timeout=300)
		pjob = q.fetch_job(job_id)
		print(job_id)
		dbjob = TaskController.createTask(job_id, 'csv validation andimport', organization, year, 'started', s3Path)
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
		if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
			return make_response(('Size mismatch', 500))
		else:
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

	


