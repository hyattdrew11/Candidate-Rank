#!3 USER
from boto.dynamodb2.items import Item

class User:

    def __init__(self, item):
        self.item			= item
        self.date_created	= item["date_created"]
        self.date_modified	= item["date_modified"]
        self.email       	= item["email"]
        self.password   	= item["password"]
        self.role           = item["role"]
        self.status         = item["status"]
        self.organization   = item["Organization"]
        self.first_name     = item["first_name"]
        self.last_name      = item["last_name"]
        
    def getStatus(self):
        status = self.status
        return status
    status = property(getStatus)