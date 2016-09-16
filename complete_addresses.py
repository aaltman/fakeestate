import urllib
import urllib.parse
import urllib.request
import logging
from logging.config import fileConfig
import json
from timeit import Timer
import csv
#from apiclient.discovery import build

fileConfig('logging_config.ini')
l = logging.getLogger('getzips')
l.setLevel(logging.DEBUG)

GEOCODE_PREFIX = 'https://maps.googleapis.com/maps/api/geocode/json?'
CSV_OUT_PATH = 'full_addresses.csv'
COLUMN_ORDER = ['formatted_address',
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

key = open("apikey.secret").read()
l.info("Key: " + key)
addresses = ["396 NW 182nd Ave, Beaverton, OR"]

def type_and_value_from_address_component(gmaps_address_component):
    # We can (usually?) throw out any type past the first; 
    # the first is usually the address, ZIP, etc., while 
    # the second is typically a general category like 'political'.
    # I haven't seen a third yet.
    ad_type = gmaps_address_component['types'][0]

    # Use the short name since we'll probably have a lot of these,
    # and they seem a little more human readable in bulk than the
    # long name.
    val = gmaps_address_component['short_name']

    l.debug("{%s: %s}" % (ad_type, val))
    return ad_type, val

def complete_address(gmaps_json):
    completed = {}
    results = gmaps_json['results'][0]
    completed['formatted_address'] = results['formatted_address']
    for component in results['address_components']:
        key, val = type_and_value_from_address_component(component)
        completed[key] = val
    completed['latitude'] = results['geometry']['location']['lat']
    completed['longitude'] = results['geometry']['location']['lng']
    completed['place_id'] = results['place_id']
    
    l.debug("Flattened complete address: \n%s", str(completed))
    return completed

def main():
    #completed_addresses = []
    writer = csv.DictWriter(open(CSV_OUT_PATH, 'w'), COLUMN_ORDER)
    writer.writeheader()

    for ad in addresses:
        l.info("Address: " + ad)
        url = GEOCODE_PREFIX + urllib.parse.urlencode({'address': ad, 'key': key})
        logging.debug("Urlencoded: " + str(url))
        results = urllib.request.urlopen(url).read().decode("utf-8", "strict")  
        logging.debug("Raw results: \n" + results)
        j = json.loads(results)
        writer.writerow(complete_address(j))
        #completed_addresses.extend(complete_address(j))

    l.info("Retrieved %d addresses." % len(addresses))

    #with open(CSV_OUT_PATH, 'w') as csvfile:
        
		
        
if __name__ == '__main__':
    t = Timer("main()", "from __main__ import main")
    print(t.timeit(number=1))