import bz2
import numpy as np

#--Existing embedding
#https://github.com/Embedding/Chinese-Word-Vectors

def readEmbedding(filePath):

    with bz2.open(filePath, 'rt', encoding='utf-8') as f:
        #Skip the first line (file meta data)
        f.readline()

        words = set()
        word_to_vec_map = {}
        for line in enumerate(f):
            line = line.strip().split()
            curr_word = line[0]
            words.add(curr_word)
            word_to_vec_map[curr_word] = np.array(line[1:], dtype=np.float64)
        
        i = 1
        words_to_index = {}
        index_to_words = {}
        for w in sorted(words):
            words_to_index[w] = i
            index_to_words[i] = w
            i = i + 1

    return words_to_index, index_to_words, word_to_vec_map

#Acquire mappings
word_to_index, index_to_word, word_to_vec_map = readEmbedding('../data/weibo/sgns.weibo.word.bz2')


#--Update