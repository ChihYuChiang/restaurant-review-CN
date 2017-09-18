from modules import collectHTML as collect

#%%
OUTPUT_PATH = '../data/'
shopIds = [93230555, 90404278, 75010650, 6088238, 22303139]
shopIds = [93230555]

for shopId in shopIds:
    print(shopId)

    #Collect data from each restaurant page
    collect.mainPage(shopId, '../data/')

    #Set a timeout between each restaurant request
    time.sleep(3)








'''
------------------------------------------------------------
Extract info from HTML - restaurant main page
------------------------------------------------------------
'''
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re




'''
From soup
'''
soupCauldron = []
def makeSoups(fldr):
    for filename in os.listdir(fldr):
        content = open(fldr + filename, 'r', errors='replace', encoding='utf-8')
        soup = BeautifulSoup(content.read(), 'html5lib')
        yield (soup, filename)

soupCauldron = makeSoups(OUTPUT_PATH + 'raw/')




#%%
shopIds = [93230555, 90404278, 75010650, 6088238, 22303139]
content = open(OUTPUT_PATH + 'raw/' + str(shopIds[3]) + '.html', 'r', errors='replace', encoding='utf-8')
soup = BeautifulSoup(content.read(), 'html5lib')


#%%
#Shop name
try: shopName = re.sub('\n\n.*', '', soup.h1.get_text()).strip('\n ')
except: shopName = None

#Category
try: shopCat = 
re.sub('[\n ]', '', soup.find(class_='breadcrumb').get_text())
except: shopCat = None

#Number of Branches
try: branchNum = re.search('([0-9]+)家分店', soup.h1.get_text()).group(1)
except: branchNum = None

#Number of reviews
try: reviewNum = soup.find(id='reviewCount').get_text().rstrip('条评论')
except: reviewNum = None

#Average consumption
try: avgConsume = soup.find(id='avgPriceTitle').get_text().strip('人均：元')
except: avgConsume = None

#Address
try: address = soup.find(class_='expand-info address').find(itemprop='street-address')['title']
except: address = None

#Tel Number
try: tel = soup.find(class_='expand-info tel').find(itemprop='tel').get_text()
except: tel = None

#Special tags (團、訂、外、促)
try:
    specialTags = str(soup.find(class_='promosearch-wrapper'))
    tag_tuan = 'tag-tuan' in specialTags
    tag_ding = 'tag-ding' in specialTags
    tag_wai = 'tag-wai' in specialTags
    tag_cu = 'tag-cu' in specialTags
except:
    tag_tuan = None
    tag_ding = None
    tag_wai = None
    tag_cu = None

#Extra info (operation hour, simple desc, parking, alias, crowd-sourced)
try: extraInfo = soup.find(class_='other J-other').get_text()
re.sub('\n+', '\n', extraInfo.strip('\n ')))
except: extraInfo = None

#Good and bad tags
try:
    good_tags = []
    good_nos = []
    for chunk in soup.find_all(class_='good'):
        tagNo = re.search('^(.+)\((\d+)\)$', chunk.get_text())
        good_tags.append(tagNo.group(1))
        good_nos.append(tagNo.group(2))
except:
    good_tags = None
    good_nos = None

try:
    bad_tags = []
    bad_nos = []
    for chunk in soup.find_all(class_='bad'):
        tagNo = re.search('^(.+)\((\d+)\)$', chunk.get_text())
        bad_tags.append(tagNo.group(1))
        bad_nos.append(tagNo.group(2))
except:
    bad_tags = None
    bad_nos = None




'''
From extra df
'''
df_shopInfo_HTML = pd.read_csv(OUTPUT_PATH + 'df_shopInfo_HTML.csv')


#--Scores
df_shopInfo_HTML.HTML_generalScores[0]
soup_scores = BeautifulSoup(df_shopInfo_HTML.HTML_generalScores[0], 'html5lib')

#5 4 3 2 1 stars
star = re.findall('\d+', soup_scores.find(class_='stars').get_text())

#口味 環境 服務
score = re.findall('\d+\.\d+', soup_scores.find(class_='scores').get_text())


#--Recommended dishes
df_shopInfo_HTML.HTML_recDishes[0]
soup_dishes = BeautifulSoup(df_shopInfo_HTML.HTML_recDishes[0], 'html5lib')

dishes = soup_dishes.find_all('a', class_='item')

dish_names = []
dish_nos = []
for dish in dishes:
    dish_names.append(dish['title'])
    dish_nos.append(dish.em.get_text().strip('()'))




'''
Output cleaned df
'''
try:
    df_main = {
        'shopName'     : shopName,
        'shopID'       : #---,
        'shopCat'      : shopCat,
        'branchNum'    : branchNum,
        'reviewNum'    : reviewNum,
        'avgConsume'   : avgConsume,
        'address'      : address,
        'tel'          : tel,
        'tag_tuan'     : tag_tuan,
        'tag_ding'     : tag_ding,
        'tag_wai'      : tag_wai,
        'tag_cu'       : tag_cu,
        'extraInfo'    : extraInfo,
        'good_tags'    : good_tags,
        'good_nos'     : good_nos,
        'bad_tags'     : bad_tags,
        'bad_nos'      : bad_nos
    }
    df_main = pd.DataFrame(df_main, index = [1])
except: df_main = None

try:
    df_extraInfo = {
        'star_5'       : star[0],
        'star_4'       : star[1],
        'star_3'       : star[2],
        'star_2'       : star[3],
        'star_1'       : star[4],
        'score_taste'  : score[0],
        'score_environ': score[1],
        'score_service': score[2],
        'dish_names'   : dish_names,
        'dish_nos'     : dish_nos
    }
except: df_extraInfo = None