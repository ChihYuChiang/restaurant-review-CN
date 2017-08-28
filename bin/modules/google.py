#--Import library
import pandas as pd
from googleapiclient.discovery import build

#--Function accesses Google API and extract result
def search(search_term, api_key, cse_id, **kwargs):

    #Perform search
    service = build("customsearch", "v1", developerKey = api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    results = res['items']

    #Extract from results
    resultData = {
        'link'       : [],
        'snippet'    : [],
        'title'      : [],
        'cacheId'    : [],
        'displayLink': []
        }
    for result in results:
        resultData['link'].append(result['link'])
        resultData['snippet'].append(result['snippet'])
        resultData['title'].append(result['title'])
        resultData['cacheId'].append(result['cacheId'])
        resultData['displayLink'].append(result['displayLink'])
    return resultData




#--Code for testing
if __name__ == "__main__":

    #Search term, Google API key, and custom search engine id
    searchTerm    = '"kung pao chicken" recipe'
    resultNumber  = 10
    my_api_key    = "AIzaSyD698CDMgU6K1cTABL5uLiZo-aoycYDs2A"
    my_cse_id     = "013164819138687069296:8c0pks8tor4"

    #Get results
    resultData    = search(searchTerm, my_api_key, my_cse_id, num=resultNumber)

    #Turn into df and print
    df_resultData = pd.DataFrame(resultData)
    print(df_resultData)
