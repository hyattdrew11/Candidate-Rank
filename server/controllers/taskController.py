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
TASKS_TABLE                     = 'tasks'

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

class TaskController:

    def __init__(self):
        self.table_users = dynamodb.Table(USERS_TABLE)
        self.table_organizations = dynamodb.Table(ORGANIZATIONS_TABLE)
        self.table_tasks = dynamodb.Table(TASKS_TABLE)

    def createTask(self, uuid, action, organization, term, progress, s3key):
        try:
            print("CREATE NEW TASK")
            now = str(datetime.now())
            item =  self.table_tasks.put_item(
                            Item={
                                "uuid"  : uuid,
                                "action" : action,
                                "start_time"      : now,
                                "Organization" : organization,
                                "term" : term,
                                "progress" : "0",
                                "s3key" : s3key
                            })

            print("TASK CREATED")
            return item
        except Exception as error:
            print(error)
            return error

    def getTasks(self, organization):
        tasks = []
        fe = Key('Organization').eq(organization)
        try:
            response = self.table_tasks.scan(FilterExpression=fe)
        except ItemNotFound as inf:
            return None
        except JSONResponseError as jre:
            return None

        for i in response['Items']:
            tasks.append(i)

        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                FilterExpression=fe,
                ExclusiveStartKey=response['LastEvaluatedKey']
                )
            for i in response['Items']:
                tasks.append(i)

        return tasks