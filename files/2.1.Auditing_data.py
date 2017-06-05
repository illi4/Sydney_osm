import xml.etree.cElementTree as ET
import pprint

filename='sydney.osm'

tags = {}

for event, elem in ET.iterparse(filename):  
    if elem.tag in tags: 
        tags[elem.tag] += 1
    else:                
        tags[elem.tag] = 1

pprint.pprint(tags)  

# Regular expressions module
import re

# Expression to detect problematic characters, characters in lowercase without and with colon 
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == "tag":
        check_k = element.attrib['k']
        if re.search(lower, check_k): 
            keys['lower'] += 1     
        elif re.search(lower_colon, check_k): 
            keys['lower_colon'] += 1        
        elif re.search(problemchars, check_k): 
            print "Problematic key: '", check_k, "', value ", element.attrib['v']
            keys['problemchars'] += 1        
        else:
            keys['other'] += 1
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        # _ is a throwaway value here 
        keys = key_type(element, keys)
    return keys

process_map(filename)

# Create a function to process the problematic payments tag for future reference
def process_bad_payment(t_key, t_val): 
    if (t_key.lower().find('payment') >= 0):
        t_key = "payment:credit_cards"
        t_val = "yes"
    return t_key, t_val
	
	
# Using defaultdict to allow for default (zero) values 
from collections import defaultdict

# Auditing street types

# Sequence of non-whitespace characters \S+ optionally followed by period (to catch st./sqr./etc.), 
# which should appear in the string ending ($)
street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)

# For int, the default value is zero. A defaultdict will never raise a KeyError. 
street_types = defaultdict(int)

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_types[street_type] += 1

def print_sorted_dict(d):
    keys = d.keys()
    # Sort the keys alphabetically independently from upper/lower case
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k, v) 

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def audit(filename):
    for event, elem in ET.iterparse(filename):
        # If this is a tag with street name
        if is_street_name(elem):
            # Update the counter for the corresponding street type 
            audit_street_type(street_types, elem.attrib['v'])    
    print_sorted_dict(street_types)    

# Running the main function on our dataset
s_types = audit(filename)
pprint.pprint(s_types)  

# List with expected names
expected = ["Avenue", "Boulevard", "Broadway", "Circuit", "Crescent", "Terrace", "Way", 
            "Drive", "Highway", "Lane", "Parade", "Place", "Road", "Street", "Square", 
            "Gardens", "Point"]

street_types_modified = defaultdict(set)
    
# Let's change our function to addy full values for unexpected street names 
def audit_street_type_modified(street_types, street_name):
    # Use the regular expression defined previously
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types_modified[street_type].add(street_name)

# And rewrite the audit function so it returns street types
def audit_modified(filename):
    for event, elem in ET.iterparse(filename):
        # If this is a tag with street name
        if is_street_name(elem):
            # Update the counter for the corresponding street type 
            audit_street_type_modified(street_types, elem.attrib['v'])    
    return street_types   
        
# Running the main function on our dataset
st_types = audit(filename)
pprint.pprint(dict(st_types)) 

# Updated list with expected names
expected = ["Avenue", "Boulevard", "Broadway", "Circuit", "Crescent", "Terrace", "Way", 
            "Drive", "Highway", "Lane", "Parade", "Place", "Road", "Street", "Square", 
            "Gardens", "Point", 
            "Arcade", "Boulevarde", "Esplanade", "North", "Plaza", "Promanade", "South"
           ]

# Dictionary with mapping 
mapping = { "street": "Street", 
            "St.": "Street", 
            "St": "Street"
            }

# P.5: For these names, 'Street' should be added
add_street = ["Berit", "Edward", "Fitzroy", "Jones", "Shaw", "Wolli"]

def name_clean(name): 
    # Capitalise the first letter 
    name = name[:1].upper() + name[1:]
    # P.1: If there is parenthesis - return the part before parenthesis
    name = re.sub(r'\s\([^)]*\)', '', name)
    # P.2: Remove non-English and non-alphanumeric excluding '&' symbol, commas, and spaces (\s)
    name = re.sub('[^0-9a-zA-Z&,\s]+', '', name)
    # P.3: If there is one comma, return symbols before the comma
    name_split = name.split(',')
    if len(name_split) == 2: name = name_split[0].strip()
    # P.4: If there are two commas or more, return value after first and before second
    if len(name_split) > 2: name = name_split[1].strip()
    # Removing all excess whitespaces 
    name = ' '.join(name.split())
    return name

def name_corr(name):
    # P.6: Handling specific cases
    if name == "King Street Offramp": name = "King Street"
    if name == "Pacific Highway underpass": name = "Pacific Highway"
    if name == "nr East street": name = "East Street"
    # P.5: Adding 'Street' where required 
    if name in add_street: 
        return name + " Street"
    else: 
        return name

