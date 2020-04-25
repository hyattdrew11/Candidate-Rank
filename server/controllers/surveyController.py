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

class SurveyController:

    def __init__(self):
        self.table = dynamodb.Table(SURVEYS_TABLE)

    def createSurvey(self, survey):
        now = str(datetime.now())
        sid = uuid.uuid4()
        sid = str(sid)
        s = {
            "uuid"          : sid,
            "date_created"  : now,
            "date_modified" : now,
            "Organization"  : survey['Organization'],
            "term"          : survey['term'],
            "type"          : survey['type'],
            "name"          : survey['name'],
            "questions"     : survey['questions']
        }
        item =  self.table.put_item(
                        Item=s)
        if item:
            return s
        else: 
            s = {}
            return False

    def updateSurvey(self, survey):
        now = str(datetime.now())
        s = {
            "date_modified" : now,
            "Organization"  : survey['Organization'],
            "term"          : survey['term'],
            "type"          : survey['type'],
            "name"          : survey['name'],
            "questions"     : survey['questions']
        }
        item =  client.update_item(
                    TableName=SURVEYS_TABLE,
                    Key={'uuid': survey.uuid },
                    AttributeUpdates=s,
                )
        if item:
            return s
        else: 
            s = {}
            return False

    def getSurveys(self, organization):
        surveys = []
        fe = Key('Organization').eq(organization['name'])
        try:
            response = self.table.scan(FilterExpression=fe)
        except ItemNotFound as inf:
            return None
        except JSONResponseError as jre:
            return None

        for i in response['Items']:
            surveys.append(i)

        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                FilterExpression=fe,
                ExclusiveStartKey=response['LastEvaluatedKey']
                )
            for i in response['Items']:
                surveys.append(i)

        return surveys