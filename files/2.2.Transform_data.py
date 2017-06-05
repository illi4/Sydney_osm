# Import libraries which will be necessary to perform transformations 
import string 

# Specifying the same filename as in the auditing data file
filename = 'sydney.osm'

# Fields which will be processed
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# Function to process tags
def process_tag(tag, id_input): 
    tag_dict = {}

    # Working with tags 
    tag_val = tag.attrib['v']
    tag_key = tag.attrib['k']
    
    # Correct street names 
    if tag_key == "addr:street": 
        tag_val = process_st_name(tag_val)   
    # Correct maximum speed values 
    if tag_key == "maxspeed": 
        tag_val = process_speed(tag_val)
    # Correct bicycle-related tags
    if (tag_key in bicycle_way_tags): 
        tag_val = process_bicycle(tag_val)  
 
    # Filling tag dictionary 
    tag_dict['id'] = id_input
    tag_dict['value'] = tag_val  
    
    # If there are no problem chars 
    if not re.search(problemchars, tag_key): 
        key_split = tag_key.split(':',1)   # to split keys    
        if key_split[0] == tag_key: 
            tag_dict['key'] = tag_key
            tag_dict['type'] = 'regular' 
        else: 
            tag_dict['key'] = key_split[1] 
            tag_dict['type'] = key_split[0]   
    # If there are problem chars - check if this is a payments tag and process accordingly
    else: 
        tag_key_corr, tag_val_corr = process_bad_payment(tag_key, tag_val)
        if tag_key_corr != tag_key: 
            tag_dict['key'] = tag_key_corr
            tag_dict['value'] = tag_val_corr  
            tag_dict['type'] = 'regular'   
    return tag_dict

# Function to clean and shape node or way XML element to Python dict
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=problemchars, default_tag_type='regular'):

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
                    
    # Filling values for 'node'
    if element.tag == 'node':
        node_id = element.attrib['id']
        for field_e in NODE_FIELDS: 
            # Fixing timestamp
            if field_e == 'timestamp':
                node_attribs[field_e] = datetime.strptime(element.attrib[field_e], '%Y-%m-%dT%H:%M:%SZ')
            else:
                node_attribs[field_e] = element.attrib[field_e]
            
        for tag in element.iter("tag"):
            tag_dict = process_tag(tag, node_id)
            tags.append(tag_dict)

    # Filling values for 'way'
    if element.tag == 'way':
        way_id = element.attrib['id']
        for field_e in WAY_FIELDS: 
            if field_e == 'timestamp':
                way_attribs[field_e] = datetime.strptime(element.attrib[field_e], '%Y-%m-%dT%H:%M:%SZ')
            else:
                way_attribs[field_e] = element.attrib[field_e]
            
        count = 0 
        for nd in element.iter("nd"): 
            way_nodes_dict = {}
            way_nodes_dict['id'] = way_id
            way_nodes_dict['node_id'] = nd.attrib['ref']
            way_nodes_dict['position'] = count
            way_nodes.append(way_nodes_dict) 
            count+=1
        for tag in element.iter("tag"):
            tag_dict = process_tag(tag, way_id)
            tags.append(tag_dict)
    
    if element.tag == 'node':
        return {'type' : 'node', 'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'type' : 'way', 'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
		
# Actual file processing 

import json  
# BSON will be used for compatibility 
from bson import json_util

# Iteratively process each XML element 
def process_map(file_in, pretty = False):  
    file_out = "{0}.json".format(file_in)
    with open(file_out, "wb") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                fo.write(json.dumps(el, default=json_util.default) + "\n")

# Now process elements
process_map(filename)  		
