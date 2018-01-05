from modules import settings
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
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
        tag_tuan = int('tag-tuan' in specialTags)
        tag_ding = int('tag-ding' in specialTags)
        tag_wai = int('tag-wai' in specialTags)
        tag_cu = int('tag-cu' in specialTags)
    except:
        tag_tuan = None
        tag_ding = None
        tag_wai = None
        tag_cu = None

    #Extra info (operation hour, simple desc, parking, alias, crowd-sourced)
    try:
        extraInfo = soup.find(class_='other J-other').get_text().strip('\r\n ')
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
        #Make as strs for saving 
        good_tags = ', '.join(good_tags)
        good_nos = ', '.join(good_nos)
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
        #Make as strs for saving
        bad_tags = ', '.join(bad_tags)
        bad_nos = ', '.join(bad_nos)
    except:
        bad_tags = None
        bad_nos = None


    #--Output extracted info
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

    #Return single entry
    #We'll write into file only after gather all info from the raw data for computational efficiency
    return entry_main








'''
------------------------------------------------------------
Extract info from HTML - restaurant main page's extra info
------------------------------------------------------------
'''
def extraInfo(soup_score, soup_dish, shopId):
    #5 4 3 2 1 stars
    try: star = re.findall('\d+', soup_score.find(class_='stars').get_text())
    except: star = [None] * 5

    #口味 環境 服務
    try: score = re.findall('\d+\.\d+', soup_score.find(class_='scores').get_text())
    except: score = [None] * 3

    #Recommended dishes
    try:
        dishes = soup_dish.find_all('a', class_='item')

        dish_names = []
        dish_nos = [] #Number of user rec
        for dish in dishes:
            dish_names.append(dish['title'])
            dish_nos.append(dish.em.get_text().strip('()'))
        #Make as strs for saving
        dish_names = ', '.join(dish_names)
        dish_nos = ', '.join(dish_nos)
    except:
        dish_names = None
        dish_nos = None


    #--Output extracted info
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

    #Return single entry
    #We'll write into file only after gather all info from the raw data for computational efficiency
    return entry_extraInfo








'''
------------------------------------------------------------
Extract info from HTML - review
------------------------------------------------------------
'''
def reviewPage(soup, filename, outputPath):
    #--Get review chunks as a list
    try:
        chunks = soup.findAll('li', attrs = {'data-id': True})
    except: return


    #--Empty vessels
    shopID = [filename.strip('.html')] * len(chunks)
    user_names = []
    user_ids = []
    user_contributions = []
    review_stars = []
    average_prices = []
    taste_stars = []
    environment_stars = []
    service_stars = []
    review_texts = []
    recommendations = []
    praises = []
    comments = []
    favorites = []


    #--Deal with individual review trunks
    #User name and id
    for chunk in chunks:
        try:
            user_account = chunk.find('div', attrs = {'class':'pic'}) 
            user_id = user_account.a['user-id']
            user_name = user_account.find('p', attrs={'class':'name'}).find('a').getText()
        except:
            user_name = None
            user_id = None
        user_names.append(user_name)
        user_ids.append(user_id)

    #User contribution level
    for chunk in chunks:
        try: 
            user_account = chunk.find('div', attrs = {'class':'pic'}) 
            user_information = user_account.find('p', attrs={'class':'contribution'}).find('span')['class'][1]
            user_contribution = re.findall("[0-9]+", user_information)[0]
        except: user_contribution = None
        user_contributions.append(user_contribution)

    #Primary rating
    for chunk in chunks:
        try:
            review_content = chunk.find('div', attrs = {'class':'content'}) 
            review_star_code = review_content.find('div', attrs={'class':'user-info'}).find('span', attrs = {'title': True})['class'][1]
            review_star = int(re.findall("[0-9]+", review_star_code)[0])
        except: review_star = None
        review_stars.append(review_star)

    #Average price
    for chunk in chunks:
        try:
            review_content = chunk.find('div', attrs = {'class':'content'}) 
            average_price_code = review_content.find('div', attrs={'class':'user-info'}).find('span', attrs = {'class': 'comm-per'}).getText()
            average_price = int(re.findall("[0-9]+", average_price_code)[0])
        except: average_price = None
        average_prices.append(average_price)

    #Sub ratings (taste, environment, service)
    for chunk in chunks:
        try:
            review_content = chunk.find('div', attrs = {'class':'content'}) 
            star_chunks = review_content.find('div', attrs={'class':'comment-rst'}).findAll('span', attrs = {'class': 'rst'})
            taste_star = int(star_chunks[0].getText()[2])
            environment_star = int(star_chunks[1].getText()[2])
            service_star = int(star_chunks[2].getText()[2])
        except: 
            taste_star = None
            environment_star = None
            service_star = None
        taste_stars.append(taste_star)
        environment_stars.append(environment_star)
        service_stars.append(service_star)

    #Review text
    for chunk in chunks:
        try:
            review_content = chunk.find('div', attrs = {'class':'content'}) 
            review_text = review_content.find('div', attrs = {'class' : 'J_brief-cont'}).getText().strip()
        except: review_text = None
        review_texts.append(review_text)

    #Recommended dishes
    for chunk in chunks:
        recommendations_1 = []
        try:
            review_content = chunk.find('div', attrs = {'class':'content'}) 
            recommendation_chunks = review_content.find('div', attrs = {'class' : 'comment-recommend'}).findAll('a', attrs = {'class' : 'col-exp'})
            for recommendation_chunk in recommendation_chunks:
                recommendation = recommendation_chunk.getText()
                recommendations_1.append(recommendation)
            recommendations_1 = ', '.join(recommendations_1)
        except: recommendations_1 = None
        recommendations.append(recommendations_1)

    #Praise and comment number (to this review)
    for chunk in chunks:
        try:
            review_action_chunk = chunk.find('span', attrs = {'class':'col-right'})
            praise = int(review_action_chunk.find('span', attrs = {'class':'heart-num'}).getText()[1])
        except: praise = None
        try:
            review_action_chunk = chunk.find('span', attrs = {'class':'col-right'})
            comment = int(review_action_chunk.find('span', attrs = {'class':'J_rtl'}).getText())
        except: comment = None
        praises.append(praise)
        comments.append(comment)


    #--Output extracted info
    entry_review = pd.DataFrame({
        'ShopID'             : shopID,
        'User Name'          : user_names,
        'User ID'            : user_ids,
        'Contribution'       : user_contributions,
        'Review Stars'       : review_stars,
        'Average Price'      : average_prices,
        'Taste Stars'        : taste_stars,
        'Environment Stars'  : environment_stars,
        'Service Stars'      : service_stars,
        'Review'             : review_texts,
        'Recommendations'    : recommendations,
        'Praises'            : praises,
        'Comments'           : comments
    })


    #Return single entry
    #We'll write into file only after gather all info from the raw data for computational efficiency
    return entry_review