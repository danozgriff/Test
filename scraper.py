import scraperwiki
import mechanize
import re
import csv
import time
from datetime import datetime, date
from time import gmtime, strftime
import datetime


##################################################      
#Load Prices from shareprices.com
##################################################
#

def ScrapeLivePrices():


    scraperwiki.sqlite.execute("delete from company1")  
    #scraperwiki.sqlite.execute("drop table if exists company")
    #scraperwiki.sqlite.execute("create table company (`TIDM` string, `Company` string, `Yesterday Price` real, `Volume` real, `FTSE` string, `Date` date NOT NULL)")

    now = datetime.datetime.now()
    ftseopen = now.replace(hour=8, minute=1, second=0, microsecond=0)
    if now >= ftseopen:
       daystarted = "Y"
    else:
       daystarted = "N" 

    ftses = ['FTSE 100', 'FTSE 250',  'FTSE Small Cap']
    
    for ftse in ftses:        # Second Example

        if ftse == 'FTSE 100':
            url = 'http://shareprices.com/ftse100'
        elif ftse == 'FTSE 250':
            url = 'http://shareprices.com/ftse250'
        elif ftse == 'FTSE Small Cap':
            url = 'http://shareprices.com/ftsesmallcap'
        
        br = mechanize.Browser()
        
            # sometimes the server is sensitive to this information
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        
        #scraperwiki.sqlite.execute("delete from company")
        #scraperwiki.sqlite.commit()
        
        response = br.open(url)
        
        
        for pagenum in range(1):
            html = response.read()
            test1 = re.search(r'Day\'s Volume(.*?)<br \/><\/div>', html).group()
            #tuples = re.findall(r'((\">|\'>)(.*?)<\/))', str(test1.replace(" ", "")).replace("><", ""))
            tuples = re.findall(r'(\">|\'>|img\/)(.*?)(<\/|\.gif)', str(test1.replace(" ", "")).replace("><", ""))
            count = 0
            tidm = ""
            company = ""
            price = 0
            change = 0
            poscnt = 0
            overallcnt = 0

            for tuple in tuples:
                if poscnt == 1:
                    company = tuple[1].replace("amp;", "")
                if poscnt == 2:
                    price = float(tuple[1].replace(",", "").replace("p", ""))
                if poscnt == 3:
                    change = float(tuple[1][:tuple[1].find("&")])
                    if tuple[1][-2:] == 'up':
                        change = change * -1
                if poscnt == 4:
                    if daystarted == "N":
                      scraperwiki.sqlite.save(["TIDM"], data={"TIDM":tidm+'.L', "Company":company, "Yesterday Price":round(price,2), "Volume":tuple[1].replace(",", ""), "FTSE":ftse, "Date":datetime.date.today()}, table_name='company1')
                    elif daystarted == "Y":
                      scraperwiki.sqlite.save(["TIDM"], data={"TIDM":tidm+'.L', "Company":company, "Yesterday Price":round(price+change,2), "Volume":tuple[1].replace(",", ""), "FTSE":ftse, "Date":datetime.date.today()}, table_name='company1')
                    scraperwiki.sqlite.commit()
                if len(tuple[1]) <= 4 and tuple[1][-1:].isalpha() and tuple[1][-1:].isupper() and tuple[1]!=tidm and poscnt!=1:
                    count = count+1
                    tidm = tuple[1]
                    poscnt = 1
                else:
                    poscnt = poscnt + 1    
             
            #if overallcnt > 9:
             #    return;
            print "%s ftse records were loaded" % (count)
    
    return;

####################################################
#Load Main Page from British Bulls
####################################################

