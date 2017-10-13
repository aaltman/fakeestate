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

API_PREFIX = 'http://developer.trimet.org/ws/V1/trips/tripplanner?'
WORK_COORDS = '-122.6775827,45.5155211'

FIELDS = [ 'SALE TYPE',
  'PROPERTY TYPE',
  'ADDRESS',
  'CITY',
  'STATE',
  'ZIP',
  'LIST PRICE',
  'LAST SOLD PRICE',
  'BEDS',
  'BATHS',
  'LOCATION',
  'SQFT',
  'LOT SIZE',
  'YEAR BUILT',
  'DAYS ON MARKET',
  'STATUS',
  'NEXT OPEN START HOUSE DATE',
  'NEXT OPEN END HOUSE DATE',
  'URL (SEE http://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)',
  'SOURCE',
  'LISTING ID',
  'FAVORITE',
  'INTERESTED',
  'LATITUDE',
  'LONGITUDE',
  'transit_time',
  'transit_transfers',
  'transit_start_time']
 
def namespace(tree):
    root = tree.getroot()
    m = re.match('\{.*\}', root.tag)
    return m.group(0) if m else ''
    
def text_from_node(name, tree):
    search_string = ".//" + namespace(tree) + name
    l.debug("Searching for " + search_string)
    results = tree.findall(search_string)
    l.debug("Found: " + str(results))
    if len(results) == 0:
        return ""
    else:
        return results[0].text
 
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
    return results
    
def main():
    reader = csv.DictReader(open('redfin_2016-10-18-18-06-09_results.csv'))
    writer = csv.DictWriter(open('redfin_2016-10-18-18-06-09_with_transit_times.csv', 'w', newline=''), FIELDS)
    writer.writeheader()
    
    for row in reader:
        xml = ET.ElementTree(ET.fromstring(api_results_from(row['LATITUDE'], row['LONGITUDE'], 'T')))
        # Noisy: l.debug("Tags: " + '\n'.join(map(lambda x: str(x), xml.findall(".//*"))))
        new_columns = {'transit_time': text_from_node('duration', xml),
                       'transit_transfers': text_from_node('numberOfTransfers', xml),
                       'transit_start_time': text_from_node('startTime', xml)}
        new_row = row.copy()
        new_row.update(new_columns)
        trash_keys = new_row.keys() - FIELDS
        l.info("Deleting fields: " + str(trash_keys))
        for key in trash_keys:
            del(new_row[key])
        writer.writerow(new_row)
        #exit()
        
if __name__ == '__main__':
    main()