#!3 CANDIDATE
from boto.dynamodb2.items import Item

class Candidate:

    def __init__(self, item):
        self.item			= item
        self.uuid           = item.uuid
        # self.uuid           = item["uuid"]
        # self.date_created	= item["date_created"]
        # self.date_modified	= item["date_modified"]
        # self.email       	= item["email"]
        # self.first_name     = item["first_name"]
        # self.last_name      = item["last_name"]
        # self.school         = item["school"]
        # self.picture        = item["picture"]
        # self.organiztion    = item["organiztion"]
        # self.rank           = item["rank"]
        
    def getStatus(self):
        status = self.status
        return status
    status = property(getStatus)