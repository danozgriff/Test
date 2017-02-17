import scraperwiki
import mechanize
import re
import csv
import time
from datetime import datetime, date, timedelta
from time import gmtime, strftime
from math import sqrt
import datetime, base64
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import random


##################################################      
#Load Prices from shareprices.com
##################################################
#

def ScrapeLivePrices(rerunflag):

    #Sleep the process while day is still open
    #time.sleep(sleeptime)
    
    scraperwiki.sqlite.execute("delete from company")  
    #scraperwiki.sqlite.execute("drop table if exists company")
    #scraperwiki.sqlite.execute("create table company (`TIDM` string, `Company` string, `Yesterday Price` real, `FTSE` string, `Date` date NOT NULL)")

    todaydate=datetime.date.today()
    todaydate=todaydate.strftime("%Y-%m-%d") 
    
    datecheck = scraperwiki.sqlite.execute("select max(`Date`) from company")
    
    for x in datecheck["data"]:
       if x[0] == None:
         tdate = datetime.date.today() - datetime.timedelta(days=1)
         tdate = tdate.strftime("%Y-%m-%d")
       else:
         tdate=datetime.datetime.strptime(x[0], "%Y-%m-%d")
         tdate=tdate.strftime("%Y-%m-%d") 

    if todaydate > tdate:
             
      now = datetime.datetime.utcnow()
      #print now
      ftseopen = now.replace(hour=8, minute=1, second=0, microsecond=0)
      ftseclosed = now.replace(hour=16, minute=31, second=0, microsecond=0)
      timetilclose = (ftseclosed - now).seconds + 5
    
      if rerunflag == 1:
        time.sleep(timetilclose + 5)
        rerunflag = 0
      
      if now >= ftseopen and now <= ftseclosed:
         tradingopen = "Y"
         rerunflag = 1
         #print "ftse open"
      else:
         #print "ftse closed"
         tradingopen = "N"
         rerunflag = 0

      ftses = ['FTSE 100', 'FTSE 250',  'FTSE Small Cap']
    
      for ftse in ftses:        

          if ftse == 'FTSE 100':
              url = 'http://shareprices.com/ftse100'
          elif ftse == 'FTSE 250':
              url = 'http://shareprices.com/ftse250'
          elif ftse == 'FTSE Small Cap':
              url = 'http://shareprices.com/ftsesmallcap'
        
          br = mechanize.Browser()
          br.set_handle_robots(False)
        
            # sometimes the server is sensitive to this information
          br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        
          #scraperwiki.sqlite.execute("delete from company")
          #scraperwiki.sqlite.commit()
        
          response = br.open(url, timeout=120.0)
        
        
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
                      change = float(tuple[1][:tuple[1].find("&")].replace(",", ""))
                      if tuple[1][-2:] == 'up':
                          change = change * -1
                  if poscnt == 4:
                      if tradingopen == "Y":
                          "Trading Started"
                          price = price+change
                          #if tidm == "3IN":
                            #print change
                            #print price
                            #print price+change
                          
                      #+timedelta(days=-1)
                      #"Volume":tuple[1].replace(",", "")
                      scraperwiki.sqlite.execute("insert into Company values (?, ?, ?, ?, ?)",  [tidm+'.L', company, round(price,2), ftse, datetime.date.today()]) 
                      #scraperwiki.sqlite.save(["TIDM", "Date"], data={"TIDM":tidm+'.L', "Company":company, "Yesterday Price":round(price,2), "FTSE":ftse, "Date":datetime.date.today()-timedelta(days=-1)}, table_name='company')
                      scraperwiki.sqlite.commit()
                  if len(tuple[1]) <= 4 and tuple[1][-1:].isalpha() and tuple[1][-1:].isupper() and tuple[1]!=tidm and poscnt!=1:
                      count = count+1
                      tidm = tuple[1]
                      poscnt = 1
                  else:
                      poscnt = poscnt + 1    
             
              #if overallcnt > 9:
               #    return;
              #print "%s ftse records were loaded" % (count)
    
    return rerunflag;

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
                
                #scraperwiki.sqlite.execute("insert or ignore into Company_Recommendations values (?, ?, ?, ?, ?, ?, ?, ?, ?)",  [recdate, rectidm, recsignal, recavgprice, eodsignal, eodpattern, eodprice, eodchange, publishdate]) 
                #scraperwiki.sqlite.commit()

                #scraperwiki.sqlite.execute("drop table if exists trades")

    

                #scraperwiki.sqlite.execute("create table trades (`TIDM` string, `OpenDate` date, `OpenSignal` string, `OpenPrice` real, `Direction` string, `LastPrice` real, `LastDate` date, `LastChange` real, `LastSignal` string, `Position` string)")
                scraperwiki.sqlite.execute("insert or ignore into Trades values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",  [rectidm, publishdate, eodsignal, eodprice, recsignal, eodprice, publishdate, eodchange, eodsignal, 'Open']) 
                scraperwiki.sqlite.commit()
                
    return;

