from pymongo import MongoClient


class MongoDB:

    def __init__(self, uri, db):
        self.conn = MongoClient(uri)[db]

    def insert(self, collection, data):
    	self.conn[collection].insert_one(data)

    def select(self, collection, userID):
        return self.conn[collection].find({ "UserID": userID })
    
    def deleteUserID(self, collection, userID):
        return self.conn[collection].delete_one({ "UserID": userID })

    def findUserID(self, collection, userID, ip):
        return self.conn[collection].find({ "UserID": userID, "ipAddress": ip })
            
        
