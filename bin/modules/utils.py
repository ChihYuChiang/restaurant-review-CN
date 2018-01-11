import os
import sys
import time
import pandas as pd
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from modules import settings


#--Transform stdout obj into a customized obj which outputs at both console and a file
class DoubleOutputTarget(object):
    def __init__(self, *outputFiles):
        self.files = outputFiles

    #Mockup the structure of original sys.stdout obj
    def write(self, obj): #obj is what to be printed
        for f in self.files:
            f.write(obj)
            f.flush() #flush from cache to file (Make the output to be visible immediately)

    def flush(self):
        for f in self.files:
            f.flush()


def reportError(sys):
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


def problematicResult(targetList, targetPath, threshold):
    """
    problematic = missing + bad  
    missing = In the list but not in the folder  
    bad = In the folder but file size is sketchy
    """
    target_missing = set(targetList) - set([fileName.strip('r.html.csv') for fileName in os.listdir(targetPath)])
    
    #'Bad threshold (kb)
    target_bad = set([fileName.strip('r.html.csv') for fileName in os.listdir(targetPath) if os.path.getsize(targetPath + fileName) < threshold * 1000]) & set(targetList)

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