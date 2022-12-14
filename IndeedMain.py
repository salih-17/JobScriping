
# import libraries 
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
import random
import pymysql
from datetime import timedelta
from datetime import date
import re

from requests.structures import CaseInsensitiveDict


headers = CaseInsensitiveDict()
headers["Connection"] = "keep-alive"
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
headers["Upgrade-Insecure-Requests"] = "1"
headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
headers["Accept-Language"] = "en-US,en;q=0.9"
headers["Accept-Encoding"] = "gzip, deflate"


my_conn = create_engine("mysql+pymysql://admin:12345678@database-1.ciaff8ckhmlj.us-west-2.rds.amazonaws.com:3306/IndeedDataBase")

#------------------------------------------------------------
# importing the global file that has information about each of the countries which have Indeed
worldwidelinks = pd.read_csv ('worldwidelink.csv').set_index ('CountryName')
#------------------------------------------------------------

filterdate = 2
position = 'data'
totalpostion = 0

#------------------------------------------------------------
# Collecting all pages links for each country in the dataset
def collectinglinks ():
  totalpostion = 0
  Links = []

  for country in worldwidelinks.index:
    # preparation the link
    url = worldwidelinks['WebURL'].loc[country]+'jobs?q={}&fromage={}'.format (position ,filterdate )

    #Gathering the baseline information
    get = requests.get(url , headers=headers)
    soup = BeautifulSoup(get.text, 'html.parser')
    cards = len (soup.find_all('div', 'cardOutline'))
    totalpostion = totalpostion + cards

    #--------------------------------------------------------
    # Some pages dosn't have any information

    try:
        page = soup.find("div", id ="searchCountPages").get_text().strip()
    except:
        print ('no information')
    #--------------------------------------------------------
    # Apped the URL to the our list

    if cards > 0 : Links.append ({'country': country, 'URL':url , 'Position':cards})
    #--------------------------------------------------------
    # now we are working on gathering the other pages links if exist so WHILE Loop will still true if there are more pages

    while True:
        try:
            url2 =  worldwidelinks['WebURL'].loc[country] + soup.find('a', {'aria-label':worldwidelinks['last_page'].loc[country]}).get('href')
            
        except AttributeError:
            break
        #--------------------------------------------------------
        # Now we are using Beautifulsoup to get the number of results inside this page

        get = requests.get(url2, headers=headers)
        soup = BeautifulSoup(get.text, 'html.parser')
        cards = len (soup.find_all('div', 'cardOutline'))
        totalpostion = totalpostion + cards
        #--------------------------------------------------------
        # Some pages dosn't have any information inside this page

        try :
            page = soup.find("div", id ="searchCountPages").get_text().strip()
        except :
            print ('Erorr')
        #--------------------------------------------------------
        # Print the URL and the number of results and apped the URL's to the LIST

        if cards > 0 : Links.append ({'country': country, 'URL':url2, 'Position':cards})

  return (Links)

def fulldesc (link ):

    get = requests.get(link, headers=headers)
    soup = BeautifulSoup(get.text, 'html.parser')
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return(text) 

def gatheringdata (pagelinks):
  Dataset2 = []
  num = 0
# Gathering data from links
  for link in pagelinks:
      #--------------------------------------------------------
      # Now we are using Beautifulsoup to get the number of results
      get = requests.get(link['URL'], headers=headers)
      soup = BeautifulSoup(get.text, 'html.parser')
      Posted_Date = 0
      #--------------------------------------------------------
      # Now we are using Beautifulsoup to get interested information
      job_title = soup.find_all("h2", class_="jobTitle")
      companyName = soup.find_all('span', 'companyName')
      companyLocation = soup.find_all('div', 'companyLocation')
      des = soup.find_all('div', 'job-snippet')
      dateee = soup.find_all('span', 'date')
      job_url = soup.find_all('a', class_ = 'jcs-JobTitle css-jspxzf eu4oa1w0')
      RatingNumber = soup.find_all("span", class_="ratingNumber")
      salary = soup.find_all("div", class_="metadata salary-snippet-container")
      job_type = soup.find_all("div", class_="attribute_snippet")
      job_id = soup.find_all("h2", class_="jobTitle jobTitle-newJob css-bdjp2m eu4oa1w0")

      #--------------------------------------------------------
      # Now we are going deepth inside the page to collect our date    
      for i  , b in enumerate (dateee):
          from datetime import timedelta
          from datetime import date
          num = num + 1
          
          
          try :
              Job_ID = str (job_id[i])[str (job_id[i]).find ("data-jk=")+9 : str (job_id[i]).find ("data-jk=")+25]
          except:
              Job_ID = "N/A"

          try :
              test = job_type[i].get_text()
              if any(chr.isdigit() for chr in test) == True :
                  Job_type = 'N/A'
              else:
                  Job_type = test
          except:
              Job_type = 'N/A'
          try :
              Rating_Number = RatingNumber[i].get_text()
          except:
              Rating_Number = 'N/A'
          try :
              Salary = salary[i].get_text()
          except:
              Salary = 'N/A'
              
          try:
              Job_title = job_title[i].get_text()
          except:
              Job_title = 'N/A'    

          try:
              CompanyName = companyName[i].get_text().strip()
          except:
              CompanyName = 'N/A'
          try:
              CompanyLocation=companyLocation[i].get_text().strip()
          except:
              CompanyLocation = 'N/A'     
          
          try: 
              Job_discribtion = des[i].get_text().strip()
          except:
              Job_discribtion = 'N/A'

          try: 
            Datee = dateee[i].get_text().strip()
          except:
            Datee = 'N/A' 
              
          try:
            exdate= [int(x) for x in re.findall(r'-?\d+\.?\d*',Datee)][0]
            Posted_Date = date.today() - timedelta(days= exdate )
          except:
            Posted_Date = date.today()


          try:
              job_url =  link['URL'][0:22]+"viewjob?jk="+ Job_ID
          except:
              job_url = 'N/A'
          
          try :
            fulljobdescribtion = fulldesc (job_url)
          except:
            fulljobdescribtion = "N/A"
          
          e = 'N/A' 
          Dataset2.append( {"Countrye" :link['country'] ,
                            "city" : CompanyLocation,
                            'JobId':Job_ID ,
                            'Source':'Indeed' ,
                            'CollectedDate' :datetime.today().strftime('%Y-%m-%d') , 
                            "JobTitle":Job_title , 
                            "CompanyName" :CompanyName , 
                            'RatingNumber':Rating_Number,
                            "PostedDate":Datee ,
                            'Salary':Salary  ,
                            'JobType':Job_type ,
                            "jobURL" : job_url , 
                            "ShortDiscribtion" : Job_discribtion  ,                         
                            'fullJobDescribtion' : fulljobdescribtion  ,
                             "Posted_Date_N" :Posted_Date} )

  return (Dataset2)




def main():
    dd = collectinglinks()
    ff = gatheringdata(dd)
    df2 = pd.DataFrame(ff)
    df2.to_sql (con =my_conn , name = 'IndeedDataSet5' , if_exists = 'append' , index = False )
    try:
      file_name = str(int(random.random()*12345)) + "_df.xlsx"
      df2.to_excel(file_name)
    except:
      file_name = str(int(random.random()*12345)) + "_df.csv"
      df2.to_csv(file_name)

    
if __name__ == '__main__':
  main()