def gvars():

    global cGFzc3dvcmQ, cGFdc2evcmQ, cGFyc3vdcmF, cPFyc4dvcvF

    cGFzc3dvcmQ = base64.b64decode("ZnRzZXBhc3M=")
    cGFdc2evcmQ = base64.b64decode("c210cC5nbWFpbC5jb20=")
    cGFyc3vdcmF = base64.b64decode("ZGFub3pncmlmZkBnbWFpbC5jb20=")
    cPFyc4dvcvF = base64.b64decode("ZGFuZS5ncmlmZkBnbWFpbC5jb20=")

    return;

####################################################
#Update Open Trades
####################################################

def UpdateOpenTrades():

    #scraperwiki.sqlite.execute("delete from trades")  
    #scraperwiki.sqlite.execute("drop table if exists trades")
    #scraperwiki.sqlite.execute("create table trades (`TIDM` string, `OpenDate` date, `OpenSignal` string, `OpenPrice` real, `Stake` string, `LastPrice` real, `LastDate` date, `LastChange` real, `LastSignal` string, `Position` string, `CloseDate` Date, `CloseSignal` string, `ClosePrice` real, `Earnings` real) UNIQUE (`TIDM`, `OpenDate`) ON CONFLICT IGNORE")
    
    lastchange = None

    openlist = scraperwiki.sqlite.execute("select `TIDM`, `OpenDate`, `OpenPrice`, `OpenSignal` from Trades where CloseDate is null")
    
    for x in openlist["data"]:
        
        tidm = x[0]
        opendate = datetime.datetime.strptime(x[1], "%d/%m/%y").date()
        openprice = x[2]
        opensignal = x[3]

        #print "tidm: %s open price %f open signal: %s" % (tidm, openprice, opensignal)
        #print "tidm length: %d" % len(tidm)

        siglist = scraperwiki.sqlite.execute("select `TIDM`, `Date`, `Signal` from Signal_History where tidm = '%s' and Date in (select max(`Date`) from Signal_History where tidm = '%s')" % (tidm, tidm))
        
        for y in siglist["data"]:
            currtidm = y[0]
            currsignaldate = datetime.datetime.strptime(y[1], "%Y-%m-%d").date()
            currsignal = y[2]

            #if currdate > opendate: 

        #print "tidm: %s current date: %s current signal: %s" % (currtidm, currsignaldate, currsignal)
       
        currprices = scraperwiki.sqlite.execute("select `Yesterday Price`, `Date` from Company where tidm = '%s'" % (tidm))
        
        for z in currprices["data"]:
            currprice = z[0]
            currdate = datetime.datetime.strptime(z[1], "%Y-%m-%d").date()
            
        if (opensignal=='BUY' or opensignal=='STAY LONG'): #and (currsignal=='SELL' or opensignal=='SHORT' or currsignal=='STAY SHORT' or currsignal=='STAY SHORT' or currsignal=='STAY IN CASH'):
          lastchange = round((currprice - openprice) / openprice,3)
        #elif (opensignal=='SELL' or opensignal=='SHORT' or opensignal=='STAY SHORT' or opensignal=='STAY SHORT' or opensignal=='STAY IN CASH') and (currsignal=='BUY' or currsignal=='STAY LONG'):
        else:  
          lastchange = round((openprice - currprice) / openprice,3)
        
        if currsignaldate <= opendate:
          scraperwiki.sqlite.execute("update Trades set LastPrice = '%f', LastDate = '%s', LastChange = '%f' where tidm = '%s'" % (currprice, currdate, lastchange, tidm))
        else:
          scraperwiki.sqlite.execute("update Trades set LastPrice = '%f', LastDate = '%s', LastChange = '%f', LastSignal = '%s', LastSignalDate = '%s' where tidm = '%s'" % (currprice, currdate, lastchange, currsignal, currsignaldate, tidm))
          if tidm==currtidm and opensignal!=currsignal:
            scraperwiki.sqlite.execute("update Trades set Position = 'Closing' where tidm = '%s'" % (tidm))
        
        scraperwiki.sqlite.commit()

        currprice = None 
        currdate = None
        currsignal = None
        currsignaldate = None
    
            #elif direction=='SELL':
             #   scraperwiki.sqlite.execute("update Trades set Position = 'Closing' where tidm = '%s'") % (tidm)
            #    scraperwiki.sqlite.commit()
           
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

