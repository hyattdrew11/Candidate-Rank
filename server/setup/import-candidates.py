#!

from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
import uuid

dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
table = dynamodb.Table('candidates')

with open("eras-test.json") as json_file:
	candidates = json.load(json_file, parse_float = decimal.Decimal)
	for x in candidates:
		cid = uuid.uuid4()
		cid = str(cid)
		x['uuid'] = cid
		x['Organization'] 	= 'Tulane'
		x['Rank-Term'] 		= 2020
		x['interview'] 		= { 'status' : 'incomplete' }
		x['survey_1']  		= { 'status' : 'incomplete' }
		x['survery_2'] 		= { 'status' : 'incomplete' }
		table.put_item(Item=x)
