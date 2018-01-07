import os
import time
import pandas as pd
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from modules import settings


def reportError():
    print('{0} {1}'.format(
        str(sys.exc_info()[0]),
        str(sys.exc_info()[1])))


def setupBrowserDcaps(): #Device capability
    dcaps = DesiredCapabilities.PHANTOMJS
    dcaps['phantomjs.page.settings.loadImages'] = False

    #Randomly acquire 0 to 4
    i = int(((time.time() % 1 * 10) // 1) // 2)

    #Set custom headers
    #Ref:http://phantomjs.org/api/webpage/property/custom-headers.html
    dcaps['phantomjs.page.customHeaders.User-Agent'] = settings.USERAGENT_CANDIDATES[i]
    dcaps['phantomjs.page.customHeaders.Accept'] = 'application/json, text/javascript'

    #!!!
    #Fully customized cookie
    #(Phantomjs uses cookie by default. Comment this line to let the browser generate natural cookies.)
    # dcaps['phantomjs.page.customHeaders.Cookie'] = settings.HEADER_COOKIE
    #!!!
    return dcaps


def createFolders(outputPath, city):
    paths = [
        '{0}raw_{1}/main/'.format(outputPath, city),
        '{0}raw_{1}/review/'.format(outputPath, city),
        '{0}raw_{1}/url/'.format(outputPath, city)
    ]
    for p in paths:
        if not os.path.exists(p): os.makedirs(p)


def errorScreenShot(browser, strLimit=1000):
    #Print all we got
    try: screenShot = browser.execute_script('return document.documentElement.innerHTML')[:strLimit]
    
    #Else, note that there's no response
    except: screenShot = 'No HTML response.'

    return screenShot


def problematicResult(targetList, targetPath):
    """
    problematic = missing + bad  
    missing = In the list but not in the folder  
    bad = In the folder but file size is sketchy
    """
    target_missing = set(targetList) - set([fileName.strip('.html') for fileName in os.listdir(targetPath)])
    
    #`Bad threshold ~= 10KB
    target_bad = set([fileName.strip('.html') for fileName in os.listdir(targetPath) if os.path.getsize(targetPath + fileName) < 10000])

    return list(target_missing | target_bad)


def sourceItem(sourcePath, reviewThreshold, city):
    #Check if the list exists
    fullSourcePath = '{0}raw_{1}/url/dianping_lis.csv'.format(sourcePath, city)
    if not os.path.exists(fullSourcePath):
        #Issue an warning
        print('List file of city {} not found. sourceItem = None.'.format(city))

        #Return items = None if no list file
        return None

    #Read in the list acquired from the url crawling
    df_source = pd.read_csv(fullSourcePath)
        
    #Strip url for shopIds
    df_source = df_source.assign(shopId=[url.strip('http://www.dianping.com/shop/') for url in df_source.url])

    #Filter by needs
    items = df_source.query('Number >= {}'.format(reviewThreshold))

    return items