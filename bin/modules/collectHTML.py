from modules import settings
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import pandas as pd
import time
import random
import re
import os
import sys








'''
------------------------------------------------------------
Set up webdriver (browser)
------------------------------------------------------------
'''
#--Set options
#Device capability
def setupDcaps():
    dcaps = DesiredCapabilities.PHANTOMJS
    dcaps['phantomjs.page.settings.loadImages'] = False

    #Randomly acquire 0 to 4
    i = int(((time.time() % 1 * 10) // 1) // 2)

    #Set custom headers
    #Ref:http://phantomjs.org/api/webpage/property/custom-headers.html
    dcaps['phantomjs.page.customHeaders.User-Agent'] = settings.USERAGENT_CANDIDATES[i]
    dcaps['phantomjs.page.customHeaders.Accept'] = 'application/json, text/javascript'
    dcaps['phantomjs.page.customHeaders.Cookie'] = settings.HEADER_COOKIE
    return dcaps

#Additional driver options
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
def reviewPage(shopId, pageLimit, startingPage, inheritContent, curAttempt, **kwargs):
    #--Initiate browser (refresh the browser)
    #Replace with .Firefox(), or with the browser of choice (options could be different)
    #Place the corresponding driver (exe file) under C:\Users\XXXX\Anaconda3
    browser = webdriver.PhantomJS(
        desired_capabilities=setupDcaps(),
        service_log_path=LOG_PATH)
    browser.set_page_load_timeout(settings.DOWNLOAD_TIMEOUT)    


    #--Initialize output object
    HTML_reviews = inheritContent


    #--Browse and screenshot the pages
    for p in range(startingPage, pageLimit + 1):
        try:
            #--Targeting a url and navigate to that page
            url = 'http://www.dianping.com/shop/{0}/review_all/p{1}'.format(str(shopId), p)
            browser.get(url)

            #--Expand all reviews
            #Wait until review list loaded
            wait = WebDriverWait(browser, settings.DOWNLOAD_TIMEOUT)
            wait.until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, '.review-words')))

            #Find all unfold buttons
            #Use "elemnet(s)" so when no target is found, return Null instead of exception
            unfoldButtons = browser.find_elements_by_css_selector('.fold')

            #Click them all
            actions = webdriver.ActionChains(browser)
            for bt in unfoldButtons: actions.click(on_element=bt)
            
            #Perform actions
            actions.perform()


            #--Screenshot
            HTML_reviews += (browser.execute_script('return document.getElementsByClassName("reviews-items")[0].innerHTML') + '\n')


        except Exception as e:
            #--Deal with "商户不存在" error, the internal error of the website
            #If the errorMessage class exists
            if len(browser.find_elements_by_class_name('errorMessage')) > 0:

                #Issue error message
                HTML_reviews = '商户不存在'

                #Break the loop for the pages and save the error message in the html
                break


            #--Deal with "illegal UTF encoding error"
            #Check the exception message when attempted a certain times
            if curAttempt >= 3 and re.search('illegal UTF-16 sequence', str(sys.exc_info()[1])) is not None:

                #Issue error message
                HTML_reviews = str(sys.exc_info())

                #Break the loop for the pages and save the error message in the html
                break


            #--Deal with "商户暫停營業" error
            #Check the shop's main page
            #Do not try everytime the error occurs
            if curAttempt >= 3:
                #Setup a new browser
                browser_main = webdriver.PhantomJS(
                    desired_capabilities=setupDcaps(),
                    service_log_path=LOG_PATH)
                browser_main.set_page_load_timeout(settings.DOWNLOAD_TIMEOUT)

                #Get main page
                url = 'http://www.dianping.com/shop/{0}'.format(str(shopId))
                browser_main.get(url)

                #Report main page access
                print('Check main page..')

                #If the mid-str0 class exists (general rating = 0)
                if len(browser_main.find_elements_by_class_name('mid-str0')) > 0:

                    #Issue error message
                    HTML_reviews = '商户暫停營業'

                    #Break the loop for the pages and save the error message in the html
                    break
                
                #Close main page browser
                browser_main.quit()

            #--Other exceptions
            #Pass the current page and content to the retry loop
            e.currentPage = p
            e.currentContent = HTML_reviews
            e.browser = browser

            #Raise exception to be dealt with in pipeline
            raise e

        #Progress marker
        print('p{}'.format(p))

        #Delay between each page
        time.sleep(random.uniform(5, 15))


    #--Close browser
    browser.quit()

    #Save reviews, 1 restaurant per file
    with open(settings.OUTPUT_PATH + 'raw_{0}/review/{1}.html'.format(settings.CITY_CODE, str(shopId)), 'w+', encoding='utf-8') as f:
        f.write(HTML_reviews)








'''
------------------------------------------------------------
Browse and acquire html - restaurant main page
------------------------------------------------------------
'''
def mainPage(shopId, curAttempt, **kwargs):
    #--Initiate browser (refresh the browser)
    #Replace with .Firefox(), or with the browser of choice (options could be different)
    #Place the corresponding driver (exe file) under C:\Users\XXXX\Anaconda3
    browser = webdriver.PhantomJS(
        desired_capabilities=setupDcaps(),
        service_log_path=LOG_PATH)
    browser.set_page_load_timeout(settings.DOWNLOAD_TIMEOUT)


    #--Targeting a main page url and navigate to that page
    url = 'http://www.dianping.com/shop/' + str(shopId)
    browser.get(url)


    #--Acquire main page + info generated by JS
    #Actions
    try:
        #Wait until basic info and rec dish elements loaded
        wait = WebDriverWait(browser, settings.DOWNLOAD_TIMEOUT)
        wait.until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, '.sub-title'))) #Basic info
        wait.until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, '.recommend-name + .J-more'))) #Rec dish

        #Perform actions
        webdriver.ActionChains(browser
            ).click(on_element=browser.find_element_by_css_selector('.basic-info > a.J-unfold') #Basic info
            ).click(on_element=browser.find_element_by_css_selector('.recommend-name + .J-more') #Rec dish
            ).perform()

        #Get HTML
        HTML_main = browser.execute_script('return document.getElementById("body").innerHTML')

    except:
        #If the error is not because of being blocked (get failed), try a couple of times, make an error-commented html and move on
        #E.g. some buttons can't be found
        if curAttempt + 3 >= settings.RETRY:
            HTML_main = str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1])
        else: raise


    #--Close browser
    browser.quit()


    #--Save info to file
    #Save main page, 1 restaurant per file
    with open(settings.OUTPUT_PATH + 'raw_{0}/main/{1}.html'.format(settings.CITY_CODE, str(shopId)), 'w+', encoding='utf-8') as f:
        f.write(HTML_main)