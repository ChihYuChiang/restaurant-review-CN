import bz2
import numpy as np
import tensorflow as tf
from collections import Counter


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
emb_matrix = np.zeros((emb_m, emb_n))

for word, index in word_to_index.items():
    emb_matrix[index, :] = word_to_vec_map[word]




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
Update embedding by restaurant corpus

- https://nlp.stanford.edu/pubs/glove.pdf
------------------------------------------------------------
'''
with open(r'..\data\preprocessed.pickle', 'rb') as f:
    text_preprocessed = pickle.load(f)

text_preprocessed = [['东方', '武功', '西方'], ['意大利', '罗马', '西班牙', '东方', '武功', '西方', '东方', '武功', '西方'], ['老公', '男人', '老婆', '中国', '台湾', '美国'], ['东方', '武功', '西方']]


#--Word co-occurrence
coOccurDic = Counter()
WIN = 5

for s in text_preprocessed:
    for i in np.arange(len(s)):
        for j in np.arange(i + 1, min(i + WIN + 1, len(s))):
            try:
                i_idx = word_to_index[s[i]]
                j_idx = word_to_index[s[j]]
            except: continue

            if i_idx == j_idx: continue

            coOccurDic[str(min(i_idx, j_idx)) + '-' + str(max(i_idx, j_idx))] += 1


#--Initialization
tf.reset_default_graph()
learning_rate = 0.01

x_nPair = len(coOccurDic)
x_max = coOccurDic.most_common(1)[0][1]

#Weighting function
def wFunc(nCoOccur, cutoff):
    w = (nCoOccur / cutoff) ** (3/4) if nCoOccur < cutoff else 1
    return w

#Variables to be learnt
embedding = tf.get_variable('embedding', dtype=tf.float32, initializer=tf.constant(emb_matrix))
b_i = tf.get_variable("b_i", [x_nPair, 1], dtype=tf.float32, initializer=tf.zeros_initializer())
b_j = tf.get_variable("b_j", [x_nPair, 1], dtype=tf.float32, initializer=tf.zeros_initializer())

#Input and output
x_ij = tf.placeholder(tf.float32, name='x_ij')
w_ij = tf.placeholder(tf.float32, name='w_ij')
id_i = tf.placeholder(tf.int32, name='id_i')
id_j = tf.placeholder(tf.int32, name='id_j')

#Intermediate
v_i = tf.nn.embedding_lookup(embedding, id_i, name='v_i')
v_j = tf.nn.embedding_lookup(embedding, id_j, name='v_j')
oh_i = tf.one_hot(indices=[id_i], depth=emb_m, dtype=tf.float32)
oh_j = tf.one_hot(indices=[id_j], depth=emb_m, dtype=tf.float32)

#Cost
cost = w_ij * tf.square(tf.matmul(v_i, v_j, transpose_b=True) + tf.matmul(oh_i, b_i) + tf.matmul(oh_j, b_j) - tf.log(x_ij))

#Optimizer and initializer
optimizer = tf.train.AdamOptimizer(learning_rate).minimize(cost)
init = tf.global_variables_initializer()


#--Training
costs = []
with tf.Session() as sess:
    temp = np.array([[1.0],[2.0],[3.0],[4.0],[5.0]])
    test0 = tf.matmul(tf.one_hot(indices=[4], depth=5, dtype=tf.float64), temp)
    test1 = tf.one_hot(indices=[4], depth=5, dtype=tf.float64)
    test2 = tf.one_hot(indices=[3], depth=5, dtype=tf.float64)
    test3 = tf.matmul(test1, test2, transpose_b=True)
    test4 = np.log(5)
    testp = sess.run(test4)
    print(testp)



    sess.run(init)

    for epoch in range(nEpoch):
        _, epoch_cost = sess.run([optimizer, cost])

        for pair in pairs:

            #Select a minibatch
            (minibatch_X, minibatch_Y) = minibatch
            #IMPORTANT: The line that runs the graph on a minibatch.
            #Run the session to execute the optimizer and the cost, the feedict should contain a minibatch for (X,Y).
            _ , temp_cost = sess.run([optimizer, cost], feed_dict={X: minibatch_X, Y: minibatch_Y})
            
            minibatch_cost += temp_cost / num_minibatches

            if epoch % 100 == 0:
                print ('Cost after epoch %i: %f' % (epoch, epoch_cost))
            if epoch % 5 == 0:
                costs.append(epoch_cost)

    plt.plot(np.squeeze(costs))
    plt.ylabel('cost')
    plt.xlabel('iterations (per fives)')
    plt.title("Learning rate =" + str(learning_rate))
    plt.show()
    plt.close()

    w_trained = sess.run(w)
