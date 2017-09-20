from modules import collectHTML as collect
from modules import extractHTML as extract
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

#Globals
OUTPUT_PATH = '../data/'
shopIds = [93230555, 90404278, 75010650, 6088238, 22303139]




'''
Collect HTML
'''
for shopId in shopIds:
    #Progress marker
    print(shopId)

    #Collect html from each restaurant main page
    collect.mainPage(shopId, OUTPUT_PATH)

    #Set a timeout between each request
    time.sleep(3)




'''
Extract HTML
'''
#--Main page
#Make all html files as soups in a soup cauldron
soupCauldron = []
def makeSoups(fldr):
    for filename in os.listdir(fldr):
        content = open(fldr + filename, 'r', errors='replace', encoding='utf-8')
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
