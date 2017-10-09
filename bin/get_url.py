from urllib import request
import os
import re
from bs4 import BeautifulSoup
import csv
import numpy as np
import pandas as pd

import os
import sys

# pd.read_csv(r'..\data\raw\url\dianping_zone_2.csv', sep='/', header=None)

with open(r'..\data\raw\url\dianping_zone_2.csv', 'r') as f:
  reader = csv.reader(f)  
  zone_list = list(reader)

def getURL_dianping(url, page):
    reviewLinks = []
    comment_numbers = []
    comment_page_number = []

    url_final = url + 'p' + str(page)

    try:
        response = request.urlopen(url_final)
        html = response.read().decode('utf-8')
        html = BeautifulSoup(html, 'html.parser')
    except: html = None

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

DF_final = pd.DataFrame()

for i in np.arange(1,2):
     for j in np.arange(1,51):
         DF = getURL_dianping(zone_list[i][0], j)
         DF_final = pd.concat([DF_final, DF])


DF_final.to_csv(r'..\data\raw\url\url_list2_1.csv')

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