def ScrapeSignalHistory(runno):
    
    CoreSQL = "select distinct `TIDM` from Trades where CloseDate is null UNION select * from (select distinct `tidm` from Company_Performance where 6mthProfit_Rank < 150 and StdDev_Rank < 150 and SignalAccuracy >= .6 limit 20)"
    weekday = datetime.datetime.today().weekday()
    rundate = datetime.datetime.now().date()
    
    
    #Determine how much history to scan for, based on the day of week and the run number
    # 0=Monday, 6=Sunday
    if runno == 1:
        # May need to centralise this ranking logic somewhere
        lselist = scraperwiki.sqlite.execute(CoreSQL)
    elif runno == 2:
      if weekday == 0:
        lselist = scraperwiki.sqlite.execute("select distinct `tidm` from company where substr(tidm,1,1) in ('A', 'H', 'O') and tidm not in ('%s')" % (CoreSQL))
      elif weekday == 1:
        lselist = scraperwiki.sqlite.execute("select distinct `tidm` from company where substr(tidm,1,1) in ('B', 'I', 'P', 'W') and tidm not in ('%s')" % (CoreSQL))        
      elif weekday == 2:
        lselist = scraperwiki.sqlite.execute("select distinct `tidm` from company where substr(tidm,1,1) in ('C', 'J', 'L', 'Q', 'X') and tidm not in ('%s')" % (CoreSQL))  
      elif weekday == 3:
        lselist = scraperwiki.sqlite.execute("select distinct `tidm` from company where substr(tidm,1,1) in ('D', 'K', 'R', 'Y') and tidm not in ('%s')" % (CoreSQL))  
      elif weekday == 4:
        lselist = scraperwiki.sqlite.execute("select distinct `tidm` from company where substr(tidm,1,1) in ('E', 'S', 'Z') and tidm not in ('%s')" % (CoreSQL))  
      elif weekday == 5:
        lselist = scraperwiki.sqlite.execute("select distinct `tidm` from company where substr(tidm,1,1) in ('1', '2', '3', '4', '5', '6', '7', '8', '9', 'F', 'M', 'T') and tidm not in ('%s')" % (CoreSQL))  
      #Must be Sunday..
      else:
        lselist = scraperwiki.sqlite.execute("select distinct `tidm` from company where substr(tidm,1,1) in ('G', 'N', 'U', 'V') and tidm not in ('%s')" % (CoreSQL))  
        
        
    #scraperwiki.sqlite.execute("drop table if exists Signal_History")  
    #scraperwiki.sqlite.execute("create table Signal_History (`TIDM` varchar2(8) NOT NULL, `Date` date NOT NULL, `Price` real NOT NULL, `Signal` varchar2(15) NOT NULL, `Confirmation` char(1) NOT NULL, `GBP 100` real NOT NULL, `Last Updated` date NOT NULL,  UNIQUE (`TIDM`, `Date`))")
    
    url = 'https://www.britishbulls.com/SignalPage.aspx?lang=en&Ticker='
    #lselist = scraperwiki.sqlite.execute("select distinct `TIDM` from company")
    
    random.shuffle(lselist["data"])
    
    for x in lselist["data"]:
        
        tidm = str(x)[3:-2]
        
        ##siglist = scraperwiki.sqlite.execute("select count(*) from Signal_History where tidm = '%s' and (Signal IN ('SELL',  'SHORT',  'STAY IN CASH',  'STAY SHORT') OR (Signal IN ('BUY, 'STAY LONG') AND ))" % (tidm, d1date))

        br = mechanize.Browser()
    
        # sometimes the server is sensitive to this information
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

        #pause before calling the URL
        time.sleep(random.uniform(1.5, 12.5))

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
                    
                    scraperwiki.sqlite.execute("insert or ignore into Signal_History values (?, ?, ?, ?, ?, ?, ?)",  [tidm, sh_Date, sh_Price, sh_Signal, sh_Confirmation, sh_GBP100, rundate]) 
    
                    scraperwiki.sqlite.commit()
                    
    return;