def ScrapeBritishMain():

    url = 'https://www.britishbulls.com/Default.aspx?lang=en'
    
    
    #scraperwiki.sqlite.execute("drop table if exists Signal_History")  
    #scraperwiki.sqlite.execute("create table Company_Recommendations (`Date` date NOT NULL, `TIDM` varchar2(8) NOT NULL, `Signal` varchar2(15) NOT NULL, `Avg Price` real NOT NULL, `EOD Signal` varchar2(15) NOT NULL, `EOD Pattern` varchar2(30) NOT NULL, `EOD Last Price` real NOT NULL, `EOD %Change` real NOT NULL, `Refresh Date` date, UNIQUE (`Date`, `TIDM`))")
    
    
    #lselist = scraperwiki.sqlite.execute("select `TIDM` from company")
    
    #for x in lselist["data"]:
        
        #tidm = str(x)[3:-2]
        
        #siglist = scraperwiki.sqlite.execute("select count(*) from Signal_History where tidm = '%s' and (Signal IN ('SELL',  'SHORT',  'STAY IN CASH',  'STAY SHORT') OR (Signal IN ('BUY, 'STAY LONG') AND ))" % (tidm, d1date))

    br = mechanize.Browser()

    # sometimes the server is sensitive to this information
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    #response = br.open(url + tidm)
    response = br.open(url)

    for pagenum in range(1):
        html = response.read()

        publishdate = re.search(r'MARKET STATUS REPORT, (..........)', html).group(0)[22:]

        test1 = re.search(r'MainContent_SignalListGrid1_DXDataRow0((.|\n)+)MainContent_SignalListGrid1_IADD', html)

        if test1:
            test1 = test1.group(0)

            test3 = re.findall('(\">|img\/)(.*?)(<\/|\.gif)', test1.replace("\B", ""))

            while len(test3) >= 5:
    
                recdate = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(" ", "")).group(0)
                rectidm = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(" ", "").replace(",", "")).group(0)
                recsignal = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(" ", "").replace(",", "")).group(0)
                recavgprice = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(" ", "").replace(",", "")).group(0)
                eodsignal = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(",", "")).group(0)
                eodpattern = re.search(r'title="((.|\n)+)" src=', str(test3.pop(0))).group(0)[7:-6]
                eodprice = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(" ", "").replace(",", "")).group(0)
                eodchange = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(" ", "").replace(",", "")).group(0)
                
                scraperwiki.sqlite.execute("insert or ignore into Company_Recommendations values (?, ?, ?, ?, ?, ?, ?, ?, ?)",  [recdate, rectidm, recsignal, recavgprice, eodsignal, eodpattern, eodprice, eodchange, publishdate]) 
                scraperwiki.sqlite.commit()
                
    return;

####################################################
#Update Open Trades
####################################################

def UpdateOpenTrades():
    
    openlist = scraperwiki.sqlite.execute("select `TIDM`, `OpenPrice`, `OpenSignal`, `Direction` from Trades where Postion = 'Open'")
    
    for x in openlist["data"]:
        
        tidm = x[0]
        openprice = x[1]
        opensignal = x[2]
        direction = x[3]

        siglist = scraperwiki.sqlite.execute("select `TIDM`, `Signal` from Signal_History where tidm = '%s' and Date in (select max(`Date`) from Signal_History where tidm = '%s')" % (tidm, tidm))
        
        for y in siglist["data"]:
            currtidm = y[0]
            currsignal = y[1]
            
            currprices = scraperwiki.sqlite.execute("select `Price`, `Date` from Company where tidm = '%s'") % (tidm)
            
            for z in currprices["data"]:
                currprice = z[0]
                currdate = datetime.datetime.strptime(z[1], "%Y-%m-%d").date()
                
                if direction == 'LONG':
                    lastchange = round((currprice - openprice) / openprice,3)
                if direction == 'SHORT':
                    lastchange = round((openprice - currprice) / openprice,3)
                scraperwiki.sqlite.execute("update Trades set LastPrice = '%f', LastDate = '%s', LastChange = '%f', LastSignal = '%s' where tidm = '%s'") % (currprice, currdate, lastchange, currsignal, tidm)
                scraperwiki.sqlite.commit()
            
            if tidm==currtidm and opensignal!=currsignal:
                if (opensignal=='BUY' or opensignal=='STAY LONG') and (currsignal=='SELL' or currsignal=='STAY SHORT' or currsignal=='STAY SHORT' or currsignal=='STAY IN CASH'):
                    scraperwiki.sqlite.execute("update Trades set Position = 'Closing' where tidm = '%s'") % (tidm)
                    scraperwiki.sqlite.commit()
                elif (opensignal=='SELL' or opensignal=='STAY SHORT' or opensignal=='STAY SHORT' or opensignal=='STAY IN CASH') and (currsignal=='BUY' or currsignal=='STAY LONG'):
                    scraperwiki.sqlite.execute("update Trades set Position = 'Closing' where tidm = '%s'") % (tidm)
                    scraperwiki.sqlite.commit()
           
    return;

