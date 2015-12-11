import scraperwiki           
import lxml.html
html = scraperwiki.scrape("http://shareprices.com/ftseallshare")
root = lxml.html.fromstring(html)
for el in root.cssselect("div.featured a"):           
    print el
