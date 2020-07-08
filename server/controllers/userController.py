import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import decimal
from datetime   import datetime
from werkzeug.security import generate_password_hash, check_password_hash
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

    def createAdmin(self, password, email, organization, cc, ccexp, cvv):
        try:
            print("CREATE NEW ADMIN")
            print( password, email, organization, cc, ccexp, cvv)
            org =  self.table_organizations.put_item(Item={"name" : organization, "admin" : email, "terms":[] })
            now = str(datetime.now())
            item =  self.table_users.put_item(
                            Item={
                                "date_created"  : now,
                                "date_modified" : now,
                                "password"      : password,
                                "email"         : email,
                                "role"          : "Admin",
                                "status"        : "Active",
                                "Organization"  : organization,
                                "first_name"    : "  ",
                                "last_name"     : "  ",
                                "cc"            : cc,
                                "ccexp"         : ccexp,
                                "cvv"           : cvv 
                            })

            print("ADMIN CREATED")
            print(item)
            return item
            # print(json.dumps(response, indent=4, cls=DecimalEncoder))
        except Exception as error:
            print(error)
            return error

    def createNewUser(self, password, email, organization):
        try:
            print("CREATE NEW USER")
            userCheck = self.getUser(email, password)
            if userCheck:
                return False
            else: 
                now = str(datetime.now())
                item =  self.table_users.put_item(
                            Item={
                                "date_created"  : now,
                                "date_modified" : now,
                                "password"      : password,
                                "email"         : email,
                                "role"          : "faculty",
                                "status"        : "inactive",
                                "Organization"  : organization,
                                "first_name"    : "  ",
                                "last_name"     : "  ",
                            })
                print(item)
                return item
                
        except Exception as error:
            print(error)
            return False

    def getUser(self, email, password):
        print("GET USER CONTROLLER")
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