import pandas as pd
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import re
import jieba
import pickle
import json
import sklearn.manifold
from pprint import pprint
from hanziconv import HanziConv

class UniversalContainer():

    def listData(self):
        data = [(item, getattr(self, item)) for item in dir(self) if not callable(getattr(self, item)) and not item.startswith("__")]
        for item in data: print(item)

    def listMethod(self):
        print([item for item in dir(self) if callable(getattr(self, item)) and not item.startswith("__")])




'''
------------------------------------------------------------
Preprocessing
------------------------------------------------------------
'''
#--Simplified and traditional conversion demonstration
HanziConv.toSimplified('憂鬱的天氣')
HanziConv.toTraditional('忧郁的天气')


#--Initialization
#Review df, sort by topic
df_review = pd.read_csv(r'..\data\person_rawtext.csv').sort_values('topic')

#Combine stopword lists and remove duplicates
#Also includes customized list
stopwords_customized = [' ', '地址', '原文', '网址', '官网', '电话', '店家', '资讯', '营业时间', '巷', '弄', '号', '楼', '年', '月', '每人', '平均', '价位', '餐厅', ]
stopwords = list(set([w for l in open(r'..\ref\stopwords\中文停用词库.txt', encoding='GB2312') for w in l.split()] + [w for l in open(r'..\ref\stopwords\哈工大停用词表.txt', encoding='GBK') for w in l.split()] + stopwords_customized))


#--Separate sentences
#Parameter: doc, a str
#Return: a list of strs (sentences)
def tokenize_sentence(doc):
    punList = ',.!?:;~，。！？：；～\r\n'
    senStart = 0
    sentences = []
    if isinstance(doc, str):
        for i in np.arange(len(doc) - 1):
            if doc[i] in punList and doc[i + 1] not in punList:
                sentences.append(doc[senStart : i + 1])
                senStart = i + 1
        if senStart < len(doc): sentences.append(doc[senStart: ])
    return sentences


#--Tokenize words
#Parameter: sentence, a str
#Return: a list of words (terms)
def tokenize_word(sentence):
    sentence = re.sub('(\\xa0)+', ' ', sentence)
    sentence = re.sub('\s+', ' ', sentence) #Space character
    sentence = re.sub('\w+', ' ', sentence, flags=re.ASCII) #number and eng words
    words = jieba.cut(sentence)
    return words


#--Remove stopwords
#Parameters: words, a list of str; stopwords, a list of str
#Return: a list of words with stopwords removed
def remove_stopword(words, stopwords):
    words = [w for w in words if w not in stopwords]
    return words


#--Tokenize and preprocessing by each doc
def preprocess(df, stopwords=stopwords):

    #Preprocessing
    text_preprocessed = []
    for _, r in df.iterrows():
        sentences = tokenize_sentence(HanziConv.toSimplified(str(r['text'])))
        sentences_preprocessed = [remove_stopword(tokenize_word(s), stopwords=stopwords) for s in sentences]
        sentences_preprocessed = [s for s in sentences_preprocessed if s] #Remove empty sentence
        if sentences_preprocessed: text_preprocessed.append((r['topic'], sentences_preprocessed)) #Remove empty review

    #Observe result
    pprint(text_preprocessed[:5])

    return text_preprocessed

text_preprocessed = preprocess(df_review)




'''
------------------------------------------------------------
Acquire doc vec
------------------------------------------------------------
'''
#--Preprocessed embedding data
with open(r'..\data\emb_updated.pickle', 'rb') as f:
    word_to_vec_map = pickle.load(f)


#--Acquire doc vec
#Average across words of a store to acquire store (doc) vec
def getDocVec(text_preprocessed, word_to_vec_map):

    #Vecs for all documents
    docVecs = []
    wordVecs = []
    topicMarker = text_preprocessed[0][0]
    topics = [topicMarker]

    #Loop over each review
    for item in text_preprocessed:

        #If new store, accumulate the wordVecs for the previous store
        if item[0] != topicMarker:
            #Update docVecs with all relevant wordVecs
            wordVecs = np.array(wordVecs)
            docVecs.append(np.mean(wordVecs, axis=0))

            #Reset wordVecs and update topic list
            wordVecs = []
            topics.append(item[0])

        #Acquire vec of each word
        for s in item[1]:
            for w in s:
                if w in word_to_vec_map.keys(): wordVecs.append(word_to_vec_map[w])

        #Update marker
        topicMarker = item[0]

    #Update docVecs with the last wordVecs
    wordVecs = np.array(wordVecs)
    docVecs.append(np.mean(wordVecs, axis=0))

    #Turn into np array
    docVecs = np.stack(docVecs)
    print(docVecs.shape)

    return docVecs, topics

docVecs, topics = getDocVec(text_preprocessed, word_to_vec_map)




'''
------------------------------------------------------------
2D projection
------------------------------------------------------------
'''
#--Tste projection
docProject_tste = sklearn.manifold.TSNE(n_components=2).fit_transform(docVecs)


