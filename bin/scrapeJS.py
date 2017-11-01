from modules import collectHTML as collect
from modules import extractHTML as extract
from modules import utils
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import sys

#Const
OUTPUT_PATH = '../data/'
RETRY = 5 #How many times to retry when error in module
PAGE_LIMIT = 5 #How many review pages per restaurant to save
REVIEW_THRESHOLD = 200 #Filter for those shops with reviews more than the threshold

#Establish necessary folder structure
paths = [
    '{}raw/main/'.format(OUTPUT_PATH),
    '{}raw/review/'.format(OUTPUT_PATH),
    '{}raw/url/'.format(OUTPUT_PATH)
]
for p in paths:
    if not os.path.exists(p): os.makedirs(p)


#--Source restaurent list
items = utils.sourceItem(REVIEW_THRESHOLD)








'''
------------------------------------------------------------
Collect HTML by Selenium
------------------------------------------------------------
'''
#Section switch
if True:

    #--Function to perform collection
    def collectBySelenium(items, collect):
        for index, item in items.iterrows():
            #Initialize
            currentPage = 1
            currentContent = ''

            #Retry several times for general errors not caught in the module
            for attempt in range(RETRY):
                try:
                    #Acquire valid review page number (20 reviews per page)
                    pageValid = (item.Number // 20) + 1

                    #Collect html from each restaurant
                    collect(item.shopId, OUTPUT_PATH, pageLimit=min(PAGE_LIMIT, pageValid), startingPage=currentPage, inheritContent=currentContent)

                except Exception as e:
                    #If arrive retry cap, raise error and stop running
                    if attempt + 1 == RETRY: raise

                    #If not arrive retry cap, print exception info, sleep, and continue next attempt
                    else:
                        print('{0} {1}'.format(
                            str(sys.exc_info()[0]),
                            str(sys.exc_info()[1])))
                        
                        #If the error coming from specific review page, update the current page and current content vars
                        try:
                            currentPage = e.currentPage
                            currentContent = e.currentContent
                        except: pass

                        time.sleep(random.uniform(20, 40))
                        print(r'{0} - retry {1}'.format(item.shopId, attempt + 1))
                        continue
                
                #If no exception occurs (successful), break from attempt
                break

            #Progress marker
            print(r'{} - done!'.format(item.shopId))

            #Set a random timeout between each successful request
            time.sleep(random.uniform(3, 7))


    #--Perform collection by setting proper callback
    #`collect.mainPage`, `collect.reviewPage`
    collectBySelenium(items[200:1200], collect.reviewPage) #12200








'''
------------------------------------------------------------
Collect HTML by Scrapy
(to compensate what the Selenium missed)
------------------------------------------------------------
'''
#Run in terminal:
#cd scrapy
#scrapy crawl main








'''
------------------------------------------------------------
Check and identify missing and bad items
------------------------------------------------------------
'''
shopIds_problematic = utils.problematicResult(targetList=items.shopId, targetPath='../data/raw/main/')








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