########################################################
# Return Signal Accuracy
########################################################

 
def signal_accuracy(tidm):
    """Calculates the signal accuracy for Signal History from British Bulls"""

    complist = scraperwiki.sqlite.execute("select Sum(case `Confirmation` when 'Y' then 1 Else 0 end), Count(*) from Signal_History where tidm = '%s' LIMIT 10" % (tidm))
    
    #signalscore = 0

    for x in complist["data"]:
      signalscore = x[0]
      num_items = x[1]

    #for x in complist["data"]:
    #  if x[0] = 'Y' 
    #    signalscore = signalscore + 1;

    #num_items = len(complist["data"])

    #accuracy = signalscore / num_items
    accuracy = float(signalscore) / num_items

    if tidm == "III.L":
      print ("Accuracy: %f" % (accuracy))
      print ("SignalScore: %i" % (signalscore))
      print ("num_items: %i" % (num_items))

    return accuracy

########################################################
# Return Standard Deviation
########################################################

 
def standard_deviation(tidm):
    """Calculates the standard deviation for a list of numbers."""

    complist = scraperwiki.sqlite.execute("select `Price` from Signal_History where tidm = '%s'" % (tidm))
    
    lst = []

    for x in complist["data"]:
      lst.append(x[0])

    #print lst

    num_items = len(lst)
    mean = sum(lst) / num_items
    differences = [y - mean for y in lst]
    sq_differences = [d ** 2 for d in differences]
    ssd = sum(sq_differences)
 
    #print('This is SAMPLE standard deviation.')
    variance = ssd / (num_items - 1)
    sd = sqrt(variance)
    # You could `return sd` here.

    return sd
 
    #print('The mean of {} is {}.'.format(lst, mean))
    #print('The differences are {}.'.format(differences))
    #print('The sum of squared differences is {}.'.format(ssd))
    #print('The variance is {}.'.format(variance))
    #print('The standard deviation is {}.'.format(sd))
    #print('--------------------------')

########################################################
# Obtain User Input from Google Sheets
########################################################

def ScrapeUserInput():
  
  #scraperwiki.sqlite.execute("create table Trades (`TIDM` string, `3D` real, `10D` real, `30D` real, `90D` real, `180D` real, `6mthProfit` real, `6mthProfit_Rank` integer, `StdDev` real, `StdDev_Rank` integer, `SignalAccuracy` real, `SignalAccuracy_Rank` integer, `Overall_Score` integer, `Overall_Rank` integer, `Date` date) UNIQUE (col_name1, col_name2) ON CONFLICT IGNORE")

  #scraperwiki.sqlite.execute("drop table if exists trades")
  #scraperwiki.sqlite.execute("create table trades (`TXID` integer PRIMARY KEY, `TIDM` string, `OpenDate` date, `OpenSignal` string, `OpenPrice` real, `Stake` string, `LastDate` date, `LastPrice` real, `LastChange` real, `LastSignal` string, `LastSignalDate` date, `Position` string, `CloseDate` Date, `CloseSignal` string, `ClosePrice` real, `Earnings` real)")

  maxTXID = scraperwiki.sqlite.execute("select max(TXID) from trades")

  #for x in complist["data"]:
  #    signalscore = x[0]  

  br = mechanize.Browser()
  #br.set_handle_robots(False)
  br.set_handle_equiv(True)
        
  csvurl = 'http://drive.google.com/open?id=1HehMfkCV3uVEu4dgsVl1MTpZ891MGTTJaSNErxKIaiE'
        
    # sometimes the server is sensitive to this information
  br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 Safari/537.36')]
  response = br.open(csvurl, timeout=120.0)
        
        
  for pagenum in range(1):
    html = response.read()
    #test1 = re.search(r'content=\"Sheet1(.*?)\"><meta name=\"google\" content=\"notranslate\">', html).group()
    test1 = re.search(r'Earnings((.|\n)+)\"><meta name=\"google\"', html).group()
    test2 = test1.replace(". ", ".").replace("/ ", "/")
    #print test2
    test3 = re.findall(r'(.*?)\,', test2)

    test3.pop(0)

    cnt=1
    while len(test3) > 0:
      CloseDate=None
      CloseSignal=None
      ClosePrice=None
      Earnings=None
      while test3[0] != "":
        if cnt==1:
          txid=test3.pop(0)
        if cnt==2:
          tidm=test3.pop(0).strip()
        if cnt==3:
          OpenDate=test3.pop(0).strip()
        if cnt==4:
          OpenSignal=test3.pop(0).strip().upper()
        if cnt==5:
          OpenPrice=test3.pop(0)
        if cnt==6:
          Stake=test3.pop(0)
        if cnt==7:
          CloseDate=test3.pop(0).strip()
        if cnt==8:
          CloseSignal=test3.pop(0).strip().upper()
        if cnt==9:
          ClosePrice=test3.pop(0)  
        if cnt==10:
          Earnings=test3.pop(0)
        cnt+=1
      if txid > maxTXID:
        scraperwiki.sqlite.execute("insert or replace into trades values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",  [txid, tidm, OpenDate, OpenSignal, OpenPrice, Stake, None, None, None, None, None, None, CloseDate, CloseSignal, ClosePrice, Earnings])  
      
      test3.pop(0)
      cnt=1

    scraperwiki.sqlite.commit()
 
  return;

