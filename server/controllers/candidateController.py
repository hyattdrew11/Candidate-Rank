from __future__ import print_function # Python 2/3 compatibility
import logging
import time
import boto3
import json
import decimal
import uuid
from flask import Flask, Blueprint, jsonify, request, current_app, json
from datetime   import datetime
from boto3.dynamodb.conditions import Key, Attr
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConflictError


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
        print("CREATE NEW CANDIDATES")
        es = Elasticsearch([{'host': current_app.config['ES_CLUSTER'], 'port': current_app.config['ES_PORT'], 'use_ssl': True}])
        try:
            for x in candidates:
                print(x)
                cid = uuid.uuid4()
                cid = str(cid)
                now = str(datetime.now())
                x['uuid']           = cid
                x["date_created"]   = now
                x["date_modified"]  = now
                self.table.put_item(Item=x)
                es.index(index='candidates', doc_type='_doc', id=cid, body=x)
            return True
        except Exception as e:
            print(e)
            return False

    def updateCandidates(self, candidates):
        print("Updating Candidates")
        es = Elasticsearch([{'host': current_app.config['ES_CLUSTER'], 'port': current_app.config['ES_PORT'], 'use_ssl': True}])
        try:
            for x in candidates:
                now = str(datetime.now())
                x['date_modified'] = now
                self.table.put_item(Item=x)
                ui = es.update(index='candidates', id=x['uuid'], body={"doc": x })
            return True
            
        except Exception as e:
            print(e)
            return False

    def checkCandidate(self, email):
            try:
                print("CHECKING FOR CANDIDATE")
                QS = '(email:"'+email+'")'
                es = Elasticsearch([{'host': current_app.config['ES_CLUSTER'], 'port': current_app.config['ES_PORT'], 'use_ssl': True}])
                candidates = es.search(
                    index="candidates", 
                    body={ "query": {  "query_string": {  "query": QS } } },
                    size=1000
                )
                cArr = []
                if candidates['hits']['total']['value'] > 0:
                    hits = candidates['hits']['hits']
                    print(hits)
                    for x in hits:
                        cArr.append(x['_source'])

                    return cArr
                else:
                    return False
            except Exception as e:
                print(e)
                return None

    def updateCandidate(self, candidate):
        print("Updating Candidate GUY")
        es = Elasticsearch([{'host': current_app.config['ES_CLUSTER'], 'port': current_app.config['ES_PORT'], 'use_ssl': True}])
        try:
            check = self.getCandidate(candidate['Organization'], candidate['uuid'])
            if check:
                print("============== ES CANDIDATE FOUND ==============")
                print(check['email'])
                now = str(datetime.now())
                check['date_modified'] = now
                check['status'] = candidate['status']
                check['rank'] = candidate['rank']
                check['interview_score'] = candidate['interview_score']
                check['preinterview_score'] = candidate['preinterview_score']

                if "comments" in candidate:
                    check['comments'] = candidate['comments']
                else:
                    print("NO COMMENTS TO UPDATE")

                if "interview-date" in candidate:
                    check['interview-date'] = candidate['interview-date']
                else:
                    print("NO interview-date TO UPDATE")

                if "interview-surveys" in candidate:
                    check['interview-surveys'] = candidate['interview-surveys']
                else:
                    print("NO interview-date TO UPDATE")

                if "invited" in candidate:
                    print("invited in candidate")
                    check['invited'] = candidate['invited']
                else:
                    print("NO interview-date TO UPDATE")

                check['preinterview_score'] = candidate['preinterview_score']
                self.table.put_item(Item=check)
                time.sleep(1)
                es.indices.refresh(index = 'candidates')
                ui = es.update(index='candidates', id=check['uuid'], body={"doc": check })
                time.sleep(1)
                print("============== ES UPDATE CANDIDATE ==============")
                return True
            else: 
                print("CANDIDATE NOT FOUND")
                return False

        except ConflictError as e:
                print(e)
                # a conflict exception is raised more info here: https://discuss.elastic.co/t/python-script-update-by-query-elasticsearch-doesnt-work
                es.indices.refresh(index = 'candidates')
                # try again
                es.update(index='candidates', id=check['uuid'], body={"doc": check })

    def checkIfTableIsActive(self):
        description = self.cm.db.describe_table("candidates")
        status = description['Table']['TableStatus']

        return status == "ACTIVE"


    def getCandidates(self, organization, year):
        candidates = []
        fe = Key('Organization').eq(organization) & Key('Rank-Term').eq(year)
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

    def getCandidate(self, organization, uuid):
        try:
            response =  self.table.get_item(Key={'uuid': uuid, 'Organization' : organization })
            if "Item" in response:
                candidate = response['Item']
                return candidate
            else: 
                return None

        except Exception as e:
            print(e)
            return None


    def deleteCandidate(self, candidate):
        item =  self.table.delete_item(Key={'uuid': candidate['_source']['uuid'], 'Organization': candidate['_source']['Organization'] })
        if item:
            return candidate
        else: 
            return False
