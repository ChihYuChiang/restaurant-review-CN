import bz2
import numpy as np


'''
------------------------------------------------------------
Existing embedding

- https://github.com/Embedding/Chinese-Word-Vectors
------------------------------------------------------------
'''
def readEmbedding(filePath):

    with bz2.open(filePath, 'rt', encoding='utf-8') as f:
        #Skip the first line (file meta data)
        f.readline()

        words = set()
        word_to_vec_map = {}
        for line in f:
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




'''
------------------------------------------------------------
Explore embedding
------------------------------------------------------------
'''
#--Cosine similarity
#1 = the same; -1 = the opposite
def cosineSimilarity(u, v):
    
    #Compute the dot product between u and v
    dot = np.dot(u, v)

    #Compute the L2 norm of u and v
    norm_u = np.linalg.norm(u)
    norm_v = np.linalg.norm(v)

    #Compute the cosine similarity
    cosine_similarity = dot / (norm_u * norm_v)
    
    return cosine_similarity

#Samples
father = word_to_vec_map['爸爸']
mother = word_to_vec_map['妈妈']
ball = word_to_vec_map['球']
crocodile = word_to_vec_map['鳄鱼']
france = word_to_vec_map['法国']
italy = word_to_vec_map['意大利']
paris = word_to_vec_map['巴黎']
rome = word_to_vec_map['罗马']

print('cosine_similarity(father, mother) = ', cosineSimilarity(father, mother))
print('cosine_similarity(ball, crocodile) = ',cosineSimilarity(ball, crocodile))
print('cosine_similarity(france - paris, rome - italy) = ',cosineSimilarity(france - paris, rome - italy))


#--Analogy task
#a is to b as c is to ____ 
def analogy(word_a, word_b, word_c):
    
    #Get the word embeddings v_a, v_b and v_c
    v_a, v_b, v_c = word_to_vec_map[word_a], word_to_vec_map[word_b], word_to_vec_map[word_c]
    
    words = word_to_vec_map.keys()
    max_cosine_sim = -100 #Initialize max_cosine_sim to a large negative number
    best_word = None #Initialize best_word with None

    #Loop over the whole word set
    for w in words:

        #Avoid best_word being one of the input words
        if w in [word_a, word_b, word_c] :
            continue
        
        #Compute cosine similarity between the vector (v_b - v_a) and the vector (v_d - v_c) 
        cosine_sim = cosineSimilarity(v_b - v_a, word_to_vec_map[w] - v_c)
        
        #Update the best fit word
        if cosine_sim > max_cosine_sim:
            max_cosine_sim = cosine_sim
            best_word = w
            
    return best_word

#Samples
triad = ('意大利', '罗马', '西班牙')
triad = ('中国', '台湾', '美国')
triad = ('老公', '男人', '老婆')
triad = ('东方', '武功', '西方')
print ('{} -> {} :: {} -> {}'.format(*triad, analogy(*triad)))




'''
------------------------------------------------------------
Update embedding
------------------------------------------------------------
'''