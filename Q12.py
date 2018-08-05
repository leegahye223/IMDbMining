import numpy as np
import re
import pickle
import statsmodels.api as sm

################################################################################

text_file_1 = open("director_movies.txt", "r")
text_file_2 = open("mergeNew.txt","r")
lines1 = text_file_1.read().split('\n')
lines2 = text_file_2.read().split('\n')

################################################################################

""" MOVIE TO DIRECTOR """
movie_to_director = dict()
for i in xrange(0,len(lines1)):
    lines1[i] = re.sub(' \([^0-9I]*?\) ','', lines1[i])
    l = lines1[i].split('\t\t')
    for movies in l[1:]:
        movies = movies.strip()
        movie_to_director[movies] = l[0].strip()

################################################################################

""" DIRECTOR TO MOVIES INDEX """
director_to_movies_index = dict()
for l in xrange(0,100):
    str_movie = lines2[l].strip()
    if str_movie == 'The Matrix (1999)':
        director_name = 'Wachowski, Andy'
    elif str_movie == 'Sen to Chihiro no kamikakushi (2001)':
        director_name = 'Miyazaki, Hayao'
    elif str_movie == 'Modern Times (1936)':
        director_name = 'Chaplin, Charles'
    elif str_movie == 'The Kid (1921)':
        director_name = 'Chaplin, Charles'
    elif str_movie == 'Apocalypse Now (1979)':
        director_name = 'Gural, Stefan'
    else:
        director_name = movie_to_director[str_movie]
    if director_name in director_to_movies_index:
        director_to_movies_index[director_name].append(l)
    else:
        director_to_movies_index[director_name] = [l]


text_file_1.close()
text_file_2.close()
#print(len(director_to_movies_index))
#print director_to_movies_index
#print director_to_movies_index['Spielberg, Steven']

################################################################################

movie_to_rating = dict()
text_file_5 = open("movie_rating.txt", "r")
lines5 = text_file_5.read().split('\n')
for i in xrange(0,len(lines5)-1):
    l = lines5[i].split('\t\t')
    movie_to_rating[l[0].strip()] = float(l[1].strip())

print(movie_to_rating['Pulp Fiction (1994)'])
print(movie_to_rating['Fight Club (1999)'])

################################################################################

text_file_3 = open("actress_movies.txt", "r")
text_file_4 = open("actor_movies.txt", "r")
lines1 = text_file_3.read().split('\n')
lines2 = text_file_4.read().split('\n')

movie_to_actor = dict()

for i in xrange(0,len(lines1)):

    lines1[i] = re.sub(' \([^0-9I]*?\) ','', lines1[i])

    l = lines1[i].split('\t\t')
    for movie in l[1:]:
        movie = movie.strip()
        if movie in movie_to_actor:
            movie_to_actor[movie].append(l[0].strip())
        else:
            movie_to_actor[movie] = [l[0].strip()]


for i in xrange(0,len(lines2)):

    lines2[i] = re.sub(' \([^0-9I]*?\) ','', lines2[i])

    l = lines2[i].split('\t\t')
    for movie in l[1:]:
        movie = movie.strip()
        if movie in movie_to_actor:
            movie_to_actor[movie].append(l[0].strip())
        else:
            movie_to_actor[movie] = [l[0].strip()]

################################################################################
# Removing movies with less than 5 actors

for k in movie_to_actor.keys():

    if (len(movie_to_actor[k]) < 5):
        del movie_to_actor[k]

del movie_to_actor[''] # removing junk data
print (len(movie_to_actor))

################################################################################


text_file_5 = open("pagerank.txt", "r")
lines5 = text_file_5.read().split('\n')
actor_to_pagerank = dict()

for i in xrange(0,len(lines5)-1,2):
    actor = lines5[i].strip()
    pagerank = float(lines5[i+1].strip())
    actor_to_pagerank[actor] = pagerank

print (len(actor_to_pagerank))

################################################################################

count = 0

for movie in movie_to_actor:
    if movie in movie_to_rating:
        page_rank_list = []
        for actor in movie_to_actor[movie]:
            valid_utf8 = True
            try:
                actor.decode('utf-8')
            except UnicodeDecodeError:
                valid_utf8 = False
            if valid_utf8 and (actor in actor_to_pagerank):
                page_rank_list.append(actor_to_pagerank[actor])

        for i in range(0, 5 - len(page_rank_list)):
            page_rank_list.append(0)

        if len(page_rank_list) >= 5:

            page_rank_list = np.asarray(page_rank_list)
            page_rank_list = sorted(page_rank_list[::-1],reverse=True)[0:5]
            page_rank_list = np.reshape(np.array(page_rank_list),[1,5])

            if movie in movie_to_director.keys():
                director = movie_to_director[movie]
            else:
                director = ""
            zero_vector = np.zeros((1,101))

            if director in director_to_movies_index:
                index_list = director_to_movies_index[director]
                np.put(zero_vector,index_list,[1])
            else:
                np.put(zero_vector,[100],[1])

            features = np.hstack((page_rank_list, zero_vector))

            if count == 0:
                combined_features = features
                combined_labels = np.asarray(movie_to_rating[movie])

            else:
                combined_features = np.vstack((combined_features, features))
                combined_labels = np.vstack((combined_labels, movie_to_rating[movie]))

            count = count + 1
            print (count)


pickle.dump(combined_features, open("features_uncollapsed.p", "wb"))
pickle.dump(combined_labels, open("labels_uncollapsed.p", "wb"))


combined_features = pickle.load(open("features_uncollapsed.p", "rb"))

combined_labels = pickle.load(open("labels_uncollapsed.p", "rb"))

results = sm.OLS(combined_labels, combined_features).fit()

pickle.dump(results,open("results_uncollapsed.p","wb"))

print (results.summary())
