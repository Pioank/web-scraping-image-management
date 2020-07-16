from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from urllib.request import urlopen as req
import re
import time
import pyodbc 
from itertools import *
import pandas as pd
from datetime import date
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import pandas.io.sql as psql
import sqlalchemy as sa
from urllib.parse import unquote
import requests
import cloudinary.uploader
import cloudinary
import cloudinary.api
import os
import glob
from selenium.webdriver.chrome.options import Options
pd.set_option('display.max_columns', None) # Remove column display limit for Pandas
driver = webdriver.Chrome(ChromeDriverManager().install()) # Installs latest Chrome driver

# Deleting locally the images that are saved from screenshots every time the script runs
files = glob.glob('C://Users//USER//Desktop//...//screenshots//') #The screenshots folder is in this project
for f in files:
    os.remove(f)

# Conntect to Cloudinary
cloudinary.config(cloud_name = '',api_key='',api_secret = '') # Credentials for img upload cloudinary
requests.packages.urllib3.disable_warnings()

today = date.today()
d1 = today.strftime("%d/%m/%Y")

# Create lists to store the scraped data
v1=list()
v2=list()
v3=list()
v4=list()
v5=list()
v6=list()
v7=list()
v8=list()

# Code below sets the Chrome driver to emulate mobile and clear Cache as well as set to Icognito
mobile_emulation = {"deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 }, "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" }
opts=Options()
opts.set_capability("browser.cache.disk.enable", False)
opts.set_capability("browser.cache.memory.enable", False)
opts.set_capability("browser.cache.offline.enable", False)
opts.set_capability("network.http.use-cache", False)
opts.add_argument("--incognito")
opts.add_experimental_option("mobileEmulation", mobile_emulation)
driverr = webdriver.Chrome(ChromeDriverManager().install(),chrome_options = opts)

# Create a list of the URLs you want to scrape - Note that these pages have all the same structure
urls = ['https://www.oddschecker.com/free-bets/free-bet-no-deposit','https://www.oddschecker.com/free-bets','https://www.oddschecker.com/bookie-offers','https://www.oddschecker.com/casino-bonus/free-spins-no-deposit','https://www.oddschecker.com/casino-bonus/live-casino','https://www.oddschecker.com/casino-bonus/new-casino','https://www.oddschecker.com/casino-bonus/mobile-casino','https://www.oddschecker.com/poker']

x=0
for url in urls:
    driver.get(url)  

    if url == 'https://www.oddschecker.com/free-bets/free-bet-no-deposit':
        product = 'Casino-No-Deposit'
    elif url == 'https://www.oddschecker.com/casino-bonus/free-spins-no-deposit':
        product = 'Free-Spins'
    elif url == 'https://www.oddschecker.com/casino-bonus/live-casino':
        product = 'Live-Casino'
    elif url == 'https://www.oddschecker.com/casino-bonus/new-casino':
        product = 'Casino'
    elif url == 'https://www.oddschecker.com/casino-bonus/mobile-casino':
        product = 'Mobile-Casino'
    elif url == 'https://www.oddschecker.com/poker':
        product = 'Poker'
    else:
        product = 'Sports'

    promotit = driver.find_elements_by_xpath('//span[@class="offer-text beta-h2"]')
    promocomp = driver.find_elements_by_xpath('//div[@class="visit-bookie beta-caption4"]')
    promotc = driver.find_elements_by_xpath('//div[@class="nfb-details beta-caption4"]')

    html=driver.page_source
    soup = bs(html,features="html.parser")
    company = soup.findAll("tr",{"class": "offer-rows"} )
    order = soup.findAll("a",{"class": "button nfb-button beta-callout"} )

    for z in promotit: 
        v1.append(str(z.text))

    # Clean the data from this field and identify the company name
    for i in promocomp:
        promo = str(i.text)
        promo = promo.split("Visit ",1)[1]
        if 'Betfair' in promo: promo = 'Betfair'
        elif 'BGO' in promo: promo = 'BGO'
        elif 'Bet365' in promo: promo = 'Bet365'
        elif '888' in promo: promo = '888'
        elif 'LV' in promo: promo = 'LV'
        elif 'Mobile Wins' in promo: promo = 'MobileWins'
        elif 'MobileWins' in promo: promo = 'MobileWins'
        elif 'Genting' in promo: promo = 'Genting'
        elif 'Paddy Power' in promo: promo = 'PaddyPower'
        elif 'Sky' in promo: promo = 'Sky'
        elif 'STS' in promo: promo = 'STS'
        elif 'Unibet' in promo: promo = 'Unibet'
        elif 'William Hill' in promo: promo = 'WilliamHill'
        else: str(promo).replace(" ", "") 
        v2.append(promo)

    for i in promotc:
        v3.append(str(i.text))
    
    for i in company:
        v4.append(i['data-customer-type'])

    for i in order:
        orde = i['href']
        orderr = orde.split("offer_position=",1)[1] 
        v5.append(orderr[:1])
        v6.append(product)
        urll = re.search('url=(.*)&name=', orde)
        urll = urll.group(1)
        urll = unquote(urll)
        if "%" in str(urll):
            urll = unquote(urll)
        else: 
            print('No Second decoding required')
        
        # This piece of code navigates to the final URL of click tracker, loads the page, takes a screenshot, saves it locally then pushes it to Cloudinary
        # If not able to get the image screenshot then uses a fall back 404
        # Images are stored as URLs from Cloudinary in the same data set as the other data points
        try:
            r = requests.get(urll,verify = False)
            r=r.url
            r=r.split("?",1)[0] 
            driverr.set_window_size(375, 667)
            driverr.get(r)
            time.sleep(10)
            name = str(v2[x]).replace(" ", "") + '-' + str(today.strftime("%d-%m-%Y")) + '-' + v6[x]
            photfol = "C:\\Users\\USER\\Desktop\\screenshots\\"+name+".png"
            try:
                driverr.save_screenshot(photfol)  
                driverr.delete_all_cookies()    
                folder = str(today.strftime("%d-%m-%Y"))
                cloudinary.uploader.upload(photfol, public_id = name,folder=folder)
                photourl = 'https://res.cloudinary.com/hnnyutwf8/image/upload/'+ folder +'/'+ name +'.png'
                print('Photo Saved' + photourl)
                v8.append(photourl)
            except:
                v8.append('https://learn.getgrav.org/user/pages/11.troubleshooting/01.page-not-found/error-404.png')
                print('Couldnt take screenshot')
           
        except:
            r = unquote(urll)
            v8.append('https://learn.getgrav.org/user/pages/11.troubleshooting/01.page-not-found/error-404.png')
            print('No screenshot taken - 404 picture used')
        
        x = x + 1
        v7.append(r)
        
fresult = list(zip(v1,v2,v3,v4,v5,v6,v7,v8))
ffresult = pd.DataFrame(fresult, columns=['Title','Company','T&Cs','Customer Type','Position','Product','Url','Photo'])
ffresult = ffresult.drop_duplicates(subset=None, keep='first')
ffresult['Date'] = d1
ffresult['Source'] = 'OddsChecker'
ffresult['Key']=(ffresult['Title'].str.lower() + ffresult['T&Cs'].str.lower())
ffresult = ffresult.drop_duplicates(subset='Key', keep='first')

print(ffresult)

#Connect to your database
cnxn = pyodbc.connect("Driver={SQL Server};Server=;Database=;uid=;Trusted_Connection=yes;autocommit=False")
cur = cnxn.cursor()

# Try creating a table if one doesn't exist
try:
    sql="""CREATE TABLE tablename (title varchar(300) NOT NULL, company varchar(100) NOT NULL, tcs varchar(900), [customer_type] varchar(10), position int(5) NOT NULL, [date] varchar(10) NOT NULL, [data_source] varchar(10),product varchar(20) NOT NULL,url varchar(20) NOT NULL, photo varchar(100), key varchar(900))"""
    cur.execute(sql)
except:
    print('table exists')

cur.commit()
cur.close()

# Append new data to the existing one in your database
engine = sa.create_engine('mssql+pyodbc:?driver=SQL+Server+Native+Client+11.0')
ffresult.to_sql('tablename', engine, if_exists='replace', index = False)

driver.quit()
driverr.quit()