########################################################
# Calculate Signal Performance
########################################################

def SignalPerformance(): 
        
   complist = scraperwiki.sqlite.execute("select `TIDM`, `Yesterday Price`, `Date` from company where TIDM in (select distinct TIDM from Signal_History)")
   #complist = scraperwiki.sqlite.execute("select `TIDM`, `Yesterday Price`, `Date` from company where tidm = 'III.L'")

   scraperwiki.sqlite.execute("drop table if exists Company_Performance")   
   scraperwiki.sqlite.execute("create table Company_Performance (`TIDM` string, `3D` real, `10D` real, `30D` real, `90D` real, `180D` real, `6mthProfit` real, `6mthProfit_Rank` integer, `StdDev` real, `StdDev_Rank` integer, `SignalAccuracy` real, `SignalAccuracy_Rank` integer, `Overall_Score` integer, `Overall_Rank` integer, `Date` date)")

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

           #print "TimeInt: %i" , (timeint)
           #print "d1date: %d" , (d1date)
    
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

                        #print "MinDate: %d" , (MinDate)
                        #print "MinPrice: %f" , (MinPrice)
               
                   d1maxdate = scraperwiki.sqlite.execute("select `Date`, `GBP 100` from Signal_History where tidm = '%s' and Date in (select min(`Date`) from Signal_History where tidm = '%s' and Date > '%s')" % (tidm, tidm, d1date))
                   
                   if len(d1maxdate["data"]) == 0:
                       MaxDate=tdate
                       MaxPrice=tprice

                       #print "MaxDate: %d" , (MaxDate)
                       #print "MaxPrice: %f" , (MaxPrice)

                   else:
                       #print "in else"
                       #print "MaxDate: %d" , (MaxDate)
                       #print "d1date: %d" , (d1date)                       
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

           stddev = standard_deviation(tidm)
           sigacc = signal_accuracy(tidm)

           #print "MaxPrice: %f" , (MaxPrice)
           #print "MixPrice: %f" , (MinPrice)
           #print "PriceDelta: %f" , (PriceDelta)
               
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

               T180Earnings = ((tprice - CalcPrice)/CalcPrice+1)*100
               scraperwiki.sqlite.execute("insert into Company_Performance values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",  [tidm, round(T3D,3), round(T10D,3), round(T30D,3), round(T90D,3), round(T180D,3), round(T180Earnings,2), 0, round(stddev,3), 0, round(sigacc,3), 0, 0, 0, tdate]) 
               scraperwiki.sqlite.commit()
       #return;     


