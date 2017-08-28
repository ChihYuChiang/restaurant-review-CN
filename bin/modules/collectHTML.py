#--Import libraries
from urllib import request
import os
import re
from bs4 import BeautifulSoup




'''
------------------------------------------------------------
getURL: Get review links from category page
------------------------------------------------------------
'''
def getURL(page, webSource):
    if webSource == 'Polygon':
        reviewLinks = getURL_Polygon(page)
    
    if webSource == 'GameSpot':
        reviewLinks = getURL_GameSpot(page)
    
    if webSource == 'GamesRadar':
        reviewLinks = getURL_GamesRadar(page)

    return reviewLinks


def getURL_GameSpot(page):
    reviewLinks = []
    response = request.urlopen('http://www.gamespot.com/reviews/?page=' + str(page))
    html = response.read().decode('utf-8')
    html = BeautifulSoup(html, 'html5lib')

    chunks = html.select('#js-sort-filter-results .js-event-tracking')
    for chunk in chunks:
        result = chunk.get('href')
        reviewLinks.append('http://www.gamespot.com' + result)
    return reviewLinks


def getURL_Polygon(page):
    reviewLinks = []
    if page == 1:
        url = 'http://www.polygon.com/games/reviewed/'
    else :
        url = 'http://www.polygon.com/games/reviewed/' + str(page)
    response = request.urlopen(url)
    html = response.read().decode('utf-8')
    html = BeautifulSoup(html, 'html5lib')

    chunks = html.select('.review_link')
    for chunk in chunks:
        result = chunk.get('href')
        reviewLinks.append(result)
    return reviewLinks


def getURL_GamesRadar(page):
    reviewLinks = []
    if page == 1:
        url = 'http://www.gamesradar.com/all-platforms/reviews'
    else :
        url = 'http://www.gamesradar.com/all-platforms/reviews/page/' + str(page) +'/'
    response = request.urlopen(url)
    html = response.read().decode('utf-8')
    html = BeautifulSoup(html, 'html.parser')

    for i in list(range(1, 21)):
        productDivs = html.findAll('div', attrs={'class': 'listingResult small result' + str(i) + " "})
        for div in productDivs:
            result = div.find('a')['href']
            reviewLinks.append(result)
    return reviewLinks




'''
------------------------------------------------------------
getHTML: Get html file and save locally
------------------------------------------------------------
'''
def getHTML(url, webSource):
    if webSource == 'Polygon': getHTML_Polygon(url)
    if webSource == 'GameSpot': getHTML_GameSpot(url)
    if webSource == 'GamesRadar': getHTML_GamesRadar(url)


def getHTML_GameSpot(url):
    #Create directory if dataset directory does not already exist
    output_fldr = '../data/raw/'
    if not os.access(output_fldr, os.F_OK):
        os.mkdir(output_fldr)
    
    #extract id from url for filenane
    searchStr = re.search('/[0-9]+-[0-9]+/$', url).group(0)[1:-1]
    response = request.urlopen(url)
    html = response.read().decode('utf-8')
    content = open(output_fldr + searchStr + '.html', 'w+', encoding='utf-8')
    content.write(html)
    content.close()


def getHTML_Polygon(url):
    #Create directory if dataset directory does not already exist
    output_fldr = '../data/raw_polygon/'
    if not os.access(output_fldr, os.F_OK):
        os.mkdir(output_fldr)
    
    #extract id from url for filenane
    searchStr = re.search('/[0-9]{5,}/', url).group(0)[1:-1] 
    response = request.urlopen(url)
    html = response.read().decode('utf-8')
    with open(output_fldr + searchStr + '.html', 'w+', encoding='utf-8') as content:
        content.write(html)


def getHTML_GamesRadar(url):
    #Create directory if dataset directory does not already exist
    output_fldr = '../data/raw_gamesradar/'
    if not os.access(output_fldr, os.F_OK):
        os.mkdir(output_fldr)
    
    #extract id from url for filenane
    searchStr = re.search('/([a-z0-9]*\-)+[a-z0-9]*/$', url).group(0)[1:-1] # extract id from url for filenane
    response = request.urlopen(url)
    html = response.read().decode('utf-8')
    content = open(output_fldr + searchStr + '.html', 'w+', encoding='utf-8')
    content.write(html)
    content.close()
