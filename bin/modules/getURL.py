from modules import settings
from modules import utils
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import re








'''
------------------------------------------------------------
Get shop main page url (from each zone)
------------------------------------------------------------
'''
def zones(zoneList):
    #--Function for acquiring shop URLs of each zone
    def getShopURL(zoneURL, page):
        reviewLinks = []
        comment_numbers = []
        comment_page_number = []

        #Acquire target page url
        url_final = zoneURL + 'p' + str(page)
        url_final = zoneList[0]


        #--Access a specific page of the URL list
        #Initialize browser and 
        browser = webdriver.PhantomJS(
            desired_capabilities=utils.setupBrowserDcaps(),
            service_log_path=settings.LOG_PATH)
        browser.set_page_load_timeout(settings.DOWNLOAD_TIMEOUT)

        #Access the target URL
        browser.get(url_final)
        
        #Acquire and parse raw HTML
        html = browser.execute_script('return document.documentElement.innerHTML')
        html = BeautifulSoup(html, 'html.parser')


        #--Produce chunks, each for one shop
        chunks = html.findAll('div', attrs={'class':'txt'})


        #--Acquire shop URL and review number from each chunk
        for chunk in chunks:
            #URL
            url_store = chunk.find('div', attrs={'class':'tit'}).find('a')['href']
            reviewLinks.append(url_store)

            #Review number
            comment_number = chunk.find('a', attrs={'class': 'review-num'}).find('b').getText()
            comment_numbers.append(comment_number)


        #--Combine the results and make into a df
        df_url = {
            'url': reviewLinks,
            'Number': comment_numbers
        }
        df_url = pd.DataFrame(df_url, index=None)


        #--Return the result if no error occurs
        return df_url





    for i in range(len(zoneList)):
        #--Initialize
        currentPage = 1
        df_url_final = pd.DataFrame()

        #Identify the shop id
        cutOff = [m for m in re.finditer('\D', zoneList[i].split('/')[-1])][1].end() - 1
        id = zoneList[i].split('/')[-1][:cutOff]


        for attempt in range(settings.RETRY):
            #--Scrape each page
            try:
                for j in range(currentPage, 51):
                    df_url = getShopURL(zoneList[i], j)

                    #If go over the last page, break, move on to next zone
                    if len(browser.find_elements_by_class_name('no-result')) > 0: break

                    #If no list returns, raise and retry
                    elif len(df_url) == 0: raise

                    #Produce the output
                    df_url_final = pd.concat([df_url_final, df_url])

                    #Page progress marker
                    print('p{}'.format(j))

                    #Sleep before next zone
                    time.sleep(random.uniform(3, 7))

            except:
                #If arrive retry cap, raise error and stop running
                if attempt + 1 == settings.RETRY: raise

                #If not arrive retry cap, sleep and continue next attempt
                else:
                    currentPage = j
                    utils.reportError()
                    time.sleep(random.uniform(3, 7) * (attempt + 1))
                    print(r'{0} - retry {1}'.format(id, attempt + 1))
                    continue
            
            #If no exception occurs (successful), break from attempt
            break
            
        
        #--Output the shop list of a specific zone
        df_url_final.to_csv('{0}raw_{1}/url/{2}{3}.csv'.format(settings.OUTPUT_PATH, settings.CITY_CODE, settings.ZONE_PREFIX, id))

        #Progress marker
        print(r'{} - done!'.format(id))

        #Sleep before next zone
        time.sleep(random.uniform(3, 7))








'''
------------------------------------------------------------
Combine main page lists
------------------------------------------------------------
'''
def combineLis():
    lis = pd.DataFrame()


    #--For all file in the folder, append onto the long list
    for filename in os.listdir('{0}raw_{1}/url/'.format(settings.OUTPUT_PATH, settings.CITY_CODE)):

        if filename[0] == 'r': #Exclude summary files
            li = pd.read_csv('{0}raw_{1}/url/{2}'.format(settings.OUTPUT_PATH, settings.CITY_CODE, filename))
            li['source'] = filename.strip('.csv')
            lis = lis.append(li, ignore_index=True)


    #--Clean the result
    #Remove duplicate urls
    lis.drop_duplicates(subset='url')[['Number', 'source', 'url']].to_csv('{0}raw_{1}/url/dianping_lis.csv'.format(settings.OUTPUT_PATH, settings.CITY_CODE), index=False)