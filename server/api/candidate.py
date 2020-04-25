#! CANDIDATE API 
import uuid
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from flask import Flask, Blueprint, jsonify, request, current_app, json
from server.controllers.candidateController   import CandidateController
from server.models.candidate               import Candidate
from flask_jwt_extended import (JWTManager, jwt_required)


controller = CandidateController()

mod = Blueprint('candidate', __name__)

# ADD A CANDIDATE TO AN ORGANIZATION
@mod.route('/add/<organization>', methods=['POST'])
def create(organization):
	# DYNAMO CREATES CANDIDATE FROM POST DATA
	data = request.get_json()
	print(data)
	candidates = controller.createNewCandidates(data)
	if candidates:
		print("Added Candidates")
		return jsonify(data), 201
	else:
		return 500

# update

# delete

# get
@mod.route('/all/<organization>/<year>', methods=('GET',))
def allCandidates(organization, year):

	candidates = controller.getCandidates( organization, int(year) )

	if not candidates:
		x = {}
		return jsonify(x), 201
	return jsonify(candidates)

# search