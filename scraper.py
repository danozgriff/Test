import scraperwiki
import mechanize
import re
import csv
#import sqlite3

url = 'http://shareprices.com/ftseallshare'


    #print str(asxlist["data"][x])[3:-2]

#for x in asxlist:
#    print asxlist

#data = scraperwiki.scrape("http://www.asx.com.au/asx/research/ASXListedCompanies.csv")
#url2 = 'https://www.aussiebulls.com/SignalPage.aspx?lang=en&Ticker=WOW.AX'
    br = mechanize.Browser()

    # sometimes the server is sensitive to this information
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

#####reader = csv.DictReader(data.splitlines()[2:10])

#scraperwiki.sqlite.execute("alter table companies add `Date Added` date")
#scraperwiki.sqlite.execute("alter table companies rename to company")
#scraperwiki.sqlite.execute("alter table company rename column `Date Added` to `Last Refreshed`")
#scraperwiki.sqlite.execute("alter table company add `Top 500` char(1)")

#scraperwiki.sqlite.execute("drop table if exists company")  
#scraperwiki.sqlite.execute("create table company (`GICS industry group` string, `ASX code` string, `Company name` string, `Last Refreshed` date, `Top 500` char(1))")
#scraperwiki.sqlite.execute("drop table if exists Signal_History")  
#scraperwiki.sqlite.execute("create table Signal_History (`ASX code` varchar2(8) NOT NULL, `Date` date NOT NULL, `Price` real NOT NULL, `Signal` varchar2(15) NOT NULL, `Confirmation` char(1) NOT NULL, `AUD 100` real NOT NULL, UNIQUE (`ASX code`, `Date`))")

#scraperwiki.sqlite.execute("insert into company values ('test', 'test', 'test', date('2015-12-07'), 'Y')")
#scraperwiki.sqlite.execute("delete from company where `ASX code` = 'test'")


#scraperwiki.sqlite.commit()

#@@@scraperwiki.sqlite.save(['GICS industry group', 'ASX code', 'Company name'], list(csv.DictReader(scraperwiki.scrape('http://www.asx.com.au/asx/research/ASXListedCompanies.csv').splitlines()[2:])), table_name='company')
#scraperwiki.sqlite.save(['industry', 'code', 'company'], list(csv.DictReader(scraperwiki.scrape('http://www.asx.com.au/asx/research/ASXListedCompanies.csv').splitlines()[2:10])), table_name="companies")

#@@@scraperwiki.sqlite.execute("update company set `Last Refreshed` = date('now') where `Last Refreshed` is null")

#@@@scraperwiki.sqlite.execute("update company set `Top 500` = 'Y' where `Last Refreshed` = date('now')")
#@@@scraperwiki.sqlite.execute("update company set `Top 500` = 'N' where `Last Refreshed` <> date('now')")


#scraperwiki.sqlite.commit()
#scraperwiki.sqlite.execute(".schema companies")
#scraperwiki.sqlite.execute("select * from company") 

#####for record in reader:
#####        print record

    response = br.open(url)

    for pagenum in range(1):
        html = response.read()
    
#comp = re.search(r'MainContent_CompanyTicker(\w{3,}\.AX)span', html).group(0)
#ASX_Code = '3PL.AX'
  
#print re.findall(r'MainContent_signalpagehistory_PatternHistory24((.)+)\<\\table\>', html) 
        test1 = re.search(r'Day\'s Volume(.*?)>(.*?)<(.*?)endcol', html)
        print test1

 #       if test1:
   #         test1 = test1.group(0)
    

# test2 = re.findall(r'(\"\>|img\/)((.)+)\<\/td\>\<td', test1)
#test2 = re.findall('\">(.*)<\/', test1)
#test2 = re.findall('\">(.*?)<\/', test1)
#test2 re.search(r'\"\>(.*)\<\/?', test1)
#test2 = re.findall('\">(.*?)<\/', test1) GOOD
#test2 = re.findall('(\">|img\/)(.*?)(<\/|\.gif)', test1) BETTER

#test2 = re.findall('(\">|img\/)(.*?)(<\/|\.gif)', test1.replace("\B", ""))

#test3 = re.findall('\', \'(.*?)\', \'', test2)
     #       test3 = re.findall('(\">|img\/)(.*?)(<\/|\.gif)', test1.replace("\B", ""))
#print "".join(test3[0].split)
#test4 = [x.replace(" ", "") for x in test3]



#print re.search(r"\',\'(.*)\',\'", str(test3[0]).replace(" ", "")).group(0)
#print len(test3)
#print ""



 #           while len(test3) >= 5:
    
                #print ASX_Code
  #              sh_Date = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(" ", "")).group(0)
#