####################################################
#Find New Stocks
####################################################

def FindNewTrades():
    
    opencnt = scraperwiki.sqlite.execute("select count(*) from Trades where Postion = 'Closing'")
    for x in opencnt["data"]:
        closecnt = x[0]
    
    #recommlist = scraperwiki.sqlite.execute("select `TIDM` from Company_Recommendations
    
    return;
####################################################
#Load Signal History from British Bulls
####################################################

def ScrapeSignalHistory():

    url = 'https://www.britishbulls.com/SignalPage.aspx?lang=en&Ticker='
    
    
    #scraperwiki.sqlite.execute("drop table if exists Signal_History")  
    #scraperwiki.sqlite.execute("create table Signal_History (`TIDM` varchar2(8) NOT NULL, `Date` date NOT NULL, `Price` real NOT NULL, `Signal` varchar2(15) NOT NULL, `Confirmation` char(1) NOT NULL, `GBP 100` real NOT NULL, UNIQUE (`TIDM`, `Date`))")
    
    
    lselist = scraperwiki.sqlite.execute("select distinct `TIDM` from AllTrades")
    
    for x in lselist["data"]:
        
        tidm = str(x)[3:-2]
        
        ##siglist = scraperwiki.sqlite.execute("select count(*) from Signal_History where tidm = '%s' and (Signal IN ('SELL',  'SHORT',  'STAY IN CASH',  'STAY SHORT') OR (Signal IN ('BUY, 'STAY LONG') AND ))" % (tidm, d1date))

        br = mechanize.Browser()
    
        # sometimes the server is sensitive to this information
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

        response = br.open(url + tidm)
    
        for pagenum in range(1):
            html = response.read()

            test1 = re.search(r'MainContent_signalpagehistory_PatternHistory24_DXDataRow0((.|\n)+)MainContent_signalpagehistory_PatternHistory24_IADD', html)
    
            if test1:
                test1 = test1.group(0)

                test3 = re.findall('(\">|img\/)(.*?)(<\/|\.gif)', test1.replace("\B", ""))

                while len(test3) >= 5:
        
                    sh_Date = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(" ", "")).group(0)
                    sh_Date = date(int(sh_Date[6:10]),int(sh_Date[3:5]),int(sh_Date[:2]))
                    sh_Price = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(" ", "").replace(",", "")).group(0)
                    sh_Signal = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(" ", "")).group(0)
                    sh_Confirmation = ((re.search("[Uncheck|Check]", str(test3.pop(0)).replace(" ", "")).group(0).lower()).replace("u","N")).replace("c", "Y")
                    sh_GBP100 = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(" ", "").replace(",", "")).group(0)
                    
                    scraperwiki.sqlite.execute("insert or ignore into Signal_History values (?, ?, ?, ?, ?, ?)",  [tidm, sh_Date, sh_Price, sh_Signal, sh_Confirmation, sh_GBP100]) 
    
                    scraperwiki.sqlite.commit()
                    
    return;

########################################################
# Calculate Signal Performance
########################################################

def SignalPerformance(): 
        
   complist = scraperwiki.sqlite.execute("select `TIDM`, `Price`, `Date` from company where TIDM in (select distinct TIDM from Signal_History)")
   #complist = scraperwiki.sqlite.execute("select `TIDM`, `Price`, `Date` from company where tidm = 'FOUR.L'")

   scraperwiki.sqlite.execute("drop table if exists Company_Performance")  
   scraperwiki.sqlite.execute("create table Company_Performance (`TIDM` string, `3D` real, `10D` real, `30D` real, `90D` real, `180D` real, `Total` real, `Date` date)")

   for x in complist["data"]:
       tidm=x[0]
       #print tidm
       nprice=x[1]
       tdate=datetime.datetime.strptime(x[2], "%Y-%m-%d").date()
       todaydate=datetime.date.today()
       
       Commission=0.994

