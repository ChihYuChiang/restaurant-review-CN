import pandas as pd
import numpy as np
import re
import operator
import jieba
from nltk.probability import FreqDist


df_review_sp = pd.read_csv('D:\OneDrive\Projects\Independent\Restaurant Review\data\df_review_bj.csv', nrows=100) + 

stopwords = list(set([w for l in open(r'..\ref\stopwords\中文停用词库.txt', encoding='GB2312') for w in l.split()] + [w for l in open(r'..\ref\stopwords\哈工大停用词表.txt', encoding='GBK') for w in l.split()]))

def tokenize_sentence(doc):
    punList = ',.!?:;~，。！？：；～'
    senStart = 0
    sentences = []
    for i in np.arange(len(doc) - 1):
        if doc[i] in punList and doc[i + 1] not in punList:
            sentences.append(doc[senStart : i + 1])
            senStart = i + 1
    if senStart < len(doc): sentences.append(doc[senStart: ])
    return sentences

def tokenize_word(sentence):
    sentence = re.sub('(\\xa0)+', ' ', sentence)
    sentence = re.sub('\s+', ' ', sentence)
    words = jieba.cut(sentence)
    return words

def remove_stopword(words):
    words = [w for w in words if w not in stopwords]
    return words

class Df_review:
    def __init__(self, filePath, chunkSize, maxChunk):
        self.df = pd.read_csv(filePath, chunksize=chunkSize)
        self.maxChunk = maxChunk
        self.curChunk = 0
    def __iter__(self):
        for p in self.df:
            if self.curChunk == self.maxChunk: break
            print('Start processing chunk', p)
            self.curChunk += 1
            yield from p.iterrows()

df = Df_review('D:\OneDrive\Projects\Independent\Restaurant Review\data\df_review_bj.csv', chunkSize=50000, maxChunk=None)

#Concat sentences
final = []
for _, r in df:
    sentences = tokenize_sentence(r.Review)
    final += [remove_stopword(tokenize_word(s)) for s in sentences]
print(final)

#Word count
def g(df):
    for _, r in df:
        sentences = tokenize_sentence(r.Review)
        for s in sentences:
            words = remove_stopword(tokenize_word(s))
            for w in words: yield w
fdist = FreqDist(g(df))
fdist.B() #Distinct word
fdist.N() #Total word
sorted(fdist.items(), key=operator.itemgetter(1), reverse=True)


def flatten(l):
    import collections
    for el in l:
        if isinstance(el, collections.Sequence) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

[i for i in flatten(final[:10])]