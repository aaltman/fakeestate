import cProfile
import urllib
import sys
from dbfpy import dbf
from BeautifulSoup import BeautifulSoup

recs = []
#minneapolis_webquery_url_prefix = "http://apps.ci.minneapolis.mn.us/PIApp/GeneralInfoRpt.aspx?PID="
minneapolis_webquery_url_prefix = "http://apps.ci.minneapolis.mn.us/PIApp/StructureInformationRpt.aspx?PID="

def record_is_interesting(rec):
    return rec['city'] == 'MINNEAPOLIS' and \
        'esidential' in rec['use1_desc'] and \
        'Address' not in rec['streetname'] and \
        'State of' not in rec['owner_name'] and \
        rec['tax_exempt'] == 'N' 

#@profile
def countrecords():
    count = 0
    db = dbf.Dbf("/home/altie/grassdata/realestategis/Parcels2010Hennepin.dbf")
    for rec in db:
        #print "tax_exempt = " + str(rec['tax_exempt']) + " num_units = " + str(rec['num_units'])
        if record_is_interesting(rec):
            # Get the property number out of the database in a way that can be used as an active parcel number (APN).
            apn = rec['pin'].split("-")[1]
            print "Found candidate APN " + str(apn) + ", address " + rec['bldg_num'] + " " + rec['streetname'] + ", sale price (if any) " + str(rec['sale_value'])
            apn = "1702824440141"

            # Use the APN to get a tag soup out of the city of Mpls website.
            soup = BeautifulSoup(urllib.urlopen(minneapolis_webquery_url_prefix + apn).read())

            # There's a div with the id "multilist" that contains the list of properties.
            multilist_div = soup.first('div', {'id':'multilist'})

            if multilist_div:
                building_list = multilist_div.ul.li.a
                if building_list:
                    print "Found building list tags: " + str(building_list)
                    structure_soup = BeautifulSoup(urllib.urlopen(minneapolis_webquery_url_prefix + apn + building_list["href"]))
                    print str(structure_soup)
                    count += 1

            exit() # FIXME testing

    print "Found " + str(count) + " matching records."

if __name__ == '__main__':
    #cProfile.run("countrecords()")
    countrecords()
    #print str(rec[0])
