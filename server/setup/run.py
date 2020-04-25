#!3
import sys
sys.path.append('../')
import boto3

# from dynamodb.connectionManager         import ConnectionManager
# from dynamodb.userController            import UserController
# from dynamodb.candidateController       import CandidateController
# from dynamodb.organizationController    import OrganizationController
# from models.user                        import User
# from models.candidate                   import Candidate

# cm = ConnectionManager()
# UserController = UserController(cm)
# CandidateController = CandidateController(cm)
# OrganizationController = OrganizationController(cm)


# client = boto3.client('dynamodb', endpoint_url="http://localhost:8000")
# dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
# table = dynamodb.Table('candidates')


DB_URL='https://dynamodb.us-east-1.amazonaws.com'
ORGANIZATIONS_TABLE             = 'organizations'
USERS_TABLE                     = 'users'
CANDIDATES_TABLE                = 'candidates'
SURVEYS_TABLE                   = 'surveys'

client = boto3.client('dynamodb', region_name='us-east-1',  endpoint_url=DB_URL)

def diagnostics():
    print("WELCOME TO APPLICATION SETUP")
    return

def createUsersTable():
    # cm.createUsersTable()
    # while UserController.checkIfTableIsActive() == False:
    #     time.sleep(3)
    client.create_table(
                    AttributeDefinitions=[
                    {
                        'AttributeName': 'email',
                        'AttributeType': 'S',

                    },
                    {
                        'AttributeName': 'Organization',
                        'AttributeType': 'S'
                    }
                    ],
                    TableName="users",
                    KeySchema=[
                        {
                        'AttributeName':'email',
                        'KeyType': 'HASH'
                        },
                        {
                        'AttributeName': 'Organization',
                        'KeyType': 'RANGE'
                        }
                    ],
                    BillingMode='PROVISIONED',
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 1,
                        'WriteCapacityUnits': 1
                    }
                )
    print("USER TABLE CREATED")

    return

def createSurveyTable():
    # cm.createUsersTable()
    # while UserController.checkIfTableIsActive() == False:
    #     time.sleep(3)
    client.create_table(
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'uuid',
                            'AttributeType': 'S'
                        },
                        {
                            'AttributeName': 'Organization',
                            'AttributeType': 'S'
                        }
                    ],
                    TableName="surveys",
                    KeySchema=[
                        {
                            'AttributeName':'uuid',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'Organization',
                            'KeyType': 'RANGE'
                        }
                    ],
                   GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'survey-organization',
                        'KeySchema': [
                            {
                                'AttributeName': 'Organization',
                                'KeyType': 'HASH'
                            },
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL',
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 1,
                            'WriteCapacityUnits': 1
                        }
                    },
                ],
                BillingMode='PROVISIONED',
                ProvisionedThroughput={
                        'ReadCapacityUnits': 1,
                        'WriteCapacityUnits': 1
                }
            )
    print("SURVEY TABLE CREATED")
    

    return

def createCandidateTable():
    # cm.createCandidatesTable()
    # while CandidateController.checkIfTableIsActive() == False:
        # time.sleep(3)
    client.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'uuid',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'Organization',
                        'AttributeType': 'S'
                    }
                ],
                TableName="candidates",
                KeySchema=[
                    {
                    'AttributeName':'uuid',
                    'KeyType': 'HASH'
                    },
                    {
                    'AttributeName': 'Organization',
                    'KeyType': 'RANGE'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'candidate-organization',
                        'KeySchema': [
                            {
                                'AttributeName': 'Organization',
                                'KeyType': 'HASH'
                            },
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL',
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 1,
                            'WriteCapacityUnits': 1
                        }
                    },
                ],
                BillingMode='PROVISIONED',
                ProvisionedThroughput={
                        'ReadCapacityUnits': 1,
                        'WriteCapacityUnits': 1
                }
            )
    print("CANDIDATE TABLE CREATED")
    
    return

def createOrganizationsTable():
    client.create_table(
                        AttributeDefinitions=[
                        {
                            'AttributeName': 'name',
                            'AttributeType': 'S',

                        },
                        {
                            'AttributeName': 'admin',
                            'AttributeType': 'S'
                        }
                        ],
                        TableName="organizations",
                        KeySchema=[
                            {
                            'AttributeName':'name',
                            'KeyType': 'HASH'
                            },
                            {
                            'AttributeName': 'admin',
                            'KeyType': 'RANGE'
                            }
                        ],
                        BillingMode='PROVISIONED',
                        ProvisionedThroughput={
                            'ReadCapacityUnits': 1,
                            'WriteCapacityUnits': 1
                        }
                    )
    print("ORGANIZATIONS TABLE CREATED")
    return

diagnostics()
createUsersTable()
createCandidateTable()
createOrganizationsTable()
createSurveyTable()