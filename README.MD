# Sydney OpenStreetMap data wrangling 

The aim of this project is to analyse a [metro extract](https://mapzen.com/data/metro-extracts/metro/sydney_australia/) of Sydney OpenStreetMap data, which includes the following steps: 

1. Auditing the xml data. 
2. Defining functions to clean problematic tags, street names and types, maximum speed values, and cycling-related tags. 
3. Transformation of data to Python dictionary and exporting to JSON file. 
4. Connecting to MongoDB and importing data. 
5. Additional examination of data in MongoDB using queries requested from Python. 
6. Concluding on the data wrangling process, benefits, and potential issues for future use. 

## Results
The results are saved in the [Jupyter notebook file](Sydney_osm_wrangling.ipynb) in the repository. 

## Files
The following auxiliary files can be found in the files folder in the repository: 
- sydney.zip: Zipped OSM XML file. 
- 2.1.Auditing_data.py: Code used for data auditing. 
- 2.1.Transform_data.py: Used for data transformation from xml to json.  
- 2.3.Overview_import.py: Overview of the files, import to MongoDB. 
- 2.4.Examine.py: Examination of imported data in MongoDB. 