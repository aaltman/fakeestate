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

def insert_link_in_index(index_file, apn):
    print "Linking into index: " + apn
    index_file.write('<li><a href="' + local_path_from_apn(apn) + '">' + apn + '</a></li>\n')

def write_page_and_close(index_file):
    index_file.write("</html></body>\n")
    close(index_page_file)

def insert_google_streetview_image(page, street_address):
    pass # FIXME implement

def collect_specifics_at_apn(apn, address):
    print "Building page for property ID " + apn + ": " + addr
    apn_page = init_page(local_path_from_apn(apn))

    # Street View image at the top.
    insert_google_streetview_image(apn_page, address)

    # Table soup objects to append to the body of the index page.
    tables = []
    for url in map(lambda postfix: baseurl + postfix, section_url.values()):
        section_soup = BeautifulSoup(urllib.urlopen(url))
        tables = section_soup.first("div", {"id":"content"}).findAll("table")
        for t in tables:
            apn_page.write(str(t))

    write_page_and_close(apn_page)

def apns_and_addresses_from_local_cache(cache_path="3and4bldg_results.html.partial"):
    apns = []
    addresses = []
    results_soup = BeautifulSoup(open(cache_path).read())
    
    for t in results_soup.findAll("table", {"id":"maddress"}):
        street_address = " ".join(map(lambda span_tags: span_tags.contents, t.td.findAll("span")))
        city_state_zip = t.td.contents.split("</span>")[:-1]
        addresses.append(" ".join([street_address, city_state_zip]))

        apns.append(t.tr.findAll("th")[1].b.contents)

    return itertools.izip(apns, addresses)
    
def main():
    index = init_page()

    # Links in the main index are in a numbered list.
    index.write("<ol>\n")

    for apn, addr in apns_and_addresses_from_local_cache():
        collect_specifics_at_apn(apn, addr)
        insert_link_in_index(index, apn)
        # FIXME TESTING
        index.close()
        exit(-1)

    index.write("</ol>\n")
    write_page_and_close(index)

if __name__ == "__main__":
    main()
