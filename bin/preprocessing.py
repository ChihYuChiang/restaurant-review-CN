# this function is to import the stopwords from the .txt file of the stopwords directory. 
def read_words(words_file):
    return [word for line in open(words_file,encoding='utf-8') for word in line.split()]

stopwords = read_words("10_stopwords.txt")


# to jieba segmentize the txt
# to remove the punctuations, space, numbers and stopwords
# and return a list of normalized terms
def txt2words (txt, stopwords = None):
    import re
    import jieba

    jieba.load_userdict("11_seg_dirc.utf8")
    
    # define the Chinese punctuations
    punct='，。－-！？/《》＊#@()＋＝——\n\u3000… '
    
    # Full model segmentation, return a generator, which can be iterated by "for loop"
    seg_list = jieba.cut(txt)
    
    norm_list=[]
    for seg in seg_list:
        # remove the numbers and English punctuations
        seg = re.sub("[A-Za-z0-9\[\`\~\!\@\#\$\^\&\*\(\)\=\|\{\}\'\:\;\'\,\[\]\.\<\>\/\?\~\！\@\#\\\&\*\%]", "", seg)
        # remove Chinese punctuations and spaces
        if seg not in punct:
            if seg not in stopwords:
                norm_list.append(seg)
    # Note: need to return a list of list for Word2Vec to process, because
    # becaue what Word2Vec deal with is a list of sentences, to each sentence, each word islolated by space
    # will be processed as the basic unit; this means each word should be at the third layer of the list
    # we return a list: then each Chinese word is at the second layer, the single character in words are at the 
    # third layer. SO in the this step, need to create word2vec by adding a list
                
    return [norm_list]



#based on the word flag (property of words) to remove time related words and numeric Chinese words, 
#also with other modification to keep meaningful words such as 一二九，九一八，五四 and so on, (takes longer time) 
# Note: the word-flag annotation:
# http://blog.csdn.net/huludan/article/details/52727298


def txt2words_wordflag (txt, stopwords = None):
    import re
    import jieba
    from jieba import posseg
    
    #load the user directory 
    jieba.load_userdict("11_seg_dirc.utf8")
    # load meaningful numerical words
    keepnumerical=['一二五','十一五','六四','九一八','四二六','五四']
    # define the Chinese punctuations
    punct='，。－-！？/《》＊#@（）％＋＝——\n\u3000…  １０２３４５６７８９'
    #define stopwords
    stopwords = read_words("10_stopwords.txt")
    
    # Full model segmentation, return a generator, which can be iterated by "for loop"
    seg_list = posseg.cut(txt)
    
    norm_list=[]
    for seg,flag in seg_list:
        seg = re.sub("[A-Za-z0-9\[\`\~\!\@\#\$\^\&\*\(\)\=\|\{\}\'\:\;\'\,\[\]\.\<\>\/\?\~\！\@\#\\\&\*\%]", "", seg)
        if seg not in punct:
            if seg not in stopwords:
                if seg in keepnumerical:
                    norm_list.append(seg)
                elif flag not in ["m","e","b","p","u", "t", "eng","f"]:
                    #remove single word
                    if len(seg)>1:
                        norm_list.append(seg)
                        
    return [norm_list]

'''
Note: Here I did not flter the low-frequency words!!!
maybe in future we need to do that
'''
