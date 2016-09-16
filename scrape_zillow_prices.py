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

API_PREFIX = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm?'

FIELDS = ['asking_price',
 'mls_id',
 'home_size',
 'property_size',
 'bedrooms',
 'bathrooms',
 'tax_value',
 'tax_year',
 'last_sold_price',
 'last_sold_date',
 'year_built',
 'zillow_id',
 'home_detail_link',
 'formatted_address',
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
  
def scrape_asking_price(address):
    address = address.split(", USA")[0]
    l.debug("Attempting to scrape price for address %s (%s)" % (address, str(type(address))))
    #urllib.parse.urlencode({'': address}) + \
    
    url = "http://www.zillow.com/homes/for_sale/-" + \
      address.replace(' ', '-') + \
      "_rb/?fromHomePage=true&shouldFireSellPageImplicitClaimGA=false&fromHomePageTab=buy"
    l.debug("Retrieveing URL: %s" % url)
    contents = urllib.request.urlopen(url).read().decode("utf-8", "strict")
    # Noisy: l.debug("Contents: \n%s" % contents)
    
    mls_re = re.compile(' MLS #([0-9]*)  ')
    try:
        mls_match = mls_re.search(contents)
        l.debug("MLS ID# regex matches: %s" % str(mls_match.groups()))
        mls_id = mls_match.groups()[0]
    except AttributeError:
        l.debug("Couldn't find MLS ID in Zillow listing.  Leaving blank.")
        mls_id = ''
    
    price_re = re.compile('itemprop="price" content="\$(.*?)"')
    try:
        price_match = price_re.search(contents)
        l.debug("Price regex matches: %s" % str(price_match.groups()))
        price = price_match.groups()[0]
    except AttributeError:
        l.debug("Couldn't find asking price in Zillow listing.  Leaving blank.")
        price = ''
    
    return {'mls_id': mls_id, 'asking_price': price}
    
def main():
    reader = csv.DictReader(open('full_addresses_with_zillow_info.csv'))
    writer = csv.DictWriter(open('info_with_prices.csv', 'w', newline=''), FIELDS)
    writer.writeheader()
    
    for row in reader:
        price_and_mls_id = scrape_asking_price(row['formatted_address'])
        l.info("Got asking price %s for address %s." % (str(price_and_mls_id), row['formatted_address']))
        new_row = row.copy()
        new_row.update(price_and_mls_id)
        l.debug("Writing row: %s" % str(new_row))
        writer.writerow(new_row)
        
if __name__ == '__main__':
    main()