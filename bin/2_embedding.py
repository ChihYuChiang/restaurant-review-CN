import bz2
import numpy as np
import pickle
import tensorflow as tf
import matplotlib.pyplot as plt
from collections import Counter
from itertools import islice

#Preprocessed restaurant distribution
with open(r'..\data\fdist.pickle', 'rb') as f:
    fdist = pickle.load(f)


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

            #Include only words in the restaurant corpus
            if curr_word in fdist:
                words.add(curr_word)
                word_to_vec_map[curr_word] = np.array(line[1:], dtype=np.float64)
            else: continue
        
        i = 1
        word_to_index = {}
        index_to_word = {}
        for w in sorted(words):
            word_to_index[w] = i
            index_to_word[i] = w
            i = i + 1

    return word_to_index, index_to_word, word_to_vec_map

#Acquire mappings
word_to_index, index_to_word, word_to_vec_map = readEmbedding('../data/weibo/sgns.weibo.word.bz2')

#Acquire numpy embedding matrix
emb_m = len(word_to_index) + 1 #Number of words
emb_n = 300 #Number of dimension
emb_matrix = np.zeros((emb_m, emb_n), dtype=np.float32)

for word, index in word_to_index.items():
    emb_matrix[index, :] = word_to_vec_map[word]

#Log in console
print('Raw embedding read and processed..')




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
Update embedding by restaurant corpus (GloVe)

- https://nlp.stanford.edu/pubs/glove.pdf
------------------------------------------------------------
'''
#--Word co-occurrence
with open(r'..\data\preprocessed.pickle', 'rb') as f:
    text_preprocessed = pickle.load(f)

coOccurDic = Counter()
WIN = 5 #The co-occurrence window

#Produce co-occurrence dict
#Result format = word_id-word_id: n_co-occurrence
for review in text_preprocessed:
    for sentense in review:
        for i in np.arange(len(sentense)):
            for j in np.arange(i + 1, min(i + WIN + 1, len(sentense))):
                try:
                    i_idx = word_to_index[sentense[i]]
                    j_idx = word_to_index[sentense[j]]
                except: continue

                if i_idx == j_idx: continue

                coOccurDic[str(min(i_idx, j_idx)) + '-' + str(max(i_idx, j_idx))] += 1

#Log in console
print('Co-occurrence dictionary created..')

#Examine co-occurrence result (top 10)
coOccurDic.most_common(10)


#--Initialization
tf.reset_default_graph()

#Parameters
np.random.seed(1)
learningRate = 0.001
nPairPerBatch = 500
x_m = len(coOccurDic) #Number of training sample
x_max = coOccurDic.most_common(1)[0][1] #Number of the most common co-occurrence

#Randomize the co-occur dict
permutation = list(np.random.permutation(x_m))
temp = [item for item in coOccurDic.items()]
coOccur_rand = [temp[idx] for idx in permutation]

#Produce batches
def genBatches(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]
batches = genBatches(coOccur_rand, nPairPerBatch)

#Weighting function
def wFunc(nCoOccur, cutoff):
    w = (nCoOccur / cutoff) ** (3/4) if nCoOccur < cutoff else 1
    return w

#Variables to be learnt
embedding = tf.get_variable('embedding', dtype=tf.float32, initializer=tf.constant(emb_matrix))
b_i = tf.get_variable("b_i", [emb_m, 1], dtype=tf.float32, initializer=tf.zeros_initializer())
b_j = tf.get_variable("b_j", [emb_m, 1], dtype=tf.float32, initializer=tf.zeros_initializer())

#Input and output
x_ij = tf.placeholder(tf.float32, name='x_ij')
w_ij = tf.placeholder(tf.float32, name='w_ij')
id_i = tf.placeholder(tf.int32, name='id_i')
id_j = tf.placeholder(tf.int32, name='id_j')

#Intermediate
v_i = tf.nn.embedding_lookup(embedding, id_i, name='v_i')
v_j = tf.nn.embedding_lookup(embedding, id_j, name='v_j')
oh_i = tf.one_hot(indices=id_i, depth=emb_m, dtype=tf.float32)
oh_j = tf.one_hot(indices=id_j, depth=emb_m, dtype=tf.float32)

#Cost
cost = w_ij * tf.square(tf.matmul(v_i, v_j, transpose_b=True) + tf.matmul(oh_i, b_i) + tf.matmul(oh_j, b_j) - tf.log(x_ij))

#Optimizer, initializer, saver
optimizer = tf.train.AdamOptimizer(learningRate).minimize(cost)
init = tf.global_variables_initializer()
saver = tf.train.Saver(max_to_keep=1) #Keep only the last version (it's 500MB per version..)

#Log in console
print('Model initialized..')


#--Model
def updateEmb(startBatch, nBatch):
    costs = []
    with tf.Session() as sess:

        #Initialize vars/restore from checkpoint
        if startBatch == 0: sess.run(init)
        else: saver.restore(sess, './../data/checkpoint/emb-update-{}'.format(startBatch))

        for i, batch in enumerate(islice(batches, startBatch, startBatch + nBatch)):
            #Get track of the cost of each batch
            cost_batch = 0

            for item in batch:
                _, cost_item = sess.run([optimizer, cost],
                    #Id must be a list, so the lookup results would be 2d instead of 1d and therefore can perform tf.matmul
                    feed_dict={
                        x_ij: item[1],
                        w_ij: wFunc(item[1], x_max),
                        id_i: [int(str.split(item[0], '-')[0])],
                        id_j: [int(str.split(item[0], '-')[1])]
                    }
                )

                #Tally the cost for each batch
                cost_batch += cost_item

            if i % 1 == 0: #For text printing
                print ('Cost after batch %i: %f' % (startBatch + i, cost_batch))
            if i % 1 == 0: #For graphing
                costs.append(cost_batch)

        #Graphing the change of the costs
        plt.plot(np.squeeze(costs))
        plt.ylabel('cost')
        plt.xlabel('iterations (per batch)')
        plt.title("Learning rate =" + str(learningRate))
        plt.show()
        plt.close()

        #Checkpoint
        saver.save(sess, './../data/checkpoint/emb-update', global_step=startBatch + nBatch)


#--Training
updateEmb(startBatch=300, nBatch=200)


#--Output
#Acquire output after certain number of global steps
AFTER_STEP = 1

with tf.Session() as sess:
    saver.restore(sess, './../data/checkpoint/emb-update-{}'.format(AFTER_STEP))

    embedding_updated = sess.run(embedding)
    print(embedding_updated)
