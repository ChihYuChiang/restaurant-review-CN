from modules import settings
from modules import utils
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import sys
import re








'''
------------------------------------------------------------
Get shop main page url (from each zone)
------------------------------------------------------------
'''
#--Function for acquiring shop URLs of each page
def getShopURL(zoneURL, page, browser):
    reviewLinks = []
    commentNumbers = []


    #--Access a specific page
    url_final = zoneURL + 'p' + str(page)
    browser.get(url_final)


    #--Acquire raw HTML
    html = browser.execute_script('return document.documentElement.innerHTML')

    #If go over the last page, break, move on to next zone
    if re.search('没有找到相应的商户', html) is not None or len(browser.find_elements_by_class_name('not-found')) > 0: return (None, True)


    #--Parse raw HTML
    html = BeautifulSoup(html, 'html.parser')

    #Produce chunks, each for one shop
    chunks = html.find_all('div', attrs={'class':'txt'})

    #Acquire shop URL and review number from each chunk
    for chunk in chunks:
        #URL
        url_store = chunk.select('.tit > a:nth-of-type(1)')[0]['href']
        reviewLinks.append(url_store)

        #Review number
        try: comment_number = chunk.select('.review-num b')[0].getText()
        except: comment_number = None
        commentNumbers.append(comment_number)


    #--Combine the results and make into a df
    df_url = {
        'url': reviewLinks,
        'Number': commentNumbers
    }
    df_url = pd.DataFrame(df_url, index=None)


    #--Return the result if no error occurs
    return (df_url, False)


#--Implement on each zone
def zones(zoneList, infinite):
    for i in range(len(zoneList)):
        #--Initialize
        cycleCount = 1
        currentPage = 1
        attempt = 1
        df_url_final = pd.DataFrame()

        #Identify the shop id
        cutOff = [m for m in re.finditer('\D', zoneList[i].split('/')[-1])][1].end() - 1
        id = zoneList[i].split('/')[-1][:cutOff]

        #Progress marker
        print(id + ' - start')


        while attempt:
            try:
                #--Initialize browser
                browser = webdriver.PhantomJS(
                    desired_capabilities=utils.setupBrowserDcaps(),
                    service_log_path=settings.LOG_PATH)
                browser.set_page_load_timeout(settings.DOWNLOAD_TIMEOUT)

                #Enter through the dianping main page
                browser.get('http://www.dianping.com/')


                #--Scrape each page
                for j in range(currentPage, 51):
                    df_url, _mo = getShopURL(zoneList[i], j, browser)
                    
                    #If go over the last page, break, move on to next zone
                    if _mo: break

                    #If no list returns, raise and retry
                    assert len(df_url) > 0

                    #Produce the output and add into list
                    df_url_final = pd.concat([df_url_final, df_url])

                    #Page progress marker
                    print('p{}'.format(j))

                    #Sleep before next zone
                    time.sleep(random.uniform(3, 7))
                
                #If no exception occurs (successful), break from attempt
                break

            except:
                #If arrive retry cap, raise error and stop running
                if attempt == settings.RETRY:
                    if infinite:
                        attempt = 1
                        utils.reportError(sys)
                        
                        #Restart after couple of mins
                        #The hibernation time is based on the restart cycle count
                        print('Hibernate for {} mins..'.format(str(5 ** cycleCount)))
                        time.sleep(random.uniform(40, 80) * 5 ** cycleCount)
                        
                        #Update and restart cycle count
                        cycleCount += 1
                        currentPage = j
                        browser.quit()
                        print('{0} - restart {1}'.format(id, str(cycleCount - 1)))
                    else: raise

                #If not arrive retry cap, sleep and continue next attempt
                else:
                    utils.reportError(sys)
                    try:
                        currentPage = j
                        browser.quit()
                    except: pass
                    time.sleep(random.uniform(3, 7) * (attempt))
                    print(r'Retry {}'.format(attempt))
                    attempt += 1
            
        
        #--Output the shop list of a specific zone
        df_url_final.to_csv('{0}raw_{1}/url/{2}{3}.csv'.format(settings.OUTPUT_PATH, settings.CITY_CODE, settings.ZONE_PREFIX, id))

        #Progress marker
        print(r'Done!')

        #Close browser and move on to the next shop
        browser.quit()

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