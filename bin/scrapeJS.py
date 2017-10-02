from modules import collectHTML as collect
from modules import extractHTML as extract
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import subprocess

#Const
OUTPUT_PATH = '../data/'
RETRY = 2

#Source
df_source = pd.read_csv(OUTPUT_PATH + 'raw/main/url/url_list_1.csv')
urls = df_source.query('Number >= 100').url




'''
Collect HTML by Scrapy

Run in terminal:
cd scrapy
scrapy crawl main
'''




'''
Collect HTML by Selenium
'''
#A marker of current item in the url list (for resuming from exceptions)
currentItem = 0

for url in urls[currentItem:]:
    #Retry a numbmer of times for each request
    for attempt in range(RETRY):
        try:
            #Progress marker
            shopId = url.strip('http://www.dianping.com/shop/')
            print(shopId)

            #Collect html from each restaurant main page
            collect.mainPage(shopId, OUTPUT_PATH)

        except:
            #If arrive retry cap, raise error and stop running
            if attempt + 1 == RETRY: raise

            #If not arrive retry cap, sleep and continue next attempt
            else:
                time.sleep(random.uniform(90, 180))
                continue
        
        #If no exception occurs (successful), break from attempt
        break
    
    #When request successful, update current item marker
    currentItem += 1

    #Set a random timeout between each successful request
    time.sleep(random.uniform(5, 15))








'''
Extract HTML
'''
#--Main page
#Make all html files as soups in a soup cauldron
soupCauldron = []
def makeSoups(fldr):
    for filename in os.listdir(fldr):
        with open(fldr + filename, 'r', errors='replace', encoding='utf-8') as content:
            soup = BeautifulSoup(content.read(), 'html5lib')
        yield (soup, filename)
soupCauldron = makeSoups(OUTPUT_PATH + 'raw/')

#Extract each soup and write into a df (in the module)
for soup, filename in soupCauldron:    
    print(filename)
    extract.mainPage(soup, filename, OUTPUT_PATH)


#--Extra shop info in main page
#Read the corresponding df
df_extraInfo_HTML = pd.read_csv(OUTPUT_PATH + 'df_extraInfo_HTML.csv')

#Extract each row and write into a new df (in the module)
for index, row in df_extraInfo_HTML.iterrows():
    #Make html text into soups
    soup_score = BeautifulSoup(row['HTML_generalScores'], 'html5lib')
    soup_dish = BeautifulSoup(row['HTML_recDishes'], 'html5lib')
    
    extract.extraInfo(soup_score, soup_dish, row['shopId'], OUTPUT_PATH)
