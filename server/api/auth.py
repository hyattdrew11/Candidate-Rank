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
from server.controllers.emailController import EmailController
from server.controllers.organizationController  import OrganizationController
from server.controllers.candidateController     import CandidateController
from server.models.user import User
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)

import http.client
import jwt
import requests
import secrets
import json
from time import time


controller = UserController()
emailController = EmailController()
OrganizationController  = OrganizationController()
CandidateController     = CandidateController()

mod = Blueprint('auth', __name__)

zoom_client = 'SekFiZ4yTliCtLOT1BjwOQ'
zoom_secret = 'BP5IOQtWwkmyPQAHQjIpH0sQSOFdiw1xHinP'

@mod.route('/zoom_authentication/', methods=('POST',))
def zoom_authentication():
    print("ZOOM AUTHENTICATION")
    # ADD DEBUG LOGIC AND VARIABLES
    data           = request.get_json()
    print(data)
    oauthCode      = data['code']
    redirect_uri   = "https://candidaterank.io/zoomredirect"
    auth_url       = "https://zoom.us/oauth/token?grant_type=authorization_code&code=" + oauthCode + "&redirect_uri=" + redirect_uri
    zoom64         = zoom_client+":"+zoom_secret
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
            print('CHECK USER')
            user = controller.getUser(data['email'], 'password')
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

# @mod.route('/refresh_zoom/', methods=('POST',))
# def refreshZoom():
#     userIDS = []
#     conn = http.client.HTTPSConnection("api.zoom.us")

#     headers = {'authorization': 'Bearer %s' % generateToken(),
#                'content-type': 'application/json'}

#     r = requests.get('https://api.zoom.us/v2/users/', headers=headers)
#     res = r.json()
#     for u in res['users']:
#         userIDS.append(u['id'])
#         user = requests.get('https://api.zoom.us/v2/users/' + u['id'], headers=headers)
#         if user.ok:
#             print(user.text)
#         else:
#             print("ERROR GETTING USER: " + u['email'])

#     return jsonify({ 'users': userIDS })

# @mod.route('/refresh_zoom/', methods=('POST',))
# def refreshZoom():
#     print("REFRESH ZOOM TOKEN")
#     error       = None
#     data        = request.get_json()
#     email       = data['email']
#     user        = controller.getUser(email,"password")
#     token       = {
#             'token': create_access_token(identity=data['email']),
#             'refresh_token': create_refresh_token(identity=data['email']),
#             'user' : user
#         }
#     if not user:
#         print("USER NOT FOUND")
#         return "Record not found", 500
#     else:
#         me      = requests.get('https://api.zoom.us/v2/users/me', headers={'Authorization': 'Bearer ' + user['access_token'] })
#         if me.ok:
#             print("CONNECTED TO ZOOM")
#             return jsonify({ 'token': token })
#         else: 
#             print("REFRESH ZOOM TOKEN")
#             auth_url       = "https://zoom.us/oauth/token?grant_type=refresh_token&refresh_token=" +  user['refresh_token']
#             zoom64         = zoom_client+":"+zoom_secret
#             # Standard Base64 Encoding
#             encodedBytes = base64.b64encode(zoom64.encode("utf-8"))
#             encodedStr = str(encodedBytes, "utf-8")
#             response = requests.post(auth_url, headers={'Authorization': 'Basic ' + encodedStr})
#             if response.ok:
#                 print("REFRESH TOKEN FOUND UPDATE USER")
#                 body                    =  json.loads(response.content)
#                 user['access_token']    =  body['access_token']
#                 user["token_type"]      =  body['token_type']
#                 user["refresh_token"]   =  body['refresh_token']
#                 user["expires_in"]      =  body['expires_in']
#                 user["scope"]           =  body['scope']
#                 updatedUser             =  controller.updateUser(user)
#                 if updatedUser:
#                     return jsonify({ 'token': token })
#             else:
#                 print("ZOOM RESPONSE NOT OK")
#                 print(response.content)
#                 return jsonify({ 'error': 'auth-zoom', 'token' : token })

@mod.route('/password_update/', methods=('POST',))
def passwordUpdate():
    print("PASSWORD UPDATE")
    data = request.get_json()
    user = controller.getUser(data['email'],"password")
    print(data['reset_link'])
    print(user['reset_link'])
    if not user:
        print("USER NOT FOUND")
        return "Record not found", 500
    else: 
        if data['reset_link'] == user['reset_link']:
            password = generate_password_hash(str(data['password']), method='sha256')
            user['password'] = password
            updatedUser = controller.updateUser(user)
            if updatedUser:
                return jsonify({ 'user': user })
            else:
                print("INCORRECT GUID")
                return "Record not found", 500
        else:
            return "Record not found", 500

@mod.route('/password_reset/', methods=('POST',))
def passwordReset():
    linkID  = str(uuid.uuid4())
    print(linkID)
    data = request.get_json()
    print(data)
    user = controller.getUser(data['email'],"password")
    if not data['recaptchaToken']:
        print("USER NOT FOUND")
        return "Record not found", 500
    else:
        recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
        recaptcha_secret_key = '6Ld4AdoZAAAAAHfWq4u0kdxf8wWtYJT-yI_EfE4h'
        payload = {
           'secret': recaptcha_secret_key,
           'response': data['recaptchaToken'],
           'remoteip': request.remote_addr,
        }
        capRes = requests.post(recaptcha_url, data = payload)
        if capRes.ok:
            if not user:
                print("USER NOT FOUND")
                return "Record not found", 500
            else: 
                user['reset_link'] = linkID
                print(user)
                updatedUser = controller.updateUser(user)
                if updatedUser:
                    print(updatedUser)
                    link = "https://candidaterank.io/update/password/" + data['email'] + "/" + user['reset_link']
                    sendEmail = emailController.passwordReset(data['email'], link)
                    if sendEmail:
                        return jsonify({ 'user': user })
                    else:
                        return "Record not found", 500
                else:
                    print("UPDATED USER NOT FOUND")
                    return "Record not found", 500
        else:
            return "Record not found", 500

@mod.route('/applicant/getorgs', methods=('POST',))
def getOrgs():
    data = request.get_json()
    seen = set()
    candidateOrgs = []
    orgs = []
    # for x in a:
    #     if x not in seen:
    #         candidateOrgs = [].append(x)
    #         seen.add(x)
    # Send your sms message.
    try:
        # CHECK CANDIDATE EMAIL IN ELASTICSEARCH
        candidates = CandidateController.checkCandidate(data['email'])
        if candidates:
            for x in candidates:
                candidateOrgs.append(x['Organization'])

            seen = set()
            uniq = [x for x in candidateOrgs if x not in seen and not seen.add(x)]  
            print(uniq)

            for x in uniq:
                ORG = OrganizationController.getOrganization(x)
                orgs.append(ORG)

            if orgs:
                return jsonify({ 'orgs': orgs , 'candidates' : candidates })
            else:
                return "Record not found", 500
        else:
            return "Record not found", 500

    except Exception as e:
        print(e)



@mod.route('/login/as', methods=('POST',))
def loginAS():
    print("LOGIN AS")
    error       = None
    data        = request.get_json()
    email       = data['email']
    password    = data['password']
    user        = controller.getUser(email,password)
    print(user)
    token       = {
            'token': create_access_token(identity=data['email']),
            'refresh_token': create_refresh_token(identity=data['email']),
            'user' : user
        }
        
    if user:
        return jsonify({ 'token': token })

    else:
        return "Record not found", 500

@mod.route('/login/', methods=('POST',))
def login():
    print("LOGIN")
    error       = None
    data        = request.get_json()
    email       = data['email']
    password    = data['password']
    user        = controller.getUser(email,password)
    print(user)
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
        return "Record not found", 500
    if error is None:
        return jsonify({ 'token': token })
    else:
        return "Record not found", 500


@mod.route('/register/', methods=('POST',))
def register():
    data           = request.get_json()
    firstname      = data["firstname"]
    lastname       = data["lastname"]
    email          = data['email']
    password       = generate_password_hash(str(data['password']), method='sha256')
    organization   = data['organization']
    checkUser      = controller.getUser(email,password)
    checkOrg       = controller.getOrganization(organization)
    linkID  = str(uuid.uuid4())
    link = "https://candidaterank.io/update/password/" + email + "/" + linkID
    if checkUser or checkOrg:
        print(checkUser)
        print(checkOrg)
        print("RECORD NOT FOUND")
        return "Record not found", 500
    else:
        print("CREATE ORG & USER")
        org = controller.createOrg(email, organization)
        if org:
            userInput = {
                "email" : email,
                "firstname" : firstname,
                "lastname"  : lastname,
                "password"  : password,
                "organization" : organization,
                "role"  : "Admin",
                "reset_link"    : link,
            }
            user = controller.createNewUser(userInput)
            if user:
                token = {
                    'token': create_access_token(identity=data['email']),
                    'refresh_token': create_refresh_token(identity=data['email']),
                    'user' : ""
                }
                return jsonify({ 'token': token }), 201
            else:
                 return "Record not found", 500
        else:
            return "Record not found", 500

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str

