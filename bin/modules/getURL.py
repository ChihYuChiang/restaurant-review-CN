from modules import settings
from urllib import request
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import re

def zones(zoneList):
    def getShopURL(zoneURL, page):
        reviewLinks = []
        comment_numbers = []
        comment_page_number = []

        url_final = zoneURL + 'p' + str(page)
        try:
            response = request.urlopen(url_final)
            html = response.read().decode('utf-8')
            html = BeautifulSoup(html, 'html.parser')
        except: raise

        try:
            chunks = html.findAll('div', attrs={'class':'txt'})
        except: chunks = None

        if chunks != None:
            for chunk in chunks:
                try: url_store = chunk.find('div', attrs={'class':'tit'}).find('a')['href']
                except: url_store = None
                reviewLinks.append(url_store)
            for chunk in chunks:
                try: comment_number = chunk.find('span', attrs={'class': 'sear-highlight'}).find('b').getText()
                except: comment_number = None
                comment_numbers.append(comment_number)

        df_url = {
            'url': reviewLinks,
            'Number': comment_numbers
        }
        df_url = pd.DataFrame(df_url, index=None)
        return df_url

    for i in range(len(zoneList)):
        #Initialize
        cutOff = [m for m in re.finditer('\D', zoneList[i].split('/')[-1])][1].end() - 1
        id = zoneList[i].split('/')[-1][:cutOff]
        currentPage = 1
        df_url_final = pd.DataFrame()

        for attempt in range(settings.RETRY):
            try:
                for j in range(currentPage, 51):
                    df_url = getShopURL(zoneList[i], j)

                    if len(df_url) == 0: break

                    df_url_final = pd.concat([df_url_final, df_url])
                    print('p{}'.format(j))
                    time.sleep(random.uniform(3, 7))

            except:
                #If arrive retry cap, raise error and stop running
                if attempt + 1 == settings.RETRY: raise

                #If not arrive retry cap, sleep and continue next attempt
                else:
                    currentPage = j
                    time.sleep(random.uniform(3, 7) * (attempt + 1))
                    print(r'{0} - retry {1}'.format(id, attempt + 1))
                    continue
            
            #If no exception occurs (successful), break from attempt
            break
                
        df_url_final.to_csv('{0}raw_{1}/url/{2}{3}.csv'.format(settings.OUTPUT_PATH, settings.CITY_CODE, settings.ZONE_PREFIX, id))
        print(r'{} - done!'.format(id))

        time.sleep(random.uniform(3, 7))


#--Combine main page lists
def combineLis():
    lis = pd.DataFrame()
    for filename in os.listdir('{0}raw_{1}/url/'.format(settings.OUTPUT_PATH, settings.CITY_CODE)):
        if filename[0] == 'r':
            li = pd.read_csv('{0}raw_{1}/url/{2}'.format(settings.OUTPUT_PATH, settings.CITY_CODE, filename))
            li['source'] = filename.strip('.csv')
            lis = lis.append(li, ignore_index=True)

    lis.drop_duplicates(subset='url')[['Number', 'source', 'url']].to_csv('{0}raw_{1}/url/dianping_lis.csv'.format(settings.OUTPUT_PATH, settings.CITY_CODE), index=False)