#--Chinese font in matplotlib
#Matlplotlib accepts only ttf in windows fonts and package font
#Copy ttf to C:\Users\XXX\Anaconda3\Lib\site-packages\matplotlib\mpl-data\fonts\ttf
#Change file type from ttc to ttf
#Remove cache in C:\Users\XXX\.matplotlib
#Rebuild font list available
#See available fonts
import matplotlib.font_manager
matplotlib.font_manager._rebuild()
[f.name for f in matplotlib.font_manager.fontManager.ttflist]


#--Plot
#Set up the font
plt.rc('font', family='Microsoft YaHei')

#Base plot
plt.scatter(docProject_tste[:, 0], docProject_tste[:, 1], alpha=1)

#Choose some items to be labeled
for i in range(0, 140, 5):
    plt.annotate(topics[i], xy=(docProject_tste[i, 0], docProject_tste[i, 1]))

#Show and close
plt.show()
plt.close()




'''
------------------------------------------------------------
Preference matrix

- https://github.com/d3/d3-contour
------------------------------------------------------------
'''
data_pref = UniversalContainer()

#Pref data
data_pref.df = pd.read_csv(r'..\data\person_rating.csv', na_values=['#DIV/0!'])
data_pref.topic = topics
data_pref.df_sorted = pd.DataFrame(data_pref.topic, columns=['餐廳']).merge(data_pref.df, on='餐廳')

#Processing the prefs
data_pref.tsteDocProject = np.around(docProject_tste * 10).astype('int')
data_pref.tsteDocProjectL = data_pref.tsteDocProject.tolist()

data_pref.tsteMax = np.max(data_pref.tsteDocProject, axis=0)
data_pref.tsteMin = np.min(data_pref.tsteDocProject, axis=0)


#--Get cleaned up preference
def getPref(personId, data=data_pref):
    cleanPrefs = data.df_sorted[personId].copy()
    cleanPrefs[pd.isnull(cleanPrefs)] = 0
    return cleanPrefs.tolist()


#--The closest neighbors
def getClosestNeighbors(topN, data=data_pref):
    distance = sp.spatial.distance.squareform(sp.spatial.distance.pdist(data.tsteDocProject, 'euclidean'))
    neighborIds = np.argsort(distance, axis=-1)[:, 1:topN + 1].tolist()
    return neighborIds


#--Make prefs into contour matrix
#Not used in current app due to sparcity
def getPrefMatrix(personId, data=data_pref):
    prefs = []
    for j in range(data.tsteMin[1] - 5, data.tsteMax[1] + 5 + 1): #5 as the margin
        for i in range(data.tsteMin[0] - 5, data.tsteMax[0] + 5 + 1):
            if [i, j] in data.tsteDocProjectL:
                v = data.df[data.df.餐廳 == data.topic[data.tsteDocProjectL.index([i, j])]][personId].values[0]
                if not pd.isnull(v): prefs.append(v)
                else: prefs.append(0)
            else: prefs.append(0)
    return prefs


#--Make pref density by jittering
#Jitter base on range
def jitter(x, y, base, scale=0.05):
    x = x + np.random.normal(base, scale * base) - base
    y = y + np.random.normal(base, scale * base) - base
    return [np.around(x, 2), np.around(y, 2)]

#Get pref point coordinates
def getPrefPoints(personId, data=data_pref):
    prefPoints = []
    for i in range(len(data.tsteDocProjectL)):
        v = data.df[data.df.餐廳 == data.topic[i]][personId].values[0]
        if not pd.isnull(v):
            prefPoints += [data.tsteDocProjectL[i]] * np.around(v * 10).astype('int')

    for i in range(len(prefPoints)):
        prefPoints[i] = jitter(*prefPoints[i], base=np.mean(data.tsteMax - data.tsteMin))

    return prefPoints


#--Output into file
prefPoints = {}
prefPoints['topic']         = data_pref.topic
prefPoints['coordinate']    = data_pref.tsteDocProjectL
prefPoints['coordinateRange'] = np.stack([data_pref.tsteMin - (data_pref.tsteMax - data_pref.tsteMin) * 0.1, data_pref.tsteMax + (data_pref.tsteMax - data_pref.tsteMin) * 0.1]).transpose().tolist()
prefPoints['closestneighbor'] = getClosestNeighbors(topN=5)
prefPoints['pref']         = {}
prefPoints['pref']['yu']   = getPref('予')
prefPoints['pref']['jian'] = getPref('兼')
prefPoints['pref']['xin']  = getPref('欣')
prefPoints['pref']['overall']  = getPref('總分')
prefPoints['point']         = {}
prefPoints['point']['yu']   = getPrefPoints('予')
prefPoints['point']['jian'] = getPrefPoints('兼')
prefPoints['point']['xin']  = getPrefPoints('欣')

with open('../data/person_prefpoint.json', 'w', encoding='utf-8') as f: 
    json.dump(prefPoints, f, ensure_ascii=False)
with open('5_plot/person_prefpoint.json', 'w', encoding='utf-8') as f:
    json.dump(prefPoints, f, ensure_ascii=False)