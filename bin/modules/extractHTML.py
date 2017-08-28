# Import libraries
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re


def extractSoup(soup, filename, webSource):
    if webSource == 'GameSpot':
        extracted = extract_GameSpot(soup, filename)

    if webSource == 'Polygon':
        extracted = extract_Polygon(soup, filename)

    if webSource == 'GamesRadar':
        extracted = extract_GamesRadar(soup, filename)

    return extracted

    
def extract_GameSpot(soup, filename):
    # Game title
    try: gameTitle = soup.find(class_ = 'related-game__title').a.get_text()
    except: gameTitle = None

    # GS review score
    try: GSScore = soup.find(class_ = 'gs-score__cell').span.get_text()
    except: GSScore = None

    # User review score
    try: userScore = soup.find(class_ = 'breakdown-reviewScores__userAvg').a.get_text()
    except: userScore = None

    # GS review
    GSReview = ""
    try:
        chunks = soup.select('#default-content p')
        for chunk in chunks:
            result = chunk.get_text()
            GSReview = GSReview + ' ' + result
    except:
        GSReview = None

    # Author name
    try: authorName = soup.find(class_ = 'authorCard-name').strong.get_text()
    except: authorName = None

    # Release date
    try: releaseDate = soup.find(class_ = 'pod-objectStats-info__release').span.get_text()
    except: releaseDate = None

    # Game short description
    try: shortDescript = soup.find(class_ = 'pod-objectStats-info__deck').get_text()
    except: shortDescript = None

    # ESRB category
    try: ESRB = soup.find(class_ = 'pod-objectStats__esrb').dt.get_text()
    except: ESRB = None

    # main table
    try:
        df_main = {
            'Game Title'       : gameTitle,
            'GS Score'         : GSScore,
            'User Score'       : userScore,
            'Author Name'      : authorName,
            'Release Date'     : releaseDate,
            'Short Description': shortDescript,
            'Review'           : GSReview,
            'ESRB'             : ESRB,
            'File Name'        : filename
        }
        df_main = pd.DataFrame(df_main, index = [1])
    except: df_main = None

    # -----------------------------------------------------
    # Platforms
    platform = []
    try:
        chunks = soup.select('.clearfix strong')
        for chunk in chunks:
            result = chunk.get_text()
            platform.append(result)
    except: platform = None

    # platform table
    try:
        df_platform = {
            'Game Title': np.repeat(gameTitle, len(platform)),
            'Platform'  : platform
        }
        df_platform = pd.DataFrame(df_platform)
    except: df_platform = None

    # -----------------------------------------------------
    # scrape for developer, publisher, genre
    chunks = soup.find(class_ = 'pod-objectStats-additional').find_all('dd')

    # Developer
    developer = []
    try:
        results = chunks[0].find_all('a')
        for res in results:
            result = res.get_text()
            developer.append(result)
    except: developer = None

    # developer table
    try:
        df_developer = {
            'Game Title': np.repeat(gameTitle, len(developer)),
            'Developer' : developer
        }
        df_developer = pd.DataFrame(df_developer)
    except: df_developer = None

    # -----------------------------------------------------
    # Publisher
    publisher = []
    try:
        results = chunks[1].find_all('a')
        for res in results:
            result = res.get_text()
            publisher.append(result)
    except: publisher = None

    # publisher table
    try:
        df_publisher = {
            'Game Title': np.repeat(gameTitle, len(publisher)),
            'Publisher' : publisher
        }
        df_publisher = pd.DataFrame(df_publisher)
    except: df_publisher = None

    # -----------------------------------------------------
    # genre
    genre = []
    try:
        results = chunks[2].find_all('a')
        for res in results:
            result = res.get_text()
            genre.append(result)
    except: genre = None

    # genre table
    try:
        df_genre = {
            'Game Title': np.repeat(gameTitle, len(genre)),
            'Genre'     : genre
        }
        df_genre = pd.DataFrame(df_genre)
    except: df_genre = None


    return (df_main, df_platform, df_developer, df_publisher, df_genre)


def extract_Polygon(soup, filename):
    #Game Title (review title)
    try: gameTitle = soup.h1.get_text()
    except: gameTitle = None

    try: gameTitle = re.sub(' review.*', '', gameTitle, flags=re.IGNORECASE)
    except: gameTitle = None

    #Review
    PolyReview = ''
    try:
        if soup.select('#review-body p'):
            chunks = soup.select('#review-body p')
            for chunk in chunks:
                result = chunk.get_text()
                PolyReview = PolyReview + ' ' + result
        else:
            chunks = soup.find_all('p')
            for chunk in chunks:
                result = chunk.get_text()
                PolyReview = PolyReview + ' ' + result
    except: PolyReview = None

    #Author
    try:
        if soup.select('#entry-top .byline a'):
            authorName = soup.select('#entry-top .byline a')[0].get_text()
        else:
            authorName = soup.select('.c-byline > .c-byline__item a')[0].get_text()
    except: authorName = None

    #Verdict
    verdict = ''
    try:
        chunks = soup.find_all('q')
        for chunk in chunks:
            result = chunk.get_text()
            verdict = verdict + ' ' + result
    except: verdict = None

    #Wrap-up
    wrap = ''
    try:
        chunks = soup.find_all('blockquote')
        for chunk in chunks:
            result = chunk.get_text()
            wrap = wrap + ' ' + result
    except: wrap = None

    #Main table
    try:
        df_main = {
            'Game Title' : gameTitle,
            'Author Name': authorName,
            'Wrap-up'    : wrap,
            'Review'     : PolyReview,
            'Verdict'    : verdict,
            'File Name'  : filename
        }
        df_main = pd.DataFrame(df_main, index = [1])
    except: df_main = None

    return df_main

    
def extract_GamesRadar(soup, filename):
    #Game title
    try: gameTitle = soup.select('.review-title-long')[0].get_text()
    except: gameTitle = None

    if gameTitle == None:
        try: gameTitle = soup.select('.review-title-medium')[0].get_text()
        except: gameTitle = None
    
    if gameTitle == None:
        try: gameTitle = soup.select('.review-title-standard')[0].get_text()
        except: gameTitle = None
    
    try: gameTitle = re.sub(' review.*', '', gameTitle, flags=re.IGNORECASE)
    except: gameTitle = None
    
    #Review score
    try: ReviewerScore = soup.find(class_ = 'out-of-score-text').p.get_text()
    except: ReviewerScore = None

    try: verdict = soup.find(class_="game-verdict").get_text()
    except: verdict = None

    #Review
    Review = ""
    try:
        for divs in soup.find_all('div', attrs={"class" : "text-copy bodyCopy auto"}):
            for ptag in divs.find_all('p'):
                result = ptag.text
                Review = Review + ' ' + result
    except: Review = None

    #Author
    try: authorName = soup.find(class_ = 'no-wrap by-author').span.get_text()
    except: authorName = None

    #Main table
    try:
        df_main = {
            'Game Title'    : gameTitle,
            'Reviewer Score': ReviewerScore,
            'Verdict'       : verdict,
            'Author Name'   : authorName,
            'Review'        : Review
        }
        df_main = pd.DataFrame(df_main, index = [1])
    except: df_main = None

    return df_main