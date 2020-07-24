#! AUTHENTICATION API 
import random
import string
import uuid
import requests
import base64    
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


@mod.route('/zoom_authentication/', methods=('POST',))
def zoom_authentication():
    print("ZOOM AUTHENTICATION")
    # ADD DEBUG LOGIC AND VARIABLES
    data           = request.get_json()
    oauthCode      = data['code']
    redirect_uri   = "https://candidaterank.io/zoomredirect"
    # redirect_uri   = "http://localhost:8080/zoomredirect"
    
    auth_url       = "https://zoom.us/oauth/token?grant_type=authorization_code&code=" + oauthCode + "&redirect_uri=" + redirect_uri
    zoom64         = "k6uY18lSSjqNNenR0lspOg:cY3I8fEqXa6s17bVh4OkcRNjZN64hCIt"
    # zoom64         = "v0xZj387TZy5AfnUtjxSPQ:Umf8BbGjUp4OekAiRgmosXjcs5fBF95P"
    # Standard Base64 Encoding
    encodedBytes = base64.b64encode(zoom64.encode("utf-8"))
    encodedStr = str(encodedBytes, "utf-8")
    response = requests.post(auth_url, headers={'Authorization': 'Basic ' + encodedStr})
    if response.ok:
        body    =  json.loads(response.content)
        print("SENDING ACCESS TOKEN TO ZOOM")
        print(body['access_token'])
        at = body['access_token']
        me      = requests.get('https://api.zoom.us/v2/users/me', headers={'Authorization': 'Bearer ' + at })
        if me.ok:
            me =  json.loads(me.content) 
            print("ZOOM OAUTH SUCCESS")
            print(me)
            print('CHECK USER')
            user = controller.getUser(me['email'], 'password')
            if not user:
                return "Record not found", 500
            else:
                user['access_token']    =  body['access_token']
                user["token_type"]      =  body['token_type']
                user["refresh_token"]   =  body['refresh_token']
                user["expires_in"]      =  body['expires_in']
                user["scope"]           =  body['scope']
                updatedUser = controller.updateUser(user)
                if updatedUser:
                    print("RETURN SUCCESS TO CLIENT")
                    token       = {
                        'token': create_access_token(identity=data['email']),
                        'refresh_token': create_refresh_token(identity=data['email']),
                        'user' : updatedUser
                    }
                    return jsonify({ 'token': token })
                else: 
                    return "Record not found", 500
        else:
            me =  json.loads(me.content) 
            print(me)
            print("ZOOM EMAIL FAIL")
            return "Record not found", 500

    else:
        body    =  json.loads(response.content)
        print(body)
        print("ZOOM OAUTH FAIL")
        return "Record not found", 500

@mod.route('/login/', methods=('POST',))
def login():
    print("LOGIN")
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
        print("USER NOT FOUND")
        return "Record not found", 500
    elif not check_password_hash(user['password'], password):
        print("INCORRECT PASSWORD")
        error = 'Incorrect password.'
    if error is None:
        me      = requests.get('https://api.zoom.us/v2/users/me', headers={'Authorization': 'Bearer ' + user['access_token'] })
        if me.ok:
            print("CONNECTED TO ZOOM")
            print(me.content)
            return jsonify({ 'token': token })
        else: 
            print("REFRESH ZOOM TOKEN")
            print(user['refresh_token'])
            auth_url       = "https://zoom.us/oauth/token?grant_type=refresh_token&refresh_token=" +  user['refresh_token']
            # zoom64         = "k6uY18lSSjqNNenR0lspOg:cY3I8fEqXa6s17bVh4OkcRNjZN64hCIt"
            zoom64         = "v0xZj387TZy5AfnUtjxSPQ:Umf8BbGjUp4OekAiRgmosXjcs5fBF95P"
            # Standard Base64 Encoding
            encodedBytes = base64.b64encode(zoom64.encode("utf-8"))
            encodedStr = str(encodedBytes, "utf-8")
            response = requests.post(auth_url, headers={'Authorization': 'Basic ' + encodedStr})
            if response.ok:
                print("REFRESH TOKEN FOUND UPDATE USER")
                body    =  json.loads(response.content)
                print(body)
                user['access_token']    =  body['access_token']
                user["token_type"]      =  body['token_type']
                user["refresh_token"]   =  body['refresh_token']
                user["expires_in"]      =  body['expires_in']
                user["scope"]           =  body['scope']
                updatedUser             = controller.updateUser(user)
                print(updatedUser)
                if updatedUser:
                    return jsonify({ 'token': token })
            else:
                print(response.content)
                print("NO RESPONSE")
                return "Record not found", 500
    else:
        return "Record not found", 500

# @mod.route('/login/', methods=('POST',))
# def login():
#     print("LOGIN")
#     error       = None
#     data        = request.get_json()
#     print(data)
#     email       = data['email']
#     user        = controller.getUser(email)
#     print(user)

#     auth_url       = "https://zoom.us/oauth/token?grant_type=authorization_code&code=" + oauthCode + "&redirect_uri=" + redirect_uri
#     # zoom64         = "k6uY18lSSjqNNenR0lspOg:cY3I8fEqXa6s17bVh4OkcRNjZN64hCIt"
#     zoom64         = "v0xZj387TZy5AfnUtjxSPQ:Umf8BbGjUp4OekAiRgmosXjcs5fBF95P"
#     # Standard Base64 Encoding
#     encodedBytes = base64.b64encode(zoom64.encode("utf-8"))
#     encodedStr = str(encodedBytes, "utf-8")
#     response = requests.post(auth_url, headers={'Authorization': 'Basic ' + encodedStr})

#     token       = {
#         'token': create_access_token(identity=user['email']),
#         'refresh_token': create_refresh_token(identity=user['email']),
#         'user' : user
#     }
#     if not user:
#         return "Record not found", 500

#     if error is None:
#         return jsonify({ 'token': token })
#     else:
#         return "Record not found", 500


@mod.route('/register/', methods=('POST',))
def register():
    print("REGISTER")
    print("")
    data           = request.get_json()
    email          = data['email']
    password       = generate_password_hash(str(data['password']), method='sha256')
    organization   = data['organization']
    # 
    checkUser      = controller.getUser(email,password)
    checkOrg       = controller.getOrganization(organization)
    # 
    if checkUser or checkOrg:
        return "Record not found", 500
    else:
        org            = controller.createOrg(email, organization)
        if org:
            user = controller.createNewUser(email, password, org)
            if user:
                return jsonify(org), 201
            else:
                 return "Record not found", 500
        else:
            return "Record not found", 500

@mod.route('/user/add/<email>/<organization>', methods=('POST','GET'))
def addUser(email, organization):
    error = None
    tmpPass  = uuid.uuid4()
    print(tmpPass)
    password = generate_password_hash(str(tmpPass), method='sha256')
    user = controller.createNewUser(email, password, organization)
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