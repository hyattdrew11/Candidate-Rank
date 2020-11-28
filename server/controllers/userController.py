import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import decimal
from datetime   import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from flask import Flask, jsonify, json
# from server import config


DB_URL='https://dynamodb.us-east-1.amazonaws.com'
ORGANIZATIONS_TABLE             = 'organizations'
USERS_TABLE                     = 'users'
CANDIDATES_TABLE                = 'candidates'
SURVEYS_TABLE                   = 'surveys'

dynamodb = boto3.resource('dynamodb',region_name='us-east-1', endpoint_url=DB_URL)
client = boto3.client('dynamodb', region_name='us-east-1',  endpoint_url=DB_URL)

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

class UserController:

    def __init__(self):
        self.table_users = dynamodb.Table(USERS_TABLE)
        self.table_organizations = dynamodb.Table(ORGANIZATIONS_TABLE)

    def getOrganization(self, organization):
        org = {}
        try:
            response = self.table_organizations.query(KeyConditionExpression=Key('name').eq(organization))
        except Exception as e:
            print(e)
        else:
            for i in response['Items']:
                org = i
        return org

    def createOrg(self, email, organization):
        try:
            check = self.getOrganization(organization)
            if check:
                return False
            else:
                print("CREATE NEW ORG")
                now = str(datetime.now())
                org =  self.table_organizations.put_item(Item={
                    "name" : organization, 
                    "admin" : email, 
                    "terms":[] , 
                    "active": "true",
                    "date_created"  : now,
                    "date_modified" : now,
                })
                res = {
                    "name" : organization, 
                    "admin" : email, 
                    "terms":[] , 
                    "active": "true" ,
                    "date_created"  : now,
                    "date_modified" : now,
                }
                print("ADMIN CREATED")
                return res
        except Exception as error:
            print(error)
            return error

    def createNewUser(self, data):
        try:
            print(data)
            check = self.getUser(data['email'], ' ')
            if check:
                return False
            else:
                print("CREATE NEW USER")
                now = str(datetime.now())
                item =  self.table_users.put_item(
                            Item={
                                "date_created"  : now,
                                "date_modified" : now,
                                "email"         : data['email'],
                                "password"      : data['password'],
                                "role"          : data['role'],
                                "status"        : "Active",
                                "Organization"  : data['organization'],
                                "first_name"    : data['firstname'],
                                "last_name"     : data['lastname'],
                                "reset_link"    : data['reset_link'],
                            })
                return item
                
        except Exception as error:
            print(error)
            return False

    def getAll(self):
        users = []
        try:
            response = self.table_users.scan()
        except Exception as e:
            print(e)
        else:
            data = response['Items']
            while 'LastEvaluatedKey' in response:
                response =  self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                data.extend(response['Items'])

            for i in data:
                users.append(i)
                
        return users

    def updateUser(self, user):
        try:
            now = str(datetime.now())
            user["date_modified"] = now
            item  = self.table_users.put_item(Item=user)
            if item:
                return item
            else: 
                return False
        except Exception as e:
            return False


    def getUser(self, email, password):
        print("GET USER CONTROLLER:")
        user = {}
        fe = Key('email').eq(email)
        try:
            response = self.table_users.scan(FilterExpression=fe)
        except Exception as e:
            print(e)
        else:
            for i in response['Items']:
                user = i
        return user

    def getFaculty(self, organization):
        faculty = []
        fe = Key('Organization').eq(organization['name'])
        try:
            response = self.table_users.scan(FilterExpression=fe)
        except ItemNotFound as inf:
            return None
        except JSONResponseError as jre:
            return None
        for i in response['Items']:
            faculty.append(i)

        while 'LastEvaluatedKey' in response:
            response = self.table_users.scan(
                FilterExpression=fe,
                ExclusiveStartKey=response['LastEvaluatedKey']
                )
            for i in response['Items']:
                faculty.append(i)

        return faculty