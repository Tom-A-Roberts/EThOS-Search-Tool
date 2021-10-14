import spacy
import numpy as np
from sklearn.cluster import KMeans

nlp = None

def load_theses():
    # Load all the thesis
    test_dic = {}

    for i in range(1,51):
        test_text = 'FlaskWebProject/papers/' + f'{i}.txt' 
        #test_text = 'papers/' + f'{i}.txt' 
        with open(test_text,'r') as f:
            test_dic[i] = f.read()
        
    ### Test_dic is the input here ###
    ### result_group_index is the output ###
    return test_dic

#print("Loading theses.")
#input_papers = load_theses()

#def create_word_vectors2(papers):
#    global WORD_VECTOR_PATH, NAMES_ORDER_PATH
#    nlp = spacy.load("en_core_web_lg")
#    matrix = []
#    names_order = []
#    for i in range(1,51):
#        temp = nlp(papers[i])
#        matrix.append(temp.vector)
#        names_order.append(str(i))
    
#    matrix = np.array(matrix)

#    np.savetxt(WORD_VECTOR_PATH, matrix, delimiter=',')
#    #np.savetxt(NAMES_ORDER_PATH, names_order, delimiter=',', fmt="%s")
#    #return matrix
#    with open(NAMES_ORDER_PATH, 'w') as f:
#        for name in names_order:
#            f.write("%s\n" % name)

def create_word_matrix(all_paper_names,RAW_TEXT_PATH, WORD_VECTOR_PATH):
    global nlp
    print("Creating word vectors...")
    
    print("Loading en_core_web_lg...")
    if nlp == None:
        nlp = spacy.load("en_core_web_lg")
    print("Complete")

    matrix = []
    names_order = []

    count = 0
    total = len(all_paper_names)

    print("Calculating word vectors. (May take some time)")

    for paper in all_paper_names:



        with open(RAW_TEXT_PATH + paper + ".txt",'r') as f:  #, encoding="utf8"
            text = f.read()
            temp = nlp(text)



            matrix.append(temp.vector)
            names_order.append(paper)

            np.savetxt(WORD_VECTOR_PATH + str(count) + ".txt", temp.vector, delimiter=',')

            count += 1
            print(str(round(count*100/total)) + "%. Finished vectors for: ", paper)
            

    
    matrix = np.array(matrix)
    print("Finished creating word vectors.")
    return matrix, names_order

def create_word_vector(RAW_TEXT_PATH, paper_name):
    global nlp

    if nlp == None:
        nlp = spacy.load("en_core_web_lg")
    with open(RAW_TEXT_PATH + paper_name + ".txt",'r') as f:  #, encoding="utf8"
        text = f.read()


        nlp.max_length = 2000000
        temp = nlp(text)

        return temp.vector



#create_word_vectors(input_papers)

def read_word_vectors():
    global WORD_VECTOR_PATH, NAMES_ORDER_PATH
    matrix = np.loadtxt(WORD_VECTOR_PATH, delimiter=',')
    name_order = []
    with open(NAMES_ORDER_PATH, 'r') as f:
        texti = f.read().splitlines()
        for name in texti:
            name_order.append(name)
    #print("name order = ", name_order)
    return matrix, name_order

#print("reading word vectors")
#matrix, name_order = read_word_vectors()

    # save the result to csv file
    # matrix_300D_clustering_result_df = pd.DataFrame(result)
    # matrix_300D_clustering_result_df.to_csv('matrix_300D_clustering_result_df.csv')


def most_similar(centroid):
    print("Loading en_core_web_lg...")
    nlp = spacy.load("en_core_web_lg")
    print("Complete")
    vector = np.asarray([centroid])
    ms = nlp.vocab.vectors.most_similar(vector, n=5)
    print("here1")
    words = [nlp.vocab.strings[w] for w in ms[0][0]]
    print("here2")
    distances = ms[2]
    print("done")
    print(words)






def k_means_clustering(word_matrix, name_order, number_of_clusters):
    # Here to implement the k-means with orignal 300-dimension vectors
    # Since it is 300-dimensional, it is hard to visualize.
    estimator = KMeans(n_clusters=number_of_clusters,
                       init='k-means++', 
                       n_init=10, 
                       max_iter=300, 
                       tol=0.0001, 
                       precompute_distances='auto', 
                       verbose=0, 
                       random_state =None, 
                       copy_x=True, n_jobs=-1,algorithm='auto')

    result = np.c_[word_matrix,estimator.fit_predict(word_matrix)]


    label_pred = estimator.labels_ 
    centroids = estimator.cluster_centers_
    inertia = estimator.inertia_




    #print(centroids[0])

    result_group_index= {}
    paper_groups = {}
    for i in range(number_of_clusters):
        index = result == i
        index = index[:,-1]
        index = np.where(index==True)[0]
        result_group_index[i] = index


        paper_groups[i] = []
        for paper_i in index:
            paper_groups[i].append(name_order[paper_i])


        #print(f'group - {i} papers are:',index+1)
        #print(f'group - {i} named papers are:', paper_groups[i])

    return paper_groups






#print("K means clustering.")
#k_means_clustering(matrix, name_order, 10)
#print("Done.")













# Here to begin give the tags
### test_dic is the output !
#group_number = 10

#def generate_key_tags(group_id): # return the corresponding gruop tag
#    integrated_text  = ''
#    for i in result_group_index[group_id]:
#        integrated_text += test_dic[i+1]
#    sentence_set,sentence_with_index = ATS.split_sentence(integrated_text, punctuation_list="!.?")
#    tfidf_matrix = ATS.get_tfidf_matrix(sentence_set, data_processing.get_stop_word())
#    sentence_with_words_weight = ATS.get_sentence_with_words_weight(tfidf_matrix)
##         print('tf-idf scores are:\n',sentence_with_words_weight)
#    sentence_with_position_weight = ATS.get_sentence_with_position_weight(sentence_set)
#    sentence_score = ATS.get_similarity_weight(tfidf_matrix)
#    sort_sent_weight = ATS.ranking_base_on_weigth(sentence_with_words_weight,
#                                                sentence_with_position_weight,
#                                                sentence_score, feature_weight = [0.9,0.05,0.05])
#    summarization = ATS.get_summarization(sentence_with_index,sort_sent_weight,topK_ratio =0.0001)
#    return summarization
# output 👇
#tag_result = {}
#for i in range(group_number):
    #tag_result[i] = generate_key_tags(i)
    #print(f'group - {i} tag is:\n {tag_result[i]}\n')