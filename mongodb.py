from pymongo import *
myclient = MongoClient("mongodb://localhost:27017")
mydb = myclient["CourseOutline"]
OutlineCollection = mydb['Outline']
LOGGINGCOLLECTION = mydb['LOG']
USERSCOLLECTION = mydb['USER']
