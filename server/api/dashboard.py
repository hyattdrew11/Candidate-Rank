#! CANDIDATE API 
import uuid
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from flask import Flask, Blueprint, jsonify, request, current_app, json
from server.controllers.organizationController import OrganizationController
from server.controllers.userController   	import UserController
from server.controllers.surveyController   	import SurveyController
from server.controllers.candidateController import CandidateController
from flask_jwt_extended import (JWTManager, jwt_required)

OrganizationController 	= OrganizationController()
UserController 			= UserController()
SurveyController 		= SurveyController()
CandidateController 	= CandidateController()

mod = Blueprint('dashboard', __name__)

@mod.route('/admin/<organization>/<year>', methods=('GET',))
def admin(organization, year):
	organization = OrganizationController.getOrganization(organization)
	# GET ALL ORGINIZATION CANDIDATES AS AN ARRAY OF JSON OBJECTS
	candidates 	= CandidateController.getCandidates( organization, int(year) )
	# GET ALL ORGINIZATION FACULTY AS AN ARRAY OF JSON OBJECTS
	faculty    = UserController.getFaculty(organization)
	# GET ALL ORGINIZATION SURVEYS AS AN ARRAY OF JSON OBJECTS
	surveys    = SurveyController.getSurveys(organization)
	print(surveys)
	# BUILD SUCCESSFUL JSON RESPONSE
	response = {
		"success"		: True,
		"error"   		: False,
		"errMsg"  		: '',
		"organization"	: organization,
		"candidates"	: candidates,
		"faculty" 		: faculty,
		"surveys" 		: surveys
	}
	return jsonify(response)

@mod.route('/faculty/<organization>/<year>', methods=('GET',))
def faculty(organization, year):
	# GET THE ORGANIZATION
	organization = OrganizationController.getOrganization(organization)
	# GET ALL ORGINIZATION CANDIDATES AS AN ARRAY OF JSON OBJECTS
	candidates = CandidateController.getCandidates(organization, int(year) )
	
	response = {
		"success"		: True,
		"error"   		: False,
		"organization"	: organization,
	}

	return jsonify(response)

	