# After performing name_clean and name_corr, we should check if street name is in expected
# If not - map; we will return None if mapping cannot be done 
def name_map(name, mapping):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()     
        if street_type in expected: 
            return name
        else: 
            if street_type in mapping:
                name = name.replace(street_type, mapping[street_type])          
            else: 
                name = None
    else: 
        name = None        
    return name 

# Combine all the functions
def process_st_name(name):
    name = name_clean(name)
    name = name_corr(name)
    name = name_map(name, mapping)  
    return name 

# Interating through s_types which we creaated previously to check the outcome
for st_type, ways in st_types.iteritems():
    for name in ways:
        print name, "=>", process_st_name(name)
		

# Auditing maximum speed values 
# Create an empty list for further cleaning
speeds_to_clean = []

def is_speed(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "maxspeed")

# Checking the values. Speeds between 5-120 are valid, and 'signals' is a valid value too
def audit_speeds(filename):
    for event, elem in ET.iterparse(filename):
        if is_speed(elem):
            try: 
                speedval = int(elem.attrib['v'])
                # Print value if it is below 5 or above 120 kmph
                if (int(speedval) < 5) or (int(speedval) > 120): 
                    print "Too low/high: ", speedval 
                    speeds_to_clean.append(speedval)
            except ValueError: 
                # Non-numeric value
                if elem.attrib['v'] != 'signals': 
                    print "Non-numeric value: ", elem.attrib['v']
                    speeds_to_clean.append(elem.attrib['v'])

# Analyse the dataset
speed_analysis = audit_speeds(filename)

# Function to correct speeds
def process_speed(speed): 
    try: 
        # P.4 - zeros should be changed to None 
        speed = int(speed)
        if speed == 0: speed = None
    except ValueError: 
        # P.1 - remove 'mph'
        speed = speed.replace(' mph','')
        # Try to convert to int again 
        try: 
            speed = int(speed)
        except ValueError: 
            # Handling P.2 & P.3
            if speed == 'sign': speed = 'signals'
            if speed == '10;10': speed = 10
    return speed

# Try on problematic values 
for speed in speeds_to_clean: 
    print speed, "=>", process_speed(speed)
	
# Auditing cycleways
# Possible tags are cycleway, cycleway:right, cycleway:left
cycleway_tags = ['cycleway', 'cycleway:left', 'cycleway:right']

# Tags and expected values for bicycle and cycleway tags as specified on OSM Wiki
cycleway_expected = ['lane', 'opposite_lane', 'opposite', 'shared_lane', 'share_busway', 'shared', 
                     'track', 'opposite_track', 'asl', 'shoulder', 'separate', 'no', 'yes', 
                     'right', 'crossing', 'segregated', 'none', 'sidepath', 'both', 'unmarked_lane', 
                     'left'] 
bicycle_expected = ['yes', 'no', 'designated', 'use_sidepath', 'permissive','destination', 'dismount']

# A dictionary to check unexpected values and their frequency
cycleway_unexp = defaultdict(int)
bicycle_unexp = defaultdict(int)

def is_cycleway(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] in cycleway_tags)

def is_bicycle(elem): 
    return (elem.tag == "tag") and (elem.attrib['k'] == "bicycle")

# Checking the values. Speeds between 5-120 are valid, and 'signals' is a valid value too
def audit_cycleways(filename):
    for event, elem in ET.iterparse(filename):
        if is_cycleway(elem): 
            if elem.attrib['v'] not in cycleway_expected:
                cycleway_unexp[elem.attrib['v']] += 1
        if is_bicycle(elem): 
            if elem.attrib['v'] not in bicycle_expected:
                bicycle_unexp[elem.attrib['v']] += 1
                
# Analyse the dataset
audit_cycleways(filename)
print "Unexpected cycleway tag values:"
pprint.pprint(dict(cycleway_unexp))
print "Unexpected bicycle tag values:"
pprint.pprint(dict(bicycle_unexp))

# Create a joint cycleways / bicycle tags list for future reference 
bicycle_way_tags = ['cycleway', 'cycleway:left', 'cycleway:right', 'bicycle']

def process_bicycle(name): 
    # If there is semicolon - return the part before it
    name = name.split(";")[0]
    # Remove non-English and non-alphanumeric
    name = re.sub('[^0-9a-zA-Z]+', '', name)
    # Other improvements 
    if name == 'y': name = 'yes'
    if name == 'stupid': name = 'yes'
    return name 

print "Cycleway tag values"
for element in cycleway_unexp:
    print element, "=>", process_bicycle(element)

print "\nBicycle tag values"
for element in bicycle_unexp:
    print element, "=>", process_bicycle(element)