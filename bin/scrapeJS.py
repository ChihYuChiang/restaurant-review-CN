from modules import collectHTML as collect
from modules import extractHTML as extract
from modules import utils
from modules import settings
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import sys


#--Establish necessary folder structure
utils.createFolders(settings.OUTPUT_PATH)


#--Source restaurent list
items = utils.sourceItem(settings.OUTPUT_PATH, settings.REVIEW_THRESHOLD)








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
            for attempt in range(settings.RETRY):
                try:
                    #Acquire valid review page number (20 reviews per page)
                    pageValid = (item.Number // 20) + 1

                    #Collect html from each restaurant
                    collect(item.shopId, settings.OUTPUT_PATH, pageLimit=min(settings.PAGE_LIMIT, pageValid), startingPage=currentPage, inheritContent=currentContent)

                except Exception as e:
                    #If arrive retry cap, raise error and stop running
                    if attempt + 1 == settings.RETRY: raise

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
len(shopIds_problematic)








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
    soupCauldron = makeSoups(settings.OUTPUT_PATH + 'raw/')

    #Extract each soup and write into a df (in the module)
    for soup, filename in soupCauldron:    
        print(filename)
        extract.mainPage(soup, filename, settings.OUTPUT_PATH)


    #--Extra shop info in main page
    #Read the corresponding df
    df_extraInfo_HTML = pd.read_csv(settings.OUTPUT_PATH + 'df_extraInfo_HTML.csv')

    #Extract each row and write into a new df (in the module)
    for index, row in df_extraInfo_HTML.iterrows():
        #Make html text into soups
        soup_score = BeautifulSoup(row['HTML_generalScores'], 'html5lib')
        soup_dish = BeautifulSoup(row['HTML_recDishes'], 'html5lib')
        
        extract.extraInfo(soup_score, soup_dish, row['shopId'], settings.OUTPUT_PATH)