#Calculate Rankings
#-----------------------------------------------

       #Update StdDev Ranking
       scraperwiki.sqlite.execute("delete from tmptbl_rank")
       scraperwiki.sqlite.execute("INSERT into tmptbl_rank (TIDM, Rank) SELECT tidm, (SELECT COUNT()+1 FROM (SELECT DISTINCT StdDev FROM Company_Performance AS t WHERE StdDev < Company_Performance.StdDev)) AS Rank FROM Company_Performance" )
       scraperwiki.sqlite.execute("Update Company_Performance SET StdDev_Rank = (select rank from tmptbl_rank where tidm = Company_Performance.tidm)")

       #Update 6mthProfit_Rank Ranking
       scraperwiki.sqlite.execute("delete from tmptbl_rank")
       scraperwiki.sqlite.execute("INSERT into tmptbl_rank (TIDM, Rank) SELECT tidm, (SELECT COUNT()+1 FROM (SELECT DISTINCT `6mthProfit` FROM Company_Performance AS t WHERE `6mthProfit` > Company_Performance.`6mthProfit` order by `6mthProfit` desc )) AS Rank FROM Company_Performance" )
       scraperwiki.sqlite.execute("Update Company_Performance SET `6mthProfit_Rank` = (select rank from tmptbl_rank where tidm = Company_Performance.tidm)")

       #Update SignalAccuracy Ranking
       scraperwiki.sqlite.execute("delete from tmptbl_rank")
       scraperwiki.sqlite.execute("INSERT into tmptbl_rank (TIDM, Rank) SELECT tidm, (SELECT COUNT()+1 FROM (SELECT DISTINCT SignalAccuracy FROM Company_Performance AS t WHERE SignalAccuracy > Company_Performance.SignalAccuracy)) AS Rank FROM Company_Performance" )
       scraperwiki.sqlite.execute("Update Company_Performance SET SignalAccuracy_Rank = (select rank from tmptbl_rank where tidm = Company_Performance.tidm)")

       #Update Company_Performance Ranking
       scraperwiki.sqlite.execute("Update Company_Performance SET Overall_Score = StdDev_Rank * `6mthProfit_Rank` * SignalAccuracy_Rank")
       scraperwiki.sqlite.execute("delete from tmptbl_rank")
       scraperwiki.sqlite.execute("INSERT into tmptbl_rank (TIDM, Rank) SELECT tidm, (SELECT COUNT()+1 FROM (SELECT DISTINCT Overall_Score FROM Company_Performance AS t WHERE Overall_Score < Company_Performance.Overall_Score)) AS Rank FROM Company_Performance" )
       scraperwiki.sqlite.execute("Update Company_Performance SET Overall_Rank = (select rank from tmptbl_rank where tidm = Company_Performance.tidm)")
       scraperwiki.sqlite.commit()

#-----------------------------#
#-----------------------------#
def Notify(rerunflag):

    if rerunflag == 0:  
    
      openlist = scraperwiki.sqlite.execute("select TXID, TIDM, OpenDate, OpenSignal, OpenPrice, Stake, LastDate, LastPrice, LastChange, LastSignal, LastSignalDate, Position, CloseDate, CloseSignal, ClosePrice, Earnings from Trades where CloseDate is null")

      Performance_Out = " TXID     TIDM     OpenDate     OpenSignal     OpenPrice     Stake     LastDate     LastPrice     LastChange     LastSignal     LastSignalDate     Position     CloseDate     CloseSignal     ClosePrice     Earnings<br>"
      Performance_Out = Performance_Out + "-----------------------------------------------------------------------------------------------------------------------------<br>"

      for x in openlist["data"]:
         txid = x[0]
         tidm = x[1]
         opendate = x[2]
         opensignal = x[3]
         openprice = x[4]
         stake = x[5]
         lastdate = x[6]
         lastprice = x[7]
         lastchange = x[8]
         lastsignal = x[9]
         lastsignaldate = x[10]
         position = x[11]
         closedate = x[12]
         closesignal = x[13]
         closeprice = x[14]
         earnings = x[15]       
         Performance_Out = Performance_Out + '{:>6} {:>6} {:>6} {:>6} {:>6} {:>6} {:>6} {:>6} {:>6} {:>6} {:>6} {:>6} {:>6} {:>6} {:>6} {:>6}<br>'.format(txid, tidm, opendate, opensignal, openprice, stake, lastdate, lastprice, lastchange, lastsignal, lastsignaldate, position, closedate, closesignal, closeprice, earnings)
    
    #closecnt = scraperwiki.sqlite.execute("select count(*) from Trades where position = 'Closing'")
    
    #if closecnt > 0:
      
      Performance_Out = "<br><br>Please close off the required trades. Here are your options for new trades:<br><br>"
    
      # New Options
      ranklist = scraperwiki.sqlite.execute("select tidm, `3d`, `10d`, `30d`, `90d`, `180d`, `6mthProfit`, `6mthProfit_Rank`, StdDev, StdDev_Rank, SignalAccuracy, SignalAccuracy_Rank, Overall_Score, Overall_Rank from Company_Performance where `6mthProfit_Rank` < 150 and StdDev_Rank < 150 and SignalAccuracy >= .6 order by Overall_Rank")

      Performance_Out = Performance_Out + "  TIDM     3D    10D    30D    90D   180D   6MthProfit   Rank    Stddev   Rank    Sig Accuracy   Rank    Overall Score   Rank<br>"
      Performance_Out = Performance_Out + "-----------------------------------------------------------------------------------------------------------------------------<br>"

      for x in ranklist["data"]:
         tidm = x[0]
         d3 = x[1]
         d10 = x[2]
         d30 = x[3]
         d90 = x[4]
         d180 = x[5]
         profit6mth = x[6]
         profit6mth_rank = x[7]
         stddev = x[8]
         stddev_rank = x[9]
         signalaccuracy = x[10]
         signalaccuracy_rank = x[11]
         overall_score = x[12]
         overall_rank = x[13]
         Performance_Out = Performance_Out + '{:>6} {:>6} {:>6} {:>6} {:>6} {:>6} {:>10} {:>6} {:>9} {:>6} {:>10} {:>6} {:>12} {:>6}<br>'.format(tidm, d3, d10, d30, d90, d180, profit6mth, profit6mth_rank, stddev, stddev_rank, signalaccuracy, signalaccuracy_rank, overall_score, overall_rank)

    

    msg = MIMEMultipart()
    msg['From'] = cGFyc3vdcmF
    msg['To'] = cPFyc4dvcvF
    msg['Subject'] = "List"

    body = "<pre><font face='Consolas'>" + Performance_Out + "</font></pre>"

    msg.attach(MIMEText(body, 'html'))
 
    server = smtplib.SMTP(cGFdc2evcmQ, 587)
    server.starttls()
    server.login(cGFyc3vdcmF, cGFzc3dvcmQ)
    text = msg.as_string()
    server.sendmail(cGFyc3vdcmF, cPFyc4dvcvF, text)
    server.quit()

    return;

