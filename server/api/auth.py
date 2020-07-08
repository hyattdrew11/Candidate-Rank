#! AUTHENTICATION API 
import random
import string
import uuid
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, Blueprint, jsonify, request, current_app, json
from flask_mail import Mail
from server.controllers.userController import UserController
from server.models.user import User
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)

controller = UserController()
mod = Blueprint('auth', __name__)

@mod.route('/register/', methods=('POST',))
def register():
    data           = request.get_json()
    password       = generate_password_hash(data['password'], method='sha256')
    email          = data['email']
    organization   = data['organization']
    cc             = generate_password_hash(data['cc'], method='sha256')
    ccexp          = data['ccexp']
    cvv            = data['cvv']
    item           = controller.createAdmin(password, email, organization, cc, ccexp, cvv)
    if item:
        return jsonify(item), 201
    else:
        return "Record not found", 500


@mod.route('/login/', methods=('POST',))
def login():
    error       = None
    data        = request.get_json()
    email       = data['email']
    password    = data['password']
    user        = controller.getUser(email,password)
    token       = {
        'token': create_access_token(identity=data['email']),
        'refresh_token': create_refresh_token(identity=data['email']),
        'user' : user
    }
    if not user:
        return "Record not found", 500
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect password.'
    if error is None:
        return jsonify({ 'token': token })
    else:
        return "Record not found", 500


@mod.route('/user/add/<email>/<organization>', methods=('POST','GET'))
def addUser(email, organization):
    error = None
    tmpPass  = uuid.uuid4()
    print(tmpPass)
    password = generate_password_hash(str(tmpPass), method='sha256')
    user = controller.createNewUser(password, email, organization)
    sender = current_app.config['MAIL_USERNAME']
    if not user:
        return "Record not found", 500

    if error is None:
        mail = Mail(current_app)
        msg = mail.send_message(
            'Candidate Rank',
            sender=sender,
            recipients=['drew@thearchengine.com'],
            body="You have been invited to Candidate Rank by " + organization + ". Please go to www.candidaterank.io/login to set your password and login."
        )
        return jsonify({ 'user': email })

    else:
        return "Record not found", 500
    # 

    # data           = request.get_json()
    # password       = generate_password_hash(data['password'], method='sha256')
    # email          = data['email']
    # organization   = data['organization']
    # cc             = generate_password_hash(data['cc'], method='sha256')
    # ccexp          = data['ccexp']
    # cvv            = data['cvv']
    # item           = controller.createAdmin(password, email, organization, cc, ccexp, cvv)
    # if item:
    #     return jsonify(item), 201
    # else:
    #     return "Record not found", 500