from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
import uuid
from datetime   import datetime
from boto3.dynamodb.conditions import Key, Attr

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

class CandidateController:
    """
    This UserController class basically acts as a singleton providing the necessary
    DynamoDB API calls.
    """
    def __init__(self):
        self.table = dynamodb.Table('candidates')

    def createNewCandidates(self, candidates):
        try:
            for x in candidates:
                cid = uuid.uuid4()
                cid = str(cid)
                now = str(datetime.now())
                x['uuid']           = cid
                x["date_created"]   = now
                x["date_modified"]  = now
                self.table.put_item(Item=x)
            return True
        except Exception as e:
            return False

    def checkIfTableIsActive(self):
        description = self.cm.db.describe_table("candidates")
        status = description['Table']['TableStatus']

        return status == "ACTIVE"


    def getCandidates(self, organization, year):
        candidates = []
        fe = Key('Organization').eq(organization) &  Key('Rank-Term').eq(year)
        try:
            response = self.table.scan(FilterExpression=fe)
        except ItemNotFound as inf:
            return None
        except JSONResponseError as jre:
            return None

        for i in response['Items']:
            candidates.append(i)

        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                FilterExpression=fe,
                ExclusiveStartKey=response['LastEvaluatedKey']
                )
            for i in response['Items']:
                candidates.append(i)


        return candidates

    def getCandidate(self, email, password):
        """
        Basic get_item call on the users Table, where we specify the primary key
        email to be the parameter email.
        Returns None on an ItemNotFound Exception.
        """
        try:
            item = self.cm.getCandidatesTable().get_item(email=email)
        except ItemNotFound as inf:
            return None
        except JSONResponseError as jre:
            return None

        return item
