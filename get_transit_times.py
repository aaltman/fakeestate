import urllib
import urllib.parse
import urllib.request
import logging
from logging.config import fileConfig
from timeit import Timer
import csv
import re

fileConfig('logging_config.ini')
l = logging.getLogger('add_zillow_info')
l.setLevel(logging.DEBUG)

API_PREFIX = 'http://developer.trimet.org/ws/V1/trips/tripplanner?'
WORK_COORDS = '-122.6775827,45.5155211'

FIELDS = ['formatted_address',
 'asking_price',
 'transit_time',
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
 
def api_results_from(lat, long, min, date='2016-10-03', time='8:55am', arr='A'):
    """Given a latitude and longitude to start from, get an itinerary to 
    WORK_COORDS with quickest trip (min = 'T'), fewest transfers ('X') 
    or shortest walk ('W')."""
    api_vars = {'fromCoord': str(long) + "," + str(lat),
                'toCoord': WORK_COORDS,
                'Date': date,
                'Time': time,
                'Min': min,
                'Arr': arr,
                'MaxIntineraries': '1',
                'appID': open('trimet_api_key.secret').read()}
    results = urllib.request.urlopen(API_PREFIX + urllib.parse.urlencode(api_vars)).read().decode('UTF-8', 'strict')
    l.info("Results: " + str(results))
    
def main():
    reader = csv.DictReader(open('info_with_prices.csv'))
    writer = csv.DictWriter(open('info_with_transi_times_and_prices.csv', 'w', newline=''), FIELDS)
    writer.writeheader()
    
    for row in reader:
        api_results_from(row['latitude'], row['longitude'], 'T')
        exit()
        
if __name__ == '__main__':
    main()