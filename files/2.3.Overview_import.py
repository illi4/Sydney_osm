import os 
# Convert from bytes to megabytes and show two decimal points only 
print 'The source XML size: {:0.2f} MB'.format(os.path.getsize(filename)/1.0e6) 
print 'Produced JSON file: {:0.2f} MB'.format(os.path.getsize(filename + ".json")/1.0e6)

import signal  
import subprocess
from pymongo import MongoClient

db_name = 'openstreetmap'

# Connect to Mongo DB
client = MongoClient('localhost:27017')  
# Database 'openstreetmap' will be created if it does not exist
db = client[db_name]  

# Preparing for mongoimport
collection = filename[:filename.find('.')]  # name before the file extention

workdir = "D:\Data_science\Nanodegree\\4.Data_wrangling\Submission\\"
json_file = filename + '.json'

# Command for importing 
mongoimport_cmd = 'mongoimport -h 127.0.0.1:27017 ' + \
                  '--db ' + db_name + \
                  ' --collection ' + collection + \
                  ' --file ' + workdir + json_file

if collection in db.collection_names():  
    print 'Dropping collection: ' + collection
    db[collection].drop()

print "Executing: ", mongoimport_cmd
subprocess.call(mongoimport_cmd.split())  