@mod.route('/user/add', methods=('POST',))
def addUser():
    data    = request.get_json()
    # TRY ZOOOM ADD USER TO ACCOUNT NEED AUTH AND REFRESH
    newUser = data['newUser']
    admin   = data['admin']
    tmpPass = get_random_string(8)
    print(tmpPass)
    linkID  = str(uuid.uuid4())
    newUser['password'] = generate_password_hash(tmpPass , method='sha256')
    newUser['reset_link'] = linkID
    user = controller.createNewUser(newUser)
    link = "https://candidaterank.io/update/password/" + newUser['email'] + "/" + linkID
    if not user:
        return "Record not found", 500
    else:
        sendEmail = emailController.evaluatorInvite(newUser['email'], link, tmpPass)
    if sendEmail:
        return jsonify({ 'user': newUser })
    else:
        return "Record not found", 500
    # body = {
    #       "action": "create",
    #       "user_info": {
    #         "email": newUser['email'],
    #         "type": 1,
    #         "first_name": newUser['firstname'],
    #         "last_name":  newUser['lastname']
    #       }
    #     }
    # zAPI = refreshZoomApi(admin)
    # if zAPI:
    #     print("zAPI")
    #     zoomUser = requests.post('https://api.zoom.us/v2/users', json=body, headers={'Authorization': 'Bearer ' + zAPI })
    #     print(zoomUser.status_code)
    #     if zoomUser.ok or zoomUser.status_code == 409:
    #         print("ZOOM USER")
    #         print(zoomUser.content)
    #         error   = None
    #         tmpPass = uuid.uuid4()
    #         linkID  = str(uuid.uuid4())
    #         newUser['password'] = generate_password_hash(str(tmpPass), method='sha256')
    #         newUser['reset_link'] = linkID
    #         user = controller.createNewUser(newUser)
    #         link = "https://candidaterank.io/update/password/" + newUser['email'] + "/" + linkID
    #         if not user:
    #             return "Record not found", 500

    #         if error is None:
    #             sendEmail = emailController.evaluatorInvite(newUser['email'], link)
    #             if sendEmail:
    #                 return jsonify({ 'user': newUser })
    #             else:
    #                 return "Record not found", 500
    #     else:
    #         print("ZOOM CREATE USER FAIL")
    #         print(zoomUser.content)
    #         errMsg = zoomUser.json()
    #         if errMsg['code'] == 1009:
    #             resStr = newUser['email'] + " already holds an active Zoom account."
    #             return jsonify({ 'error': resStr })
    # else:
    #     return "Record not found", 500

def refreshZoomApi(data):
    print("REFRESH ZOOM TOKEN")
    error       = None
    email       = data['email']
    user        = controller.getUser(email,"password")
    token       = {
            'token': create_access_token(identity=data['email']),
            'refresh_token': create_refresh_token(identity=data['email']),
            'user' : user
        }
    if not user:
        print("USER NOT FOUND")
        return "Record not found", 500
    else:
        me      = requests.get('https://api.zoom.us/v2/users/me', headers={'Authorization': 'Bearer ' + user['access_token'] })
        if me.ok:
            print("CONNECTED TO ZOOM")
            print(me.content)
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
                print(response.content)
                body                    =  json.loads(response.content)
                user['access_token']    =  body['access_token']
                user["token_type"]      =  body['token_type']
                user["refresh_token"]   =  body['refresh_token']
                user["expires_in"]      =  body['expires_in']
                user["scope"]           =  body['scope']
                updatedUser             = controller.updateUser(user)
                if updatedUser:
                    return body['access_token']
            else:
                print("ZOOM RESPONSE NOT OK")
                return False