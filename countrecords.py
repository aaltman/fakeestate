import cProfile
import urllib
import sys
from dbfpy import dbf
from BeautifulSoup import BeautifulSoup
import datetime
import time

recs = []
# Go straight to the structure information page for a given APN.
minneapolis_webquery_url_prefix = "http://apps.ci.minneapolis.mn.us/PIApp/StructureInformationRpt.aspx?PID="

def record_is_interesting(rec):
    return rec['city'] == 'MINNEAPOLIS' and \
        ('partment' in rec['use1_desc'] or 'riplex' in ['use1_desc']) and \
        'Address' not in rec['streetname'] and \
        'State of' not in rec['owner_name'] and \
        rec['tax_exempt'] == 'N' 

def building_is_interesting(bldg_soup):
    # Example page: http://apps.ci.minneapolis.mn.us/PIApp/StructureInformationRpt.aspx?Structure=92393&Action=Show&PID=2702924430113
    # If there are 3 or 4 registered dwellings or reference dwellings, we're interested.
    # The HTML elements describing this are the first and 2nd and 4th TDs in the document.
    dwellings_table = bldg_soup.first('table', {'class':'rtable'})
    if dwellings_table is None:
        return False
    try:
        dwelling_elements = dwellings_table.findAll("td")
        dwelling_elements = list(dwelling_elements[i] for i in [1, 3])
    # If there were no tds, return.
    except IndexError:
        return False
    for d in dwelling_elements:
        num_dwellings = d.contents[0]
        if num_dwellings == '3' or num_dwellings == "4":
            print "Found 3 or 4 dwelling building!"
            return True
    return False

def write_building_if_interesting(bldg_soup, outfile=sys.stdout):
    if building_is_interesting(bldg_soup):
        outfile.write(str(bldg_soup))

def write_interesting_buildings_at_apn(apn, outfile=sys.stdout):
    # Use the APN to get a tag soup out of the city of Mpls website.
    soup = BeautifulSoup(urllib.urlopen(minneapolis_webquery_url_prefix + apn).read())

    # There's a div with the id "multilist" that contains the list of properties.
    multilist_div = soup.first('div', {'id':'multilist'})

    if multilist_div:
        building_list = multilist_div.ul.findAll("a")
        if building_list:
            print "APN " + str(apn) + " contains building list tags: " + str(building_list)
            for bldg_link in building_list:
                # Snip the trailing "?PID=" off of the base url with [:-5].
                url = minneapolis_webquery_url_prefix[:-5] + bldg_link['href']
                print "Retrieving building URL " + str(url)
                bldg_soup = BeautifulSoup(urllib.urlopen(url))
                write_building_if_interesting(bldg_soup, outfile)

#@profile
def get_all_possible_3and4unit_buildings_by_parcel(outfile=sys.stdout, starting_entry="0202824110278"):
    start_time = datetime.datetime.now()
    count = 0
    found_start = False # Skip until starting_entry is found

    db = dbf.Dbf("/home/altie/grassdata/realestategis/Parcels2010Hennepin.dbf")
    for rec in db:
        # Get the property number out of the database in a way that can be used as an active parcel number (APN).
        apn = rec['pin'].split("-")[1]

        #if (not found_start) and (apn == starting_entry):
        #    print "Starting search after " + starting_entry
        #    found_start = True
        #elif not found_start:
        #    print "Skipping " + apn
        #    continue 
        #elif record_is_interesting(rec):
        if record_is_interesting(rec):
            elapsed = datetime.datetime.now() - start_time
            print str(elapsed) + ": Attempt " + str(count) + ": "
            print "Found candidate APN " + str(apn) + ", address " + rec['bldg_num'] + " " + rec['streetname'] + ", sale price (if any) " + str(rec['sale_value'])
            count += 1
            write_interesting_buildings_at_apn(apn, outfile)

def count_triplexes():
    db = dbf.Dbf("/home/altie/grassdata/realestategis/Parcels2010Hennepin.dbf")
    props = []
    for rec in db:
        use1_desc = rec['use1_desc']
        if use1_desc.strip() == 'Triplex':
            props.append(rec)
    for tri in props:  print str(tri)
    print "Found " + str(len(props)) + " triplexes: " 

def example_fourplex_info():
    write_interesting_buildings_at_apn('2602924330013', open("test.txt", "w"))

if __name__ == '__main__':
    #cProfile.run("get_all_possible_3and4unit_buildings_by_parcel()")
    get_all_possible_3and4unit_buildings_by_parcel(open("3and4bldg_results.html.partial", "w"))
    #count_triplexes()
    #example_fourplex_info()
