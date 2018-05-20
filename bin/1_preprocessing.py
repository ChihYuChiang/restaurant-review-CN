import pandas as pd
import numpy as np
import re
import operator
import jieba
import pickle
from nltk.probability import FreqDist

#Raw file path
FILE_PATH = 'D:\OneDrive\Projects\Independent\Restaurant Review\data\df_review_bj.csv'

#Sample df, for observation only
df_review_sp = pd.read_csv(FILE_PATH, nrows=100)

#Combine stopword lists and remove duplicates
stopwords = list(set([w for l in open(r'..\ref\stopwords\中文停用词库.txt', encoding='GB2312') for w in l.split()] + [w for l in open(r'..\ref\stopwords\哈工大停用词表.txt', encoding='GBK') for w in l.split()]))




'''
------------------------------------------------------------
Utility functions
------------------------------------------------------------
'''
#--Flatten list (recursive)
#Parameter: l, a list
#Return: a flattened list as a generator
def flatten_list(l):
    import collections
    for el in l:
        if isinstance(el, collections.Sequence) and not isinstance(el, (str, bytes)):
            yield from flatten_list(el)
        else:
            yield el


#--Separate sentences
#Parameter: doc, a str
#Return: a list of strs (sentences)
def tokenize_sentence(doc):
    punList = ',.!?:;~，。！？：；～'
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
    sentence = re.sub('\s+', ' ', sentence)
    words = jieba.cut(sentence)
    return words


#--Remove stopwords
#Parameters: words, a list of str; stopwords, a list of str
#Return: a list of words with stopwords removed
def remove_stopword(words, stopwords):
    words = [w for w in words if w not in stopwords]
    return words


#--A df_review row generator
#Parameters: chunkSize and maxChunk both int
#The actual num of rows will be generated = chunkSize * maxChunk
class Df_review:
    def __init__(self, filePath, chunkSize, maxChunk):
        self.df = pd.read_csv(filePath, chunksize=chunkSize)
        self.maxChunk = maxChunk
        self.curChunk = 0
    def __iter__(self):
        for p in self.df:
            if self.curChunk == self.maxChunk: break
            print('Start processing chunk', self.curChunk)
            self.curChunk += 1
            yield from p.iterrows()




'''
------------------------------------------------------------
Preprocessing
------------------------------------------------------------
'''
#--Tokenize and preprocessing by each doc
#Df row generator
df = Df_review(FILE_PATH, chunkSize=50000, maxChunk=None)

#Preprocessing
text_preprocessed = []
for _, r in df:
    sentences = tokenize_sentence(r.Review)
    text_preprocessed.append([remove_stopword(tokenize_word(s), stopwords=stopwords) for s in sentences])

#Observe result
print(text_preprocessed[:10])

#Save result
with open(r'..\data\preprocessed.pickle', 'wb') as f:
    pickle.dump(text_preprocessed, f)


#--Word count (all docs)
#Word frequency distribution by nltk
fdist = FreqDist([i for i in flatten_list(text_preprocessed)])

#Observe result
print('Unique terms:', fdist.B())
print('Total terms:', fdist.N())
sorted(fdist.items(), key=operator.itemgetter(1), reverse=True) #Top terms

#Save result
with open(r'..\data\fdist.pickle', 'wb') as f:
    pickle.dump(fdist, f)



#--Tf-idf is costly and has to be decided if implement