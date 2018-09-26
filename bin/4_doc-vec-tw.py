import pandas as pd
import numpy as np
import re
import jieba
import pickle
from pprint import pprint
from hanziconv import HanziConv




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
def preprocess(df=df_review):

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

text_preprocessed = preprocess()




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

    return docVecs

docVecs = getDocVec(text_preprocessed, word_to_vec_map)




'''
------------------------------------------------------------
2D projection
------------------------------------------------------------
'''







'''
------------------------------------------------------------
Preference visualization
------------------------------------------------------------
'''