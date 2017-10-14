from urllib import request
import os
import re
from bs4 import BeautifulSoup
import csv
import numpy as np
import pandas as pd
import time
import random

import os
import sys

zone_list = list(pd.read_csv(r'..\data\raw\url\dianping_zone.csv', sep=',', header=None)[0])

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

    # for url_store in reviewLinks:
    #     if url_store != None:
    #         url_dianping = url_store + '/review_more'

    # url_dianping = 'http://www.dianping.com/shop/67863483/review_more?pageno=1'

    # try:
    #     response_dianping = request.urlopen(url_dianping)
    #     html_dianping = response_dianping.read().decode('utf-8')
    #     html_dianping = BeautifulSoup(html_dianping, 'html.parser')
    # except: html_dianping = None

    # comment_page_number = html_dianping.find('div', attrs={'class':'pages'}).findAll('a', attrs = {'class' : 'PageLink'})['data-pg']

    df_main = {
        'url' : reviewLinks,
        'Number':comment_numbers
    }
    df_main = pd.DataFrame(df_main, index = None)
    return df_main

RETRY = 2
for i in np.arange(161,300):
    for attempt in range(RETRY):
        try:
            DF_final = pd.DataFrame()
            id = zone_list[i].split('/')[-1][:-5]
            for j in np.arange(1,51):
                DF = getURL_dianping(zone_list[i], j)
                DF_final = pd.concat([DF_final, DF])
                time.sleep(random.uniform(1, 5))

        except:
            #If arrive retry cap, raise error and stop running
            if attempt + 1 == RETRY: raise

            #If not arrive retry cap, sleep and continue next attempt
            else:
                time.sleep(random.uniform(30, 90))
                continue
        
        #If no exception occurs (successful), break from attempt
        break
            
    DF_final.to_csv(r'..\data\raw\url\r{}.csv'.format(id))
    print(r'{} - done!'.format(id))
    time.sleep(random.uniform(30, 90))

# else: reviewLinks = None

# # number = html.find(class_ = 'sear-highlight').b.get_text()
# productDivs_number = html.findAll('span', attrs={'class': 'sear-highlight'})
# # # if productDivs != []:
# for span in productDivs_number: 
#     try: number = span.find('b').getText()
#     except: number = None
#     numbers.append(number)

# df_main = {
#     'url' : reviewLinks,
#     'Number':numbers
# }
# df_main = pd.DataFrame(df_main, index = None)

# print(reviewLinks)


# # # url = ""
# # try:
# #     productDivs = html.findAll('div', attrs={'class': 'tit'})
# #     for div in productDivs:
# #         url_store = div.find('a')['href']
# #         reviewLinks.append(url_store)
# # except: reviewLinks = None
# # # else: reviewLinks = None
# # try:
# #     # number = html.find(class_ = 'sear-highlight').b.get_text()
# #     productDivs_number = html.findAll('span', attrs={'class': 'sear-highlight'})
# # # # if productDivs != []:
# #     for span in productDivs_number:
# #         number = span.find('b').getText()
# #         numbers.append(number)
# # except: numbers = None

# # try:
# #     df_main = {
# #         'url' : reviewLinks,
# #         'Number':numbers
# #     }
# #     df_main = pd.DataFrame(df_main, index = None)

# # except: 
# #     df_main = pd.DataFrame({
# #     'url' : reviewLinks,
# #     'Number' : numbers
# #     }, index = [0])

# # return df_main

# # getURL_dianping(zone_list[1][0], 1).to_csv(r"C:\Users\Shun Wang\Desktop\test\url_list.csv")
# # result_test = getURL_dianping(zone_list[1][0],1)
# # print(result_test)
# # result_test = ['apple','cherry','orange','pineapple','strawberry']

# # with open(r'C:\Users\Shun Wang\Desktop\test\url_list.csv','w') as resultFile:
# #     wr = csv.writer(resultFile, lineterminator = '\n')
# #     for val in result_test:
# #         wr.writerow([val])
#     # wr.writerow(result_test)
# # RESULTS = []
# # DF_final = pd.DataFrame()
# # #
# # for i in np.arange(0,1):
# #      for j in np.arange(1,3):
# #          DF = getURL_dianping(zone_list[i][0], j)
# #          DF_final = pd.concat([DF_final, DF])

# print(zone_list[0][0])
# # df_1 = getURL_dianping(zone_list[0][0], 50)
# df_2 = getURL_dianping(zone_list[0][0], 30)
# # df_3 = pd.concat([df_1, df_2])
# print(df_2)

# # DF_final.to_csv(r"C:\Users\Shun Wang\Desktop\test\url_list_1.csv")
# #          print(RESULTS)
#         #  with open("url_list.csv",'wb') as resultFile:
#         #      wr = csv.writer(resultFile, dialect='excel')
#         #      for item in RESULTS:
#         #          wr.writerow(item)
# # with open(r'C:\Users\Shun Wang\Desktop\test\url_list.csv','w') as resultFile:
# #     wr = csv.writer(resultFile, lineterminator = '\n')
# #     for i in np.arange(0,2):
# #         for val in RESULTS[i]:
# #             wr.writerow([val])
# #
# #     # print(zone_list[i][0])
# #
# # # for i in zone_list:
# # #     # for i in list(range(1, 50)):
# # #     print(i)

#Combine main page lists
lis = pd.DataFrame()
for filename in os.listdir('../data/raw/url/'):
    if filename[0] == 'r':
        li = pd.read_csv('../data/raw/url/' + filename)
        li['source'] = filename.strip('.csv')
        lis = lis.append(li, ignore_index=True)

lis.drop(lis.columns[0], axis=1).drop_duplicates(subset='url').to_csv(r'..\data\raw\url\dianping_lis.csv')