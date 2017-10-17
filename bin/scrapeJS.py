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
RETRY = 3 #How many times to retry when error in module
PAGE_LIMIT = 5 #How many review pages per restaurant to save

#Establish necessary folder structure
paths = [
    '{}raw/main/'.format(OUTPUT_PATH),
    '{}raw/review/'.format(OUTPUT_PATH),
    '{}raw/url/'.format(OUTPUT_PATH)
]
for p in paths:
    if not os.path.exists(p): os.makedirs(p)




'''
------------------------------------------------------------
Collect HTML by Selenium
------------------------------------------------------------
'''
#Section switch
if True:

    #Source
    df_source = pd.read_csv(OUTPUT_PATH + 'raw/url/dianping_lis.csv')
    items = df_source.query('Number >= 100')

    def collectBySelenium(items, collect):
        for index, item in items.iterrows():
            #Retry several times for general errors not caught in the module
            for attempt in range(RETRY):
                try:
                    #Progress marker
                    shopId = item.url.strip('http://www.dianping.com/shop/')

                    #Acquire valid review page number (20 reviews per page)
                    pageValid = (item.Number // 20) + 1

                    #Collect html from each restaurant
                    collect(shopId, OUTPUT_PATH, pageLimit=min(PAGE_LIMIT, pageValid))

                except:
                    #If arrive retry cap, raise error and stop running
                    if attempt + 1 == RETRY: raise

                    #If not arrive retry cap, sleep and continue next attempt
                    else:
                        time.sleep(random.uniform(30, 90))
                        print(r'{0} - retry {1}'.format(shopId, attempt + 1))
                        continue
                
                #If no exception occurs (successful), break from attempt
                break

            #Progress marker
            print(r'{} - done!'.format(shopId))

            #Set a random timeout between each successful request
            time.sleep(random.uniform(4, 10))

    #Perform collection by setting proper callback
    #`collect.mainPage`, `collect.reviewPage`
    collectBySelenium(items[5570:7000], collect.mainPage) #Last: 17034 5560-5570








'''
------------------------------------------------------------
Collect HTML by Scrapy
------------------------------------------------------------
'''
#Run in terminal:
#cd scrapy
#scrapy crawl main








'''
------------------------------------------------------------
Extract HTML
------------------------------------------------------------
'''
#Section switch
if False:

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
