import urllib
import urllib.parse
import urllib.request
import logging
from logging.config import fileConfig
from timeit import Timer
import csv
import xml.etree.ElementTree as ET
import re

fileConfig('logging_config.ini')
l = logging.getLogger(__name__)
l.setLevel(logging.DEBUG)

API_PREFIX = 'http://api.walkscore.com/score?format=xml&'
WORK_COORDS = '-122.6775827,45.5155211'

FIELDS = ['formatted_address',
 'asking_price',
 'transit_time',
 'transit_transfers',
 'transit_start_time',
 'walk_score',
 'home_size',
 'property_size',
 'bedrooms',
 'bathrooms',
 'tax_value',
 'tax_year',
 'last_sold_price',
 'last_sold_date',
 'year_built',
 'mls_id',
 'zillow_id',
 'home_detail_link',
 'walk_score_link',
 'street_number', 
 'route', 
 'locality', 
 'postal_code', 
 'postal_code_suffix', 
 'neighborhood', 
 'administrative_area_level_1', 
 'administrative_area_level_2', 
 'latitude', 
 'longitude', 
 'country', 
 'place_id']
 
def namespace(tree):
    root = tree.getroot()
    m = re.match('\{.*\}', root.tag)
    return m.group(0) if m else ''
    
def text_from_node(name, tree):
    search_string = ".//" + namespace(tree) + name
    l.debug("Searching for " + search_string)
    results = tree.findall(search_string)
    l.debug("Found: " + str(results))
    return results[0].text
 
def api_results_from(address, lat, long):
    api_vars = {'address': address, 
                'lat': lat, 
                'lon': long, 
                'wsapikey': open('walkscore_api_key.secret').read()}
    results = urllib.request.urlopen(API_PREFIX + urllib.parse.urlencode(api_vars)).read().decode('UTF-8', 'strict')
    l.info("Results: " + str(results))
    return results
    
def main():
    reader = csv.DictReader(open('short_transit_times.csv'))
    writer = csv.DictWriter(open('short_transit_times_with_walkscore.csv', 'w', newline=''), FIELDS)
    writer.writeheader()
    
    for row in reader:
        xml = ET.ElementTree(ET.fromstring(api_results_from(row['formatted_address'], row['latitude'], row['longitude'])))
        # Noisy: 
        l.debug("Tags: " + '\n'.join(map(lambda x: str(x), xml.findall(".//*"))))
        new_columns = {'walk_score': text_from_node('walkscore', xml),
                       'walk_score_link': text_from_node('ws_link', xml)}
        new_row = row.copy()
        new_row.update(new_columns)
        writer.writerow(new_row)
        
if __name__ == '__main__':
    main()