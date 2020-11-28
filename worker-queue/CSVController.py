from __future__ import print_function 
import boto3
import time
import json
import decimal
import uuid
import csv
from datetime   import datetime
from boto3.dynamodb.conditions import Key, Attr
import Levenshtein
from elasticsearch import Elasticsearch
import xmltodict
from json import loads, dumps

DB_URL ='https://dynamodb.us-east-1.amazonaws.com'
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

class CSVController:

	def __init__(self):
		self.table = dynamodb.Table('candidates')
		self.esHost = 'search-crprodcluster-gzhpfjadnrk7352eg5asofwcfm.us-east-1.es.amazonaws.com'
		self.esPort = '443'
		self.erasFieldsOne = [
			"AAMC ID",
			"Last Name",
			"First Name",
			"Middle Name",
			"Couples - Partner Name",
			"Couples - Partner Specialty",
			"Participating as a Couple in NRMP",
			"Medical Degree",
			"USMLE Step 1 Score",
			"USMLE Step 2 CK Score",
			"Medical School of Graduation",
			"Medical School State/Province",
			"Medical School Type",
			"Awards & Recognitions - Medical School",
			"Awards & Recognitions - Others",
			"Explanation of why Medical Education or Training Interrupted",
			"Higher Education Attendance Dates",
			"Higher Education Degree",
			"Higher Education Degree Date Earned",
			"Higher Education Degree Earned",
			"Higher Education Institution",
			"Higher Education Location",
			"Higher Education Major",
			"Medical Degree Expected or Earned",
			"Medical Education or Training Interrupted",
			"Medical School Attendance Dates",
			"Medical School Clinical Campus",
			"Medical School Country",
			"Medical School Degree Date of Graduation",
			"Membership in Honorary or Professional Societies",
			"Medical Degree_1",
			"Medical School of Graduation_1",
			"Medical School State/Province_1",
			"Medical School Type_1",
			"Higher Education Attendance Dates_1",
			"Higher Education Degree_1",
			"Higher Education Degree Date Earned_1",
			"Higher Education Degree Earned_1",
			"Higher Education Institution_1",
			"Higher Education Location_1",
			"Higher Education Major_1",
			"Medical Degree Expected or Earned_1",
			"Medical School Attendance Dates_1",
			"Medical School Clinical Campus_1",
			"Medical School Country_1",
			"Medical School Degree Date of Graduation_1",
			"Higher Education Attendance Dates_2",
			"Higher Education Degree_2",
			"Higher Education Degree Date Earned_2",
			"Higher Education Degree Earned_2",
			"Higher Education Institution_2",
			"Higher Education Location_2",
			"Higher Education Major_2",
			"Higher Education Attendance Dates_3",
			"Higher Education Degree_3",
			"Higher Education Degree Date Earned_3",
			"Higher Education Degree Earned_3",
			"Higher Education Institution_3",
			"Higher Education Location_3",
			"Higher Education Major_3",
			"Higher Education Attendance Dates_4",
			"Higher Education Degree_4",
			"Higher Education Degree Date Earned_4",
			"Higher Education Degree Earned_4",
			"Higher Education Institution_4",
			"Higher Education Location_4",
			"Higher Education Major_4",
			"Higher Education Attendance Dates_5",
			"Higher Education Degree_5",
			"Higher Education Degree Date Earned_5",
			"Higher Education Degree Earned_5",
			"Higher Education Institution_5",
			"Higher Education Location_5",
			"Higher Education Major_5"
		]

		self.erasFieldsTwo = [
			"AAMC ID",
			"Complete Application Date",
			"Medical Education or Training Interrupted",
			"Explanation of why Medical Education or Training Interrupted",
			"Medical School Degree Date of Graduation",
			"Tracks Applied by Applicant",
			"Date of Birth",
			"Participating as a Couple in NRMP",
			"Couples - Partner Name",
			"Couples - Partner Specialty",
			"Citizenship",
			"Limiting Factors",
			"Limitations Description",
			"Contact Address 1",
			"Contact Address 2",
			"Contact City",
			"Contact State",
			"Contact Zip",
			"E-mail",
			"Preferred Phone",
			"Hobbies and Interests",
			"First Name",
			"Last Name",
			"Medical School of Graduation",
			"Alpha Omega Alpha (Yes/No)",
			"USMLE Step 1 Score",
			"USMLE Step 2 CK Score",
			"Total Interview Score",
			"Medical School Degree Date of Graduation_1",
			"Tracks Applied by Applicant_1",
			"Medical School of Graduation_1"
		]

		self.erasFieldsThree = [
			 "AAMC ID",
			 "Applicant Name",
			 "E-mail",
			 "Cell Phone #",
			 "Most Recent Medical School",
			 "Most Recent Application Status",
			 "Most Recent Application Status Date",
			 "Tracks Considered by Program",
			 "Tracks Applied by Applicant",
			 "USMLE Step 1 Score",
			 "USMLE Step 2 CK Score",
			 "USMLE Step 2 CS Score",
			 "COMLEX-USA Level 1 Score",
			 "COMLEX-USA Level 2 CE Score",
			 "COMLEX-USA Level 2 PE Score"
		]
		self.erasFieldsFour = [
			"AAMC ID",
			"Cell Phone #",
			"Applicant Name",
			"COMLEX-USA Level 1 Score",
			"COMLEX-USA Level 2 CE Score",
			"COMLEX-USA Level 2 PE Score",
			"COMLEX-USA Level 3 Score",
			"USMLE Step 1 Score",
			"USMLE Step 2 CK Score",
			"USMLE Step 2 CS Score",
			"USMLE Step 3 Score",
			"E-mail",
			"Selected to Interview",
			"First Name",
			"Last Name",
			"Middle Name",
			"Most Recent Application Status",
			"Most Recent Application Status Date",
			"Most Recent Medical School",
			"Tracks Considered by Program",
			"Tracks Applied by Applicant",
			"Preferred Phone",
			"Tracks Considered by Program_1",
			"Tracks Applied by Applicant_1"
		]
		self.erasFieldsFive = [
			"AAMC ID",
			"Applicant Name",
			"E-mail",
			"Cell Phone #",
			"Most Recent Medical School",
			"Most Recent Application Status",
			"Most Recent Application Status Date",
			"Tracks Considered by Program",
			"Tracks Applied by Applicant",
			"USMLE Step 1 Score",
			"USMLE Step 2 CK Score",
			"USMLE Step 2 CS Score",
			"USMLE Step 3 Score",
			"Most Recent Medical Training Program"
		]
		self.erasFieldsSix = [
			"AAMC ID",
			"Cell Phone #",
			"Applicant Name",
			"COMLEX-USA Level 1 Score",
			"COMLEX-USA Level 2 CE Score",
			"COMLEX-USA Level 2 PE Score",
			"COMLEX-USA Level 3 Score",
			"USMLE Step 1 Score",
			"USMLE Step 2 CK Score",
			"USMLE Step 2 CS Score",
			"USMLE Step 3 Score",
			"E-mail",
			"Selected to Interview",
			"First Name",
			"Last Name",
			"Middle Name",
			"Most Recent Application Status",
			"Most Recent Application Status Date",
			"Most Recent Medical School",
			"Tracks Considered by Program",
			"Tracks Applied by Applicant",
			"Preferred Phone",
			"Tracks Considered by Program_1",
			"Tracks Applied by Applicant_1"
		]
		self.erasFieldsSeven = [
			"AAMC ID",
			"Applicant Name",
			"Cell Phone #",
			"E-mail",
			"Most Recent Application Status",
			"Most Recent Application Status Date",
			"USMLE Step 1 Score",
			"USMLE Step 2 CK Score",
			"USMLE Step 2 CS Score",
			"Medical Degree Expected or Earned",
			"Medical School of Graduation",
			"Medical Degree Expected or Earned_1",
			"Medical School of Graduation_1",
			"Medical Degree Expected or Earned_2",
			"Medical School of Graduation_2"
		]
		self.erasFieldsEight = [
			"AAMC ID",
			"Applicant Name",
			"E-mail",
			"Cell Phone #",
			"USMLE ID",
			"Medical School of Graduation",
			"Medical School of Graduation_1"
		]
		self.erasFieldsNine = [
			"AAMC ID",
			"Applicant Name",
			"E-mail",
			"USMLE Step 1 Score",
			"USMLE Step 2 CK Score",
			"Medical School of Graduation"
		]
		self.erasFieldsTen = [
			"AAMC ID",
			"Applicant Name",
			"E-mail",
			"Most Recent Medical School",
			"Tracks Applied by Applicant",
			"Tracks Applied by Applicant_1",
			"Preferred Phone",
			"Event Start Date"
		]
		self.sfFields = [
			"ApplicantId",
			"LastName",
			"FirstName",
			"Email",
			"AddToInterviewList",
			"MedSchool",
			"YearOfGraduation",
			"AAMC ID",
			"CurrentResidency",
			"YearOfResCompletion",
			"StepOneDateTaken",
			"StepOneThreeDigitScore",
			"StepTwoDateTaken",
			"StepTwoThreeDigitScore",
			"StepThreeDateTaken",
			"StepThreeThreeDigitScore",
			"NBOME ID",
			"ComlexStep1DateTaken",
			"Comlex1 Score",
			"ComlexStep2DateTaken",
			"Comlex2 Score",
			"ComlexStep3DateTaken",
			"Comlex3 Score",
			"AoaStatus",
			"GoldHumanismStatus",
			"Category",
			"First Delivery",
			"Last Updated",
			"Last Reviewed",
			"Address1",
			"Address2",
			"City",
			"State",
			"Zip",
			"Country",
			"PhoneHome",
			"PhoneCell"
		]

		self.standardFields = [
			"uuid",
			"first name",
			"last name",
			"email",
			"medical school",
			"aamcid",
			"city",
			"state",
			"zip",
			"country",
			"USMLE Step 1 Score",
			"USMLE Step 2 CK Score",
			"ComlexStep1DateTaken",
			"Comlex1 Score",
			"ComlexStep2DateTaken",
			"Comlex2 Score",
			"ComlexStep3DateTaken",
			"Comlex3 Score",

		]
	def test(self):
		 es = Elasticsearch([{'host': self.esHost, 'port': self.esPort }])
		 print(es)

	def handle(self, file, organization, year):
		try:
			# time.sleep(2)
			print("CSV CONTROLLER HANDLE")
			candidates = []
			# SET MATCH VARIABLE 
			# match = False
			# READ CSV FILE TO GET HEADER FIELDS
			with open(file, 'r') as infile:
				reader = csv.DictReader(infile)
				fields = reader.fieldnames
				print(fields)

			print('READING CSV HEADER')
			# SET ARRAY OF DIFFERENT FIELD ARRAYS TO COMPARE CSV AGAINST
			# fieldArrays = [
			# 	self.erasFieldsOne, 
			# 	self.erasFieldsTwo, 
			# 	self.erasFieldsThree, 
			# 	self.erasFieldsFour,
			# 	self.erasFieldsFive,
			# 	self.erasFieldsSix,
			# 	self.erasFieldsSeven,
			# 	self.erasFieldsEight,
			# 	self.erasFieldsNine,
			# 	self.erasFieldsTen,
			# 	self.sfFields
			# ]
			# GET SET OF FIELDS FROM CSV FILE
			# setFields   = set(fields)
			# IF THERE ARE MATCHING FIELDS CONVERT EARCH CSV ROW TO A JSON OBJECT AND PUSH TO CANDIDATES ARRAY
			# for i, x in enumerate(fieldArrays):
				# print('FIELD ARRAYS')
				# ctrlSet = set(x)
				# ctrlSet = x
				# if fields == x:
				# 	print('FOUND A MATCH')
				# 	match = True
				# 	header = x
			with open(file, "r") as f:
				reader = csv.reader(f)
				for l, line in enumerate(reader):
					if l == 0:
						print("CSV HEADER")
					else:
						json = {}
						for i, f in enumerate(line):
							key = fields[i]
							value = f
							try:
								check = self.checkFields(key, value)
							except IndexError:
								print("INDEX ERROR")
								check = {}

							json.update(check)

							if len(value) > 0:
								json[key] = value
							else:
								json[key] = 'n/a'

						candidates.append(json)
					
			print(len(candidates))
			self.importCandidates(candidates, organization, year)
			return
			
		except Exception as e:
			print(e)
			return

	# else:
	# 	print('NO MATCH')
	# 	match = False

	def importCandidates(self, candidates, organization, year):
		try:
			print("START IMPORTING CANDIDATES")
			es = Elasticsearch([{'host': self.esHost, 'port': self.esPort, 'use_ssl': True }])
			print(es)
			newCandidates = []
			currentCandidates  = []
			for x in candidates:
				if "aamcid" in x:
					QS = '(aamcid:"'+x['aamcid']+'") AND (Organization:"' + organization + '") AND (Rank-Term:' + year + ')'
					candidate = es.search(
						index="candidates", 
						body={ 
							"query": 
								{  
								"query_string": {  "query": QS } 
								} 
						},
						size=1
					)
					hits = candidate['hits']['hits']
					if len(hits) == 0:
						newCandidates.append(x)
					else:
						currentCandidates.append(x)
				else:
					newCandidates.append(x)

			for x in newCandidates:
				cid = uuid.uuid4()
				cid = str(cid)
				x['uuid'] = cid
				x['Organization'] 	 		= organization
				x['interview-year']  		= year
				x['Rank-Term']  		    = year
				x['interview_score'] 		= 0
				x['preinterview_score'] 	= 0
				x['total-score'] 			= 0
				x['manual_rank']			= 0
				x['rank']  			 		= 0
				x['status']  			 	= 'pre-interview'
				if "Medical School of Graduation" in x:
					x['medical school'] = x['Medical School of Graduation']

				self.table.put_item(Item=x)
				es.index(index='candidates', doc_type='_doc', id=cid, body=x)

			print("TASK COMPLETE")
			return

		except Exception as e:
			print(e)
			return


	def checkFields(self, field, value):
		try:
			match = False
			obj = {}
			sField = field.lower()
			sField = sField.strip()
			for i, x in enumerate(self.standardFields):
				xClean = x.lower()
				xClean = x.strip()
				distance = Levenshtein.distance(sField, xClean)
				if distance > 2:
					match = False
				else:
					print("MATCH FOUND")
					print(field)
					match = True
					obj[x] = value

			print(obj)
			return obj

		except IndexError:
			print("INDEX ERROR")
			pass

	def validate(self, file, organization, year):
		print("VALIDATE CSV")
		print(file, organization, year)
		self.handle(file, organization, year)

	def processXML(self, file, organization, year):
	    candidates = []
	    header = ['ApplicantId', 'LastName', 'FirstName', 'Email', 'AddToInterviewList', 'MedSchool', 'YearOfGraduation', 'AAMC ID', 'CurrentResidency', 'YearOfResCompletion', 'StepOneDateTaken', 'StepOneThreeDigitScore', 'StepTwoDateTaken', 'StepTwoThreeDigitScore', 'StepThreeDateTaken', 'StepThreeThreeDigitScore', 'NBOME ID', 'ComlexStep1DateTaken', 'Comlex1 Score', 'ComlexStep2DateTaken', 'Comlex2 Score', 'ComlexStep3DateTaken', 'Comlex3 Score', 'AoaStatus', 'GoldHumanismStatus', 'Category', 'First Delivery', 'Last Updated', 'Last Reviewed', 'Address1', 'Address2', 'City', 'State', 'Zip', 'Country', 'PhoneHome', 'PhoneCell']
	    count = 0
	    string = open(file, 'r').read()
	    pp = xmltodict.parse(string)
	    if pp['Workbook']['Worksheet'][0]['Table']['Row']:
	        for inx, x in enumerate(pp['Workbook']['Worksheet'][0]['Table']['Row']):
	            if inx == 0:
	                print("SKIP HEADER")
	            else:
	                rowJson = loads(dumps(x))
	                candidate = {}
	                index = 0 
	                if "Cell" in rowJson:
	                    data = rowJson['Cell']
	                    for obj in data:
	                        if "Data" in obj:
	                            if "#text" in obj['Data']:
	                            	if header[index] == "MedSchool":
	                            		candidate['medical school'] = str(obj["Data"]["#text"])
	                            	else:
	                            		candidate[header[index]] = str(obj["Data"]["#text"])

	                            	index += 1

	                            else:
	                                index += 1

	                        else:
	                            print("NO DATA")

	                    candidates.append(candidate)

	                else:
	                    print("CELL NOT FOUND")
	    else:
	        return False

	    # CHECK FOR STANDARD FIELDS 
	    mergedCandidates = []
	    for value in candidates:
	    	tmpObj = {}
	    	for key in value:
	    		check = self.checkFields(key, value[key])
	    		if check:
	    			tmpObj.update(check)

	    	value.update(tmpObj)
	    	mergedCandidates.append(value)
	    self.importCandidates(mergedCandidates, organization, year)
	    return

