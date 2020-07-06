from pymongo import MongoClient


class MongoDB:

    def __init__(self, uri, db):
        self.conn = MongoClient(uri)[db]

    def insert(self, collection, data):
    	self.conn[collection].insert_one(data)

    def select(self, collection):
        return self.conn[collection].find()
            
        
