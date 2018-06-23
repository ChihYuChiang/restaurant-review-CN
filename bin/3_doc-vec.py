import pickle
import numpy as np

#--Data
#Preprocessed restaurant data
with open(r'..\data\preprocessed_all.pickle', 'rb') as f:
    text_preprocessed, marker_shopId = pickle.load(f)

#Preprocessed embedding data
with open(r'..\data\emb_raw.pickle', 'rb') as f:
    word_to_vec_map = pickle.load(f)
with open(r'..\data\emb_updated.pickle', 'rb') as f:
    word_to_vec_map_updated = pickle.load(f)


#--Doc vec to summary vec
#Average across words of a store to acquire store (doc) vec
#Average across doc vecs to acquire summary vec
def summaryVec(text_preprocessed, word_to_vec_map):

    #Vecs for all documents
    docVecs = []
    wordVecs = []
    marker_last = marker_shopId[0]

    #Loop over each review
    for i in range(len(text_preprocessed)):
        
        #If different store, compute the docVec for that store
        if marker_last != marker_shopId[i]:
            
            #Average vec of all word
            wordVecs = np.array(wordVecs)
            docVec = np.mean(wordVecs, axis=0)

            #Update docVecs
            docVecs.append(docVec)

            #Reset wordVecs
            wordVecs = []

        #Acquire vec of each word
        for s in text_preprocessed[i]:
            for w in s:
                if w in word_to_vec_map.keys(): wordVecs.append(word_to_vec_map[w])
        
        #Update marker
        marker_last = marker_shopId[i]

    #Average vec of all documents
    docVecs = np.array(docVecs)
    print(docVecs.shape)
    summary = np.mean(docVecs, axis=0)

    return summary


#--Summary vecs
#All stores
summary_all = summaryVec(text_preprocessed, word_to_vec_map)