#-----------------------------#
#-----------------------------#
def Logger(rundt, fname, status):
    
    #scraperwiki.sqlite.execute("create table RunLog (`Rundate` date, `RunDateTime` date, `Proc` string, `status` string)") 
    
    if status == 'Starting':
      scraperwiki.sqlite.execute("insert into RunLog values (?,?,?,?)", [rundt.date(), rundt, fname, status])
    elif status == 'Complete':
      scraperwiki.sqlite.execute("update RunLog set proc = '%s', status = '%s' where rundatetime = '%s'" % (fname, status, rundt))
    else:
      scraperwiki.sqlite.execute("update RunLog set proc = '%s', status = '%s' where rundatetime = '%s'" % (fname, 'Incomplete', rundt))                      
    
    scraperwiki.sqlite.commit()
    return;

            
########################################################
# MAIN
########################################################
if __name__ == '__main__':
    
    #


    run = 1
    rerunflag = 0                        
    rundt = datetime.datetime.utcnow()
    
    print (rundt.date())

    Logger(rundt, 'Main', 'Starting')
                               
    while run == 1:
      gvars()
      
      Logger(rundt, 'ScrapeUserInput', None)
      ScrapeUserInput()
                               
      #Logger(rundt, 'ScrapeLivePrices', None)
      #rerunflag = ScrapeLivePrices(rerunflag)
      #if rerunflag = 0:
      #  run = 0
      
      #Logger(rundt, 'ScrapeSignalHistory_Core', None)
      #ScrapeSignalHistory(1)
      
      #Logger(rundt, 'UpdateOpenTrades', None)
      #UpdateOpenTrades()
                                 
      #Logger(rundt, 'SignalPerformance', None)                            
      #SignalPerformance()
                                 
      #Logger(rundt, 'Notify', None)
      #Notify(rerunflag)
                                 
      #Logger(rundt, 'ScrapeSignalHistory_Ext', None)
      #ScrapeSignalHistory(2)
                      
      #Logger(rundt, 'Main', 'Complete')

      
      #ScrapeBritishMain()
      
      #NewLivePrices()
      #SignalPerformance()
      #Notify(rerunflag)

    #`6mthProfit` real, `6mthProfit_Rank` integer, `StdDev` real, `StdDev_Rank` integer, `SignalAccuracy`
    #scraperwiki.sqlite.execute("create table tmptbl_rank (`TIDM` string, `Rank` integer)")

    #scraperwiki.sqlite.execute("delete from tmptbl_rank")
    #scraperwiki.sqlite.execute("INSERT into tmptbl_rank (TIDM, Rank) SELECT tidm, (SELECT COUNT()+1 FROM (SELECT DISTINCT StdDev FROM Company_Performance AS t WHERE StdDev < Company_Performance.StdDev)) AS Rank FROM Company_Performance" )

    #scraperwiki.sqlite.execute("UPDATE Company_Performance SET Company_Performance.StdDev_Rank = (select rank from tmptbl_rank) where tidm = Company_Performance.tidm")

    #scraperwiki.sqlite.execute("UPDATE Company_Performance dest, (SELECT tidm, (SELECT COUNT()+1 FROM (SELECT DISTINCT StdDev FROM Company_Performance AS t WHERE StdDev < Company_Performance.StdDev)) AS Rank FROM Company_Performance) src SET dest.StdDev_Rank = src.Rank where dest.tidm = src.tidm" )


    #scraperwiki.sqlite.execute( \
    #+ "Update Company_Performance CP Set StdDev_Rank = SELECT RANK FROM (SELECT tidm, StdDev, (SELECT COUNT()+1 FROM (SELECT DISTINCT StdDev FROM Company_Performance AS t WHERE StdDev < Company_Performance.StdDev)) AS Rank FROM Company_Performance) where tidm = CP.tidm" ) 
    #+ "SET StdDev_Rank = " \
    #+ "(select rank from (SELECT tidm, StdDev, (SELECT COUNT()+1 FROM (SELECT DISTINCT StdDev FROM Company_Performance AS t WHERE StdDev < Company_Performance.StdDev))" \
    #+ " AS Rank FROM Company_Performance) as A)" \
    #+ " where tidm = A.tidm" ) 

    #scraperwiki.sqlite.execute(
    #+ "Update Company_Performance "
    #+ "SET StdDev_Rank = " \
    #+ "(select rank from (SELECT tidm, StdDev, (SELECT COUNT()+1 FROM (SELECT DISTINCT StdDev FROM Company_Performance AS t WHERE StdDev < t.StdDev)) " \
    #+ "AS Rank FROM Company_Performance) as A) " \
    #+ "where tidm = Company_Performance.tidm" ) 

    #scraperwiki.sqlite.execute("Update Company_Performance SET StdDev_Rank = (select rank from (SELECT tidm, StdDev, (SELECT COUNT()+1 FROM (SELECT DISTINCT StdDev FROM Company_Performance AS t WHERE StdDev < Company_Performance.StdDev)) AS Rank FROM Company_Performance) as A) where tidm = Company_Performance.tidm")
    
    #scraperwiki.sqlite.execute("Update Company_Performance SET StdDev_Rank = (select rank from (SELECT tidm, StdDev, (SELECT COUNT()+1 FROM (SELECT DISTINCT StdDev FROM Company_Performance AS t WHERE StdDev < t.StdDev)) AS Rank FROM Company_Performance) where tidm = Company_Performance.tidm)")
    #scraperwiki.sqlite.execute("Update Company_Performance SET StdDev_Rank = (select rank from tmptbl_rank where tidm = Company_Performance.tidm)")


    #scraperwiki.sqlite.commit()

    #ranklist = scraperwiki.sqlite.execute( \
    #"SELECT TIDM, 3D, 10D, 30D, 90D, 180D, 6mthProfit, StdDev, SignalAccuracy, Date, from Company_Performance_tmp order by tidm" \
    #+ "UNION" \
    #+ "SELECT tidm, StdDev, (SELECT COUNT()+1 FROM (SELECT DISTINCT StdDev FROM Company_Performance " \
    #+  "AS t WHERE StdDev < Company_Performance.StdDev)) AS Rank FROM Company_Performance order by tidm")

    #ranklist = scraperwiki.sqlite.execute("SELECT tidm, StdDev, (SELECT COUNT()+1 FROM (SELECT DISTINCT StdDev FROM Company_Performance " \
    #+  "AS t WHERE StdDev < Company_Performance.StdDev)) AS Rank FROM Company_Performance order by rank")
          
    #data = scraperwiki.scrape("https://drive.google.com/open?id=1HehMfkCV3uVEu4dgsVl1MTpZ891MGTTJaSNErxKIaiE")
      
    #reader = csv.reader(data.splitlines())

    #for row in reader:           
    #    print row[1]




          #print test3.pop(0)
          #print test3.pop(0)
          #print test3.pop(0)

        #test3 = re.findall('(\">|img\/)(.*?)(<\/|\.gif)', test1.replace("\B", ""))

         #       while len(test3) >= 5:
        
          #          sh_Date = re.search("(\w|\d)(.*)(\w|\d)", str(test3.pop(0)).replace(" ", "")).group(0)

    #reader = csv.DictReader(data.splitlines()) 
    
    #for row in reader:           qqw
    #if row['Transaction Number']:
    #   row['Amount'] = float(row['Amount'])
    #   scraperwiki.sqlite.save(unique_keys=['Transaction Number', 'Expense Type', 'Expense Area'], data=row)

    #Notify(Performance_Out)
    #print strftime("%Y-%m-%d %H:%M:%S", gmtime())


