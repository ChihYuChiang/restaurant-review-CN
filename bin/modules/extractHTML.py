from bs4 import BeautifulSoup
import pandas as pd
import re
import os








'''
------------------------------------------------------------
Extract info from HTML - restaurant main page
------------------------------------------------------------
'''
def mainPage(soup, filename, outputPath):
    #Shop name
    try: shopName = re.sub('\n\n.*', '', soup.h1.get_text()).strip('\n ')
    except: shopName = None

    #Category
    try: shopCat = re.sub('[\n ]', '', soup.find(class_='breadcrumb').get_text())
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
    try:
        extraInfo = soup.find(class_='other J-other').get_text().strip('\r\n')
        re.sub('\n+', '\n', extraInfo)
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


    #--Output extracted info
    try:
        entry_main = pd.DataFrame({
            'shopID'       : [filename.strip('.html')],
            'shopName'     : [shopName],
            'shopCat'      : [shopCat],
            'branchNum'    : [branchNum],
            'reviewNum'    : [reviewNum],
            'avgConsume'   : [avgConsume],
            'address'      : [address],
            'tel'          : [tel],
            'tag_tuan'     : [tag_tuan],
            'tag_ding'     : [tag_ding],
            'tag_wai'      : [tag_wai],
            'tag_cu'       : [tag_cu],
            'extraInfo'    : [extraInfo],
            'good_tags'    : [good_tags],
            'good_nos'     : [good_nos],
            'bad_tags'     : [bad_tags],
            'bad_nos'      : [bad_nos]
        })

        #Use df method to Write into file
        OUTPUT_FILE = outputPath + 'df_main.csv'
        entry_main.to_csv(OUTPUT_FILE, header=not os.path.exists(OUTPUT_FILE), index=False, encoding='utf-8', mode='a')
    except: pass








'''
------------------------------------------------------------
Extract info from HTML - restaurant main page's extra info
------------------------------------------------------------
'''
def extraInfo(soup_score, soup_dish, shopId, outputPath):
    #5 4 3 2 1 stars
    try: star = re.findall('\d+', soup_score.find(class_='stars').get_text())
    except: star = None

    #口味 環境 服務
    try: score = re.findall('\d+\.\d+', soup_score.find(class_='scores').get_text())
    except: score = None

    #Recommended dishes
    try:
        dishes = soup_dish.find_all('a', class_='item')

        dish_names = []
        dish_nos = [] #Number of user rec
        for dish in dishes:
            dish_names.append(dish['title'])
            dish_nos.append(dish.em.get_text().strip('()'))
    except:
        dish_names = None
        dish_nos = None


    #--Output extracted info
    try:
        entry_extraInfo = pd.DataFrame({
            'shopID'       : [shopId],
            'star_5'       : [star[0]],
            'star_4'       : [star[1]],
            'star_3'       : [star[2]],
            'star_2'       : [star[3]],
            'star_1'       : [star[4]],
            'score_taste'  : [score[0]],
            'score_environ': [score[1]],
            'score_service': [score[2]],
            'dish_names'   : [dish_names],
            'dish_nos'     : [dish_nos]
        })

        #Use df method to write into file
        OUTPUT_FILE = outputPath + 'df_extraInfo.csv'
        entry_extraInfo.to_csv(OUTPUT_FILE, header=not os.path.exists(OUTPUT_FILE), index=False, encoding='utf-8', mode='a')
    except: pass
