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


#--Establish necessary folder structure
utils.createFolders(settings.OUTPUT_PATH, settings.CITY_CODE)


#--Source restaurent list
items = utils.sourceItem(settings.OUTPUT_PATH, settings.REVIEW_THRESHOLD, settings.CITY_CODE)








'''
------------------------------------------------------------
Collect URL lists
------------------------------------------------------------
'''
#Section switch
if False:

    #Acquire restaurant list for each zone
    zoneList = list(pd.read_csv('{0}raw_{1}/url/{2}'.format(settings.OUTPUT_PATH, settings.CITY_CODE, settings.ZONELIST_FILE), header=None)[0])

    get.zones(zoneList)








'''
------------------------------------------------------------
Combine URL lists
------------------------------------------------------------
'''
#Section switch
if False:

    get.combineLis()








'''
------------------------------------------------------------
Collect HTML by Selenium
------------------------------------------------------------
'''
#Section switch
if True:
    
    #--Function to perform collection
    def collectBySelenium(items, target, infinite):
        for index, item in items.iterrows():
            #Start marker
            print('{} - start'.format(item.shopId))

            #Initialize
            currentPage = 1
            currentContent = ''
            attempt = 1
            cycleCount = 1

            #Retry several times for general errors not caught in the module
            while attempt:
                try:
                    #Acquire valid review page number (20 reviews per page)
                    pageValid = (item.Number // 20) + 1

                    #Decide the function to use
                    targetFunctionMap = {
                        0: collect.mainPage,
                        1: collect.reviewPage
                    }

                    #Collect html from each restaurant
                    targetFunctionMap[target](item.shopId, pageLimit=min(settings.PAGE_LIMIT, pageValid), startingPage=currentPage, inheritContent=currentContent, curAttempt=attempt)

                    #If no exception occurs (successful), break from attempt
                    break

                except Exception as e:
                    #If arrive retry cap, screenshot, decide if reset or break
                    if attempt == settings.RETRY:
                        print(utils.errorScreenShot(e.browser))

                        #If infinite attempt
                        if infinite:
                            #Reset attempt
                            attempt = 1

                            #Restart after couple of mins
                            #The hibernation time is based on the restart cycle count
                            print('Hibernate for {} mins..'.format(str(5 ** cycleCount)))
                            time.sleep(random.uniform(40, 80) * 5 ** cycleCount)
                            
                            #Update restart cycle count
                            cycleCount += 1
                            print('{0} - restart {1}'.format(item.shopId, str(cycleCount - 1)))

                        else: raise

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

                        time.sleep(random.uniform(20, 40) * (attempt) * 0.5)
                        print(r'Retry {}'.format(attempt))

                        #Update attempt and continue
                        attempt += 1

            #Progress marker
            print(r'Done!')

            #Set a random timeout between each successful request
            time.sleep(random.uniform(3, 7))


    #--Perform collection
    #0 for mainPage, 1 for reviewPage
    collectBySelenium(items, 0, infinite=False)








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

    shopIds_problematic = utils.problematicResult(targetList=items.shopId, targetPath='{0}raw_{1}/review/'.format(settings.OUTPUT_PATH, settings.CITY_CODE))

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

    def extractFolder(target):
        #Decide the function and path to use
        targetFunctionMap = {
            0: {'txt': 'main', 'fun': extract.mainPage},
            1: {'txt': 'review', 'fun': extract.reviewPage}
        }

        #Acquire the cauldron
        soupCauldron = makeSoups('{0}raw_{1}/{2}/'.format(settings.OUTPUT_PATH, settings.CITY_CODE, targetFunctionMap[target]['txt']))

        #Concat the extracted info to a united df
        #.drop_duplicates(subset='shopID') if needed
        df = pd.concat(genEntries(soupCauldron, ext=targetFunctionMap[target]['fun']), ignore_index=True)

        #Output to a file
        #Support batch extraction
        #'df_main.csv' or 'df_review.csv'
        fullOutputPath = '{0}df_{1}_{2}.csv'.format(settings.OUTPUT_PATH, targetFunctionMap[target]['txt'], settings.CITY_CODE)
        df.to_csv(fullOutputPath, index=False, encoding='utf-8', mode='a', header=not os.path.isfile(fullOutputPath))


    #--Perform extraction
    #0 for mainPage, 1 for reviewPage
    extractFolder(0)








'''
------------------------------------------------------------
Extract HTML -- Extra info
(deprecated, only bj has this info)
------------------------------------------------------------
'''
#Section switch
if False:

    #--Extra shop info in main page
    #Read the corresponding dfs
    fldr = '{0}raw_{1}/main/'.format(settings.OUTPUT_PATH, settings.CITY_CODE)
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
    df_extraInfo.to_csv(settings.OUTPUT_PATH + 'df_extraInfo_{}.csv'.format(settings.CITY_CODE), index=False, encoding='utf-8')