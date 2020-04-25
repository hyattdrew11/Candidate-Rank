#! SURVEY
import boto3

class Survey:

    def __init__(self, item):
        self.item			= item
        self.uuid           = item.uuid
        self.date_created	= item.date_created
        self.date_modified	= item.date_modified
        self.organization   = item.organization 
        self.term           = item.term 
        self.type           = item.type 
        self.name       	= item.name
        self.questions      = item.questions


# EXAMPLE
# survey = {
#     "uuid"          : "1234-5678-1234-5678"
#     "date_created"  : "2020-03-04 14:20:27.813232"
#     "date_modified" : "2020-03-04 14:20:27.813232"
#     "Organization"  : "Tulane"  
#     "term"          : "2020"  
# 	  "type"          : "2020"  
#     "name"          : "Survey 2020"
#     "questions"     : [{}] 
# }