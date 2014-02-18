import urllib
from BeautifulSoup import BeautifulSoup
import os
import itertools

raw_search_results = open("3and4bldg_results.html.partial")
baseurl = "http://apps.ci.minneapolis.mn.us/PIApp"
section_url = {
    "valuation":"ValuationRpt.aspx?pid=",
    "inspection":"InspectionPermitsRpt.aspx?Year=All&Action=Show&PID=",
    "tish":"TishRpt.aspx?pid=",
    "assessments":"SpecialAssessmentsRpt.aspx?Year=All&Action=Show&PID="
}

def init_page(path="index.html"):
    f = open(path, "w")
    f.write("<html><body>\n")
    return f

def local_path_from_apn(apn):
    return apn + ".html"

def insert_link_in_index(index_file, apn, address):
    print "Linking into index: " + apn
    index_file.write('<li><a href="' + local_path_from_apn(apn) + '">' + address + '</a></li>\n')

def write_page_and_close(page):
    page.write("</html></body>\n")
    page.close()

def insert_google_streetview_image(page, street_address):
    page.write("""<img src="http://maps.googleapis.com/maps/api/streetview?size=800x600&location=""")
    page.write(urllib.quote_plus(street_address))
    page.write("""&sensor=false&key=""" + open("apikey").readlines()[0].strip() + """" />\n""") 

def collect_specifics_at_apn(apn, address):
    print "Building page for property ID " + apn + ": " + address
    apn_page = init_page(local_path_from_apn(apn))

    # Street View image at the top.
    insert_google_streetview_image(apn_page, address)

    # Table soup objects to append to the body of the index page.
    tables = []
    for url in map(lambda postfix: baseurl + "/" + postfix + apn, section_url.values()):
        section_soup = BeautifulSoup(urllib.urlopen(url))
        try:
            tables = section_soup.first("div", {"id":"content"}).findAll("table")
        except AttributeError:
            print """Couldn't find <div id="content"> at url """ + url
            print "Exiting..."
            exit(-1)
        for t in tables:
            apn_page.write(str(t))

    write_page_and_close(apn_page)

def apns_and_addresses_from_local_cache(cache_path="3and4bldg_results.html.partial"):
    apns = []
    addresses = []
    results_soup = BeautifulSoup(open(cache_path).read())
    
    for t in results_soup.findAll("table", {"id":"maddress"}):
        address_contents = map(lambda span_tags: str(span_tags.contents[0]), t.td.findAll("span"))
        street_address = " ".join(address_contents)
        city_state_zip = str(t.td.contents[-1]).strip()
        addresses.append(" ".join([street_address, city_state_zip]))

        apns.append(str(t.tr.findAll("th")[1].b.contents[0]))

    return itertools.izip(apns, addresses)
    
def main():
    index = init_page()

    # Links in the main index are in a numbered list.
    index.write("<ol>\n")

    for apn, addr in apns_and_addresses_from_local_cache():
        collect_specifics_at_apn(apn, addr)
        insert_link_in_index(index, apn, addr)

    index.write("</ol>\n")
    write_page_and_close(index)

if __name__ == "__main__":
    main()
