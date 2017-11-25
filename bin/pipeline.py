from modules import collectHTML as collect
from modules import extractHTML as extract
from modules import getURL as get
from modules import utils
from modules import settings
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import sys


#--Target city
#bj / sh / cd / gz
CITY_CODE = 'sh'


#--Establish necessary folder structure
utils.createFolders(settings.OUTPUT_PATH, CITY_CODE)


#--Source restaurent list
items = utils.sourceItem(settings.OUTPUT_PATH, settings.REVIEW_THRESHOLD, CITY_CODE)








'''
------------------------------------------------------------
Collect URL
------------------------------------------------------------
'''
#Section switch
if True:

    zoneList = list(pd.read_csv('{0}raw_{1}/url/dianping_zone_2.csv'.format(settings.OUTPUT_PATH, CITY_CODE), header=None)[0])

    get.zones(zoneList[100:200], 'r', CITY_CODE)





'''
------------------------------------------------------------
Collect HTML by Selenium
------------------------------------------------------------
'''
#Section switch
if False:

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
    collectBySelenium(items_problematic, collect.reviewPage)








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
#Section switch
if False:

    shopIds_problematic = utils.problematicResult(targetList=items.shopId, targetPath='{0}raw_{1}/review/'.format(settings.OUTPUT_PATH, CITY_CODE))

    len(shopIds_problematic)

    #Filter the items with the problematic ids
    items_problematic = items[items.shopId.isin(shopIds_problematic)]








'''
------------------------------------------------------------
Extract HTML -- Main and review
------------------------------------------------------------
'''
#Section switch
if False:

    #Make all html files as soups in a soup cauldron
    def makeSoups(fldr):
        #Filter out extra info df files
        filteredFilenames = (filename for filename in os.listdir(fldr) if filename[0:2] != 'df')
        for filename in filteredFilenames:
            with open(fldr + filename, 'r', errors='replace', encoding='utf-8') as content:
                soup = BeautifulSoup(content.read(), 'html5lib')
            yield (soup, filename)

    #Extract each soup and write into a df (in the module)
    def genEntries(soupCauldron, ext):
        for soup, filename in soupCauldron:    
            yield ext(soup, filename, settings.OUTPUT_PATH)

            #Progress marker
            print(filename)

    #Acquire the cauldron
    #'raw/main/' or 'raw/review/'
    soupCauldron = makeSoups('{0}raw_{1}/review/'.format(settings.OUTPUT_PATH, CITY_CODE))

    #Concat the extracted info to a united df
    #ext = extract.mainPage or extract.review
    #.drop_duplicates(subset='shopID') if needed
    df = pd.concat(genEntries(soupCauldron, ext=extract.review), ignore_index=True)

    #Output to a file
    #Support batch extraction
    #'df_main.csv' or 'df_review.csv'
    fullOutputPath = '{0}df_review_{1}.csv'.format(settings.OUTPUT_PATH, CITY_CODE)
    df.to_csv(fullOutputPath, index=False, encoding='utf-8', mode='a', header=not os.path.isfile(fullOutputPath))








'''
------------------------------------------------------------
Extract HTML -- Extra info
------------------------------------------------------------
'''
#Section switch
if False:

    #--Extra shop info in main page
    #Read the corresponding dfs
    fldr = '{0}raw_{1}/main/'.format(settings.OUTPUT_PATH, CITY_CODE)
    dfs_extraInfo_HTML = (pd.read_csv(fldr + filename) for filename in os.listdir(fldr) if filename[0:2] == 'df')

    #Extract each row and write into a new df
    def genEntries(dfs):
        for df in dfs:
            for index, row in df.iterrows():
                #Make html text into soups
                #Dealing with multiple columns
                try:
                    soup_score = BeautifulSoup(row['HTML_generalScores'], 'html5lib')
                except: soup_score = None
                try:
                    soup_dish = BeautifulSoup(row['HTML_recDishes'], 'html5lib')
                except: soup_dish = None
                
                yield extract.extraInfo(soup_score, soup_dish, row['shopId'])
            
            #Progress marker
            print('Raw file extraction done.')

    #Concat the extracted info to a united df
    df_extraInfo = pd.concat(genEntries(dfs_extraInfo_HTML), ignore_index=True).drop_duplicates(subset='shopID')

    #Output to a file
    df_extraInfo.to_csv(settings.OUTPUT_PATH + 'df_extraInfo_{}.csv'.format(CITY_CODE), index=False, encoding='utf-8')