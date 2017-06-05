sydney_db = db[collection]  

docnum = sydney_db.find().count()  
print "Number of documents:", docnum

# Create a function to return results of the cursor execution
def agg_pipeline(db, pipeline):
    return [doc for doc in sydney_db.aggregate(pipeline)]

# Create a pipeline for nodes and ways 
for elem_type in ['node', 'way']: 
    pipeline = [{"$match" : {'type': elem_type}}, 
                { "$group" : { "_id" : "$"+elem_type+".uid","count" : { "$sum" : 1}}}, 
                { "$group" : { "_id" : "unique"+elem_type+"users", "count" : { "$sum" : 1}}}
                ] 
    results = agg_pipeline(sydney_db, pipeline)
    print elem_type, ":", results 
	
# Create a list because we need unique values only
unique_users = set()

for elem_type in ['node', 'way']: 
    # Finding all the records of each type 
    results = sydney_db.find({"type":elem_type})
    for elem in results:
        # Adding unique uid's to the set
        unique_users.add(elem[elem_type]['uid'])   
    
print "The number of unique users:", len(unique_users)

pipeline = [{"$match": {"type": "node", "node_tags.value": "bicycle_pump"}}, 
            {"$group" : { "_id" : "Bicycle pumps","count" : { "$sum" : 1}}}
           ]

print "Bicycle pumps:", agg_pipeline(sydney_db, pipeline)[0]['count']

pipeline = [{"$match": {"type": "node", "node_tags.value": "bicycle_parking"}}, 
            {"$group" : { "_id" : "Bicycle parkings","count" : { "$sum" : 1}}}
           ]

print "Bicycle parking:", agg_pipeline(sydney_db, pipeline)[0]['count']

# Three most referenced nodes 
pipeline = [{"$match": {"type": "way"}}, 
            {"$unwind": "$way_nodes"},
            {"$group" : { "_id" : "$way_nodes.node_id","count" : { "$sum" : 1}}}, 
            {"$sort": {"count": -1}},
            {"$limit": 3}
           ]

# Getting 3 most referenced nodes 
ref_nodes = agg_pipeline(sydney_db, pipeline)
# Printing every node
for node in ref_nodes: 
    pprint.pprint(sydney_db.find({'node.id': node['_id']})[0])
	
	
# Pipeline to calculate ages. Difference is first calculated in milliseconds. 
# We will recalculate it to days by dividing on (1000(ms)*60(s)*60(m)*24(h))
from datetime import datetime
pipeline = [{"$match": {"type": "way"}},
            {'$project': {'DiffMilliSec': {'$subtract': [datetime.now(), '$way.timestamp']}}}, 
            {'$project': {'_id': 1, 'AgeDays': {'$divide': ['$DiffMilliSec', 1000*60*60*24]}}}, 
            {"$sort": {"AgeDays": -1}},
            {"$limit": 15}
           ]

results = agg_pipeline(sydney_db, pipeline)
for result in results: 
    print "Id:", result['_id'], "Age in days:", result['AgeDays']
	

# Remove limit from the pipeline
pipeline = [{"$match": {"type": "way"}},
            {'$project': {'DiffMilliSec': {'$subtract': [datetime.now(), '$way.timestamp']}}}, 
            {'$project': {'_id': 1, 'AgeDays': {'$divide': ['$DiffMilliSec', 1000*60*60*24]}}}, 
            {"$sort": {"AgeDays": -1}}
           ]

results = agg_pipeline(sydney_db, pipeline)

# Create and populate dictionary
agedict = {}
for result in results: 
    agedict[result['_id']] = result['AgeDays']
    
# Import pandas DataFrame to create a dataframe and plot it
from pandas import DataFrame
# Create a dataframe with rows as keys
agedf = DataFrame.from_dict(agedict, orient='index')  

# Plot data 
%pylab inline
import matplotlib.pyplot as plt
import seaborn as sns

# Plotting a histogram
agedf[0].hist(bins = 80)