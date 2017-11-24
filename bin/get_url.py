from urllib import request
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
import random
import os

zone_list = list(pd.read_csv(r'..\data\raw_sh\url\dianping_shanghai_zone_2.csv', sep=',', header=None)[0])

def getURL_dianping(url, page):
    reviewLinks = []
    comment_numbers = []
    comment_page_number = []

    url_final = url + 'p' + str(page)

    response = request.urlopen(url_final)
    html = response.read().decode('utf-8')
    html = BeautifulSoup(html, 'html.parser')

    try:
        chunks = html.findAll('div', attrs = {'class':'txt'})
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

    df_main = {
        'url' : reviewLinks,
        'Number':comment_numbers
    }
    df_main = pd.DataFrame(df_main, index = None)
    return df_main

RETRY = 2
for i in np.arange(0,5): #'230
    for attempt in range(RETRY):
        try:
            DF_final = pd.DataFrame()
            id = zone_list[i].split('/')[-1][:-5]
            for j in np.arange(1,51):
                DF = getURL_dianping(zone_list[i], j)
                DF_final = pd.concat([DF_final, DF])
                time.sleep(random.uniform(1, 5))
                print('p{}'.format(j))

        except:
            #If arrive retry cap, raise error and stop running
            if attempt + 1 == RETRY: raise

            #If not arrive retry cap, sleep and continue next attempt
            else:
                time.sleep(random.uniform(10, 30))
                print(r'{0} - retry {1}'.format(id, attempt + 1))
                continue
        
        #If no exception occurs (successful), break from attempt
        break
            
    DF_final.to_csv(r'..\data\raw_sh\url\rr{}.csv'.format(id))
    print(r'{} - done!'.format(id))
    time.sleep(random.uniform(30, 90))


#--Combine main page lists
lis = pd.DataFrame()
for filename in os.listdir('../data/raw/url/'):
    if filename[0] == 'r':
        li = pd.read_csv('../data/raw/url/' + filename)
        li['source'] = filename.strip('.csv')
        lis = lis.append(li, ignore_index=True)

lis.drop(lis.columns[0], axis=1).drop_duplicates(subset='url').to_csv(r'..\data\raw\url\dianping_lis.csv', index=False)