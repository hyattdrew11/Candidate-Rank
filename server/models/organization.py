#!3 ORGANIZATION
from boto.dynamodb2.items import Item

class Organization:

    def __init__(self, item):
        self.item			    = item
        self.date_created	    = item["date_created"]
        self.date_modified	    = item["date_modified"]
        self.name               = item["name"]
        self.admin       	    = item["admin"]
        self.picture            = item["picture"]
        self.candidates         = item["candidates"]
        self.status             = item["status"]
        self.billing_address    = item["billing_address"]
        self.billing_zip        = item["billing_zip"]
        self.billing_plan       = item["billing_plan"]
        
    def getStatus(self):
        status = self.status
        return status
    status = property(getStatus)