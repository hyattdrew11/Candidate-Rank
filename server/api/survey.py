#! CANDIDATE API 
import uuid
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from flask import Flask, Blueprint, jsonify, request, current_app, json
from server.controllers.surveyController   import SurveyController
# from server.controllers.surveyController   import SurveyController
from flask_jwt_extended import (JWTManager, jwt_required)


# CandidateController = CandidateController()
SurveyController 	= SurveyController()

mod = Blueprint('survey', __name__)

@mod.route('/all/<organization>', methods=('GET',))
def allSurveys(organization):

	surveys = SurveyController.getSurveys(organization)

	if not surveys:
		return "Record not found", 500
	return jsonify(surveys), 201


@mod.route('/add', methods=('POST',))
def addSurvey():
	survey 	= request.get_json()
	item	= SurveyController.createSurvey(survey)
	if item:
		print(item)
		return jsonify(item), 201
	else:
		return "Record not found", 500

@mod.route('/update', methods=('POST',))
def updateSurvey():
	print("UpDATE SURVEY")
	survey 	= request.get_json()
	item	= SurveyController.updateSurvey(survey)
	if item:
		return jsonify(item), 201
	else:
		return "Record not found", 500

@mod.route('/delete', methods=('POST',))
def deleteSurvey():
	survey 	= request.get_json()
	item	= SurveyController.deleteSurvey(survey)
	if item:
		return jsonify(item), 201
	else:
		return "Record not found", 500