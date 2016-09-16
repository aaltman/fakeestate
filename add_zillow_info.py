import urllib
import urllib.parse
import urllib.request
import logging
from logging.config import fileConfig
import json
from timeit import Timer
import csv
import pyzillow.pyzillow
from pyzillow.pyzillow import ZillowWrapper, GetDeepSearchResults
import csv

fileConfig('logging_config.ini')
l = logging.getLogger('add_zillow_info')
l.setLevel(logging.DEBUG)

API_PREFIX = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm?'
  
NEW_FIELDS = ['home_size',
 'property_size',
 'bedrooms',
 'bathrooms',
 'tax_value',
 'tax_year',
 'last_sold_price',
 'last_sold_date',
 'year_built',
 'zillow_id',
 'home_detail_link']

ALL_FIELDS = ['formatted_address',
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
  'place_id'] + NEW_FIELDS

zillow = ZillowWrapper(open('zillow_api_key.secret').read())
# Test value: addresses = ["396 NW 182nd Ave, Beaverton, OR"] # FIXME add zip - this expects we've already gotten it from Google

def main():
    reader = csv.DictReader(open('full_addresses.csv'))
    writer = csv.DictWriter(open('full_addresses_with_zillow_info.csv', 'w', newline=''), ALL_FIELDS)
    writer.writeheader()
    
    for row in reader:
        address = "%s %s %s %s" % (row['street_number'], row['route'], row['locality'], row['administrative_area_level_1'])
        zip_code = "%s-%s" % (row['postal_code'], row['postal_code_suffix'])
        
        try:
            response = zillow.get_deep_search_results(address, zip_code)
            result = GetDeepSearchResults(response)
        except pyzillow.pyzillowerrors.ZillowError:
            l.error("Got ZillowError for property %s; skipping." % row['formatted_address'])
            continue
        l.debug("Got result object: %s", str(vars(result)))
        
        # Add just the fields we're interested in.
        new_row = row.copy()
        for key in NEW_FIELDS:
            new_row[key] = result.__dict__[key]
            
        l.debug("Annotating Google maps property info with Zillow results: %s" % new_row)
        writer.writerow(new_row)
        
if __name__ == '__main__':
    main()