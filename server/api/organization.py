#! USER API 
import uuid
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, Blueprint, jsonify, request, current_app, json
from server.controllers.organizationController import OrganizationController

OrganizationController = OrganizationController()

mod = Blueprint('organization', __name__)

@mod.route('/test', methods=['GET'])
def test():
        return "Success organization"

@mod.route('/update', methods=('POST',))
def updateOrganization():
	survey 	= request.get_json()
	item	= OrganizationController.updateOrganization(organization)
	if item:
		print(item)
		return jsonify(item), 201
	else:
		return "Record not found", 500



@mod.route('/update/terms/<organization>', methods=('POST',))
def updateTerms(organization):
	data 	= request.get_json()
	item	= OrganizationController.updateTerms(data)
	if item:
		return jsonify(item), 201
	else:
		return "Record not found", 500

# API ENDPOINT FOR FILE UPLOADS - ONLY ADMIN WILL HAVE UPLOAD CAPABILITES ALLOW ON .PNG TO START
@mod.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return render_template('index.html')