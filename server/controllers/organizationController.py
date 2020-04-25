import time
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import uuid
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

class OrganizationController:

    def __init__(self):
        self.table = dynamodb.Table(ORGANIZATIONS_TABLE)

    def updateOrganization(self, organization):
        now = str(datetime.now())
        org = organization
        org["date_modified"] = now
        item =  client.update_item(
                    TableName=ORGANIZATIONS_TABLE,
                    Key={'name': org.name },
                    AttributeUpdates=s,
                )
        if item:
            return s
        else: 
            s = {}
            return False

    def updateTerms(self, organization):
        try:
            now = str(datetime.now())
            organization['date_modified'] = now
            self.table.put_item(Item=organization)
            return organization
            
        except Exception as e:
            return False

    def getOrganization(self, organization):
        org = {}
        try:
            response = self.table.query(KeyConditionExpression=Key('name').eq(organization))
        except Exception as e:
            print(e)
        else:
            for i in response['Items']:
                org = i
        return org