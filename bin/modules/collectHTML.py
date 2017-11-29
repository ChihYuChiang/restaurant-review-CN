from modules import settings
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import pandas as pd
import time
import random
import os
import sys








'''
------------------------------------------------------------
Set up webdriver (browser)
------------------------------------------------------------
'''
#--Acquire updated user agents from: https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
userAgentCandidates = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38'
]


#--Set options
#Device capability
def setupDcaps():
    dcaps = DesiredCapabilities.PHANTOMJS
    dcaps['phantomjs.page.settings.loadImages'] = False

    #Randomly acquire 0 to 4
    i = int(((time.time() % 1 * 10) // 1) // 2)

    #Set custom headers
    #Ref:http://phantomjs.org/api/webpage/property/custom-headers.html
    dcaps['phantomjs.page.customHeaders.User-Agent'] = userAgentCandidates[i]
    dcaps['phantomjs.page.customHeaders.Accept'] = 'application/json, text/javascript'
    dcaps['phantomjs.page.customHeaders.Cookie'] = 'PHOENIX_ID=0a010725-15e38404ab2-e498b4e; _hc.v=c9678f60-ffb1-70f3-6cc2-ca97c011b225.1492122470; __mta=43235098.1504182293440.1504182293440.1506927949288.2; _lxsdk=15e383e817439-0148d385f6254f-e313761-384000-15e383e8175c8;_lxsdk_cuid=15e383e817439-0148d385f6254f-e313761-384000-15e383e8175c8;aburl=1; cy=2; cye=beijing; s_ViewType=10'

    return dcaps

#Additional driver options
DOWNLOAD_TIMEOUT = 20
LOG_PATH = 'log/ghostdriver.log'

#Establish necessary folder structure
if not os.path.exists(LOG_PATH.split('/')[0]): os.makedirs(LOG_PATH.split('/')[0])

#Can be added to webdriver.PhantomJS(service_args)
#Currently unused
SERVICE_ARGS = [
    '--proxy=127.0.0.1:9999',
    '--proxy-type=http',
    '--ignore-ssl-errors=true'
]








'''
------------------------------------------------------------
Browse and acquire html - restaurant review page
------------------------------------------------------------
'''
def reviewPage(shopId, outputPath, pageLimit, startingPage, inheritContent, **kwargs):
    #--Initiate browser (refresh the browser)
    #Replace with .Firefox(), or with the browser of choice (options could be different)
    #Place the corresponding driver (exe file) under C:\Users\XXXX\Anaconda3
    browser = webdriver.PhantomJS(
        desired_capabilities=setupDcaps(),
        service_log_path=LOG_PATH)
    browser.set_page_load_timeout(DOWNLOAD_TIMEOUT)    


    #--Initialize output object
    HTML_reviews = inheritContent


    #--Browse and screenshot the pages
    for p in range(startingPage, pageLimit + 1):
        try:
            #Targeting a url and navigate to that page
            url = 'http://www.dianping.com/shop/{0}/review_more?pageno={1}'.format(str(shopId), p)
            browser.get(url)

            #Screenshot
            HTML_reviews += (browser.execute_script('return document.getElementsByClassName("comment-list")[0].innerHTML') + '\n')
        
        except:
            #Deal with "商户不存在" error, the internal error of the website
            try:
                HTML_reviews = browser.execute_script('return document.getElementsByClassName("errorMessage")[0].innerHTML')

                #Break the loop for the pages and save the error message in the html
                break

            except Exception as e:
                #Pass the current page and content to the retry loop
                e.currentPage = p
                e.currentContent = HTML_reviews
                raise e

        #Progress marker
        print('p{}'.format(p))

        #Delay between each page
        time.sleep(random.uniform(3, 7))


    #--Close browser
    browser.quit()

    #Save reviews, 1 restaurant per file
    with open(outputPath + 'raw_{0}/review/{1}.html'.format(settings.CITY_CODE, str(shopId)), 'w+', encoding='utf-8') as f:
        f.write(HTML_reviews)








'''
------------------------------------------------------------
Browse and acquire html - restaurant main page
------------------------------------------------------------
'''
def mainPage(shopId, outputPath, **kwargs):
    #--Initiate browser (refresh the browser)
    #Replace with .Firefox(), or with the browser of choice (options could be different)
    #Place the corresponding driver (exe file) under C:\Users\XXXX\Anaconda3
    browser = webdriver.PhantomJS(
        desired_capabilities=setupDcaps(),
        service_log_path=LOG_PATH)
    browser.set_page_load_timeout(DOWNLOAD_TIMEOUT)


    #--Targeting a main page url and navigate to that page
    url = 'http://www.dianping.com/shop/' + str(shopId)
    browser.get(url)


    #--Acquire main page + info generated by JS
    #Actions
    try:
        #Wait until basic info and rec dish elements loaded
        wait = WebDriverWait(browser, 10)
        wait.until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, '.sub-title'))) #Basic info
        wait.until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, '.recommend-name + .J-more'))) #Rec dish

        #Perform actions
        webdriver.ActionChains(browser
            ).click(on_element=browser.find_element_by_css_selector('.basic-info > a.J-unfold') #Basic info
            ).click(on_element=browser.find_element_by_css_selector('.recommend-name + .J-more') #Rec dish
            ).perform()

        #Get HTML
        HTML_main = browser.execute_script('return document.getElementById("body").innerHTML')

    except: HTML_main = str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1])


    #--Close browser
    browser.quit()


    #--Save info to file
    #Save main page, 1 restaurant per file
    with open(outputPath + 'raw_{0}/main/{1}.html'.format(settings.CITY_CODE, str(shopId)), 'w+', encoding='utf-8') as f:
        f.write(HTML_main)