# Find Today GDP100

       ldata = scraperwiki.sqlite.execute("select `Price` from Signal_History where tidm = '%s' and Date = '%s'" % (tidm, tdate))
       if len(ldata["data"]) != 0:
           for c in d1mindate["data"]:
               tprice = c[0]
           
       else:
        
           ldata = scraperwiki.sqlite.execute("select `Date`, `GBP 100`, `Price`, `Signal` from Signal_History where tidm = '%s' and Date in (select max(`Date`) from Signal_History where tidm = '%s')" % (tidm, tidm))
           if len(ldata["data"]) == 0:
               tprice = 0
    
           else: 
               for b in ldata["data"]:
                   LatestGDP100 = b[1]
                   LatestPrice = b[2]
                   LatestSignal = b[3]
       
                   ldiff = (nprice - LatestPrice) / LatestPrice
           
                   if LatestSignal == 'BUY':
                       tprice = (LatestGDP100 + (LatestGDP100*ldiff))*Commission
                   elif LatestSignal == 'SHORT':
                       tprice = (LatestGDP100 + (LatestGDP100*(ldiff*-1)))*Commission
                   #SELL etc
                   else:
                       tprice = LatestGDP100*.994
               #print "Latest: %s: $%s" % (tdate, round(tprice,2))


#Calculate Performance for the various intervals   
#-----------------------------------------------

       timeintervals = [3, 10, 30, 90, 180];
       
       for timeint in timeintervals:
       
          #print "Starting interval: %d" , (timeint)
           d1date=todaydate - datetime.timedelta(days=timeint)
    
           d1list = scraperwiki.sqlite.execute("select `GBP 100` from Signal_History where tidm = '%s' and Date = '%s'" % (tidm, d1date))
           
           if len(d1list["data"]) != 0:
               for a in d1list["data"]: 
                   CalcPrice = a[0]
    
           else:        
               d1mindate = scraperwiki.sqlite.execute("select `Date`, `GBP 100` from Signal_History where tidm = '%s' and Date in (select max(`Date`) from Signal_History where tidm = '%s' and Date < '%s')" % (tidm, tidm, d1date))
               
               if len(d1mindate["data"]) == 0:
                   #MinDate = '1900-01-01' #datetime.datetime.strptime(y[0], "%Y-%m-%d").date()
                   MinDate = datetime.datetime.strptime('1900-01-01', "%Y-%m-%d").date()
                   MinPrice = 0.0
               else: 
                   for y in d1mindate["data"]:
                        MinDate = datetime.datetime.strptime(y[0], "%Y-%m-%d").date()
                        MinPrice = y[1]
               
                   d1maxdate = scraperwiki.sqlite.execute("select `Date`, `GBP 100` from Signal_History where tidm = '%s' and Date in (select min(`Date`) from Signal_History where tidm = '%s' and Date > '%s')" % (tidm, tidm, d1date))
                   
                   if len(d1maxdate["data"]) == 0:
                       MaxDate=tdate
                       MaxPrice=tprice
                   else:
                       for z in d1maxdate["data"]:
                            MaxDate = datetime.datetime.strptime(z[0], "%Y-%m-%d").date()
                            MaxPrice = z[1]
               Abovedelta = MaxDate - d1date
               Belowdelta = d1date - MinDate
               
               MinMaxDelta = MaxDate - MinDate
               PriceDelta = MaxPrice - MinPrice
               if PriceDelta == 0:
                   PriceInterval=0
               else:
                   PriceInterval = PriceDelta / MinMaxDelta.days
               
               if abs(Abovedelta.days) >= Belowdelta.days:
                   CalcPrice = MinPrice+Belowdelta.days*PriceInterval
               else:
                   CalcPrice = MaxPrice-Abovedelta.days*PriceInterval
                   
           D1PC = (tprice - CalcPrice) / CalcPrice
               
           if timeint == 3:
               T3D = round(D1PC,3)
           elif timeint == 10:
               T10D = round(D1PC,3)
           elif timeint == 30:
               T30D = round(D1PC,3)
           elif timeint == 90:
               T90D = round(D1PC,3)               
           elif timeint == 180:
               T180D = round(D1PC,3)
               total = T3D + T10D + T30D + T90D + T180D
               scraperwiki.sqlite.execute("insert into Company_Performance values (?, ?, ?, ?, ?, ?, ?, ?)",  [tidm, T3D, T10D, T30D, T90D, T180D, total, tdate]) 
               scraperwiki.sqlite.commit()
       return;     


########################################################
# MAIN
########################################################
if __name__ == '__main__':
    
    #ScrapeBritishMain()
    #NewLivePrices()
    ScrapeLivePrices()
    #SignalPerformance()

    #print strftime("%Y-%m-%d %H:%M:%S", gmtime())


