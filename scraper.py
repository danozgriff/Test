import scraperwiki           
import lxml.html
html = scraperwiki.scrape("http://shareprices.com/ftseallshare")
root = lxml.html.fromstring(html)
