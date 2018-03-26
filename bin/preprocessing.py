import pandas as pd
import numpy as np
import jieba
import gensim
from nltk.probability import FreqDist

df_review = pd.read_csv('D:\OneDrive\Projects\Independent\Restaurant Review\data\df_review_bj.csv', nrows=2000)

stopwords = [w for l in open(r'..\ref\stopwords\中文停用词库.txt', encoding='GB2312') for w in l.split()]


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
    words = jieba.cut(sentence)
    return words

def remove_stopword(words):
    words = [w for w in words if w not in stopwords]
    return words



model = gensim.models.Word2Vec(tt, min_count=1)


class Df_review:
    def __init__(self, filePath, chunkSize, maxChunk):
        self.df = pd.read_csv(filePath, chunksize=chunkSize)
        self.maxChunk = maxChunk
        self.curChunk = 0
    def __iter__(self):
        for p in self.df:
            if self.curChunk == self.maxChunk: break
            for _, r in p.iterrows():
                yield r
            self.curChunk += 1

df = Df_review('D:\OneDrive\Projects\Independent\Restaurant Review\data\df_review_bj.csv', chunkSize=10000, maxChunk=3)

#Concat sentences
final = []
for r in df:
    sentences = tokenize_sentence(r.Review)
    final += [remove_stopword(tokenize_word(s)) for s in sentences]
print(final)

#Word count
def g(df):
    for r in df:
        sentences = tokenize_sentence(r.Review)
        for s in sentences:
            words = remove_stopword(tokenize_word(s))
            for w in words: yield w

fdist = FreqDist(g(df))