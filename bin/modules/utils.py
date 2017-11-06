import os
import pandas as pd


def createFolders(outputPath):
    paths = [
        '{}raw/main/'.format(outputPath),
        '{}raw/review/'.format(outputPath),
        '{}raw/url/'.format(outputPath)
    ]
    for p in paths:
        if not os.path.exists(p): os.makedirs(p)


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


def sourceItem(sourcePath, reviewThreshold):
    #Read in the list acquired from the url crawling
    df_source = pd.read_csv(sourcePath + 'raw/url/dianping_lis.csv')
        
    #Strip url for shopIds
    df_source = df_source.assign(shopId=[url.strip('http://www.dianping.com/shop/') for url in df_source.url])

    #Filter by needs
    items = df_source.query('Number >= {}'.format(reviewThreshold))

    return items