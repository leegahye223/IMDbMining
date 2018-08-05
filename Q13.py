import re
import codecs
from igraph import Graph
from collections import defaultdict
from heapq import nlargest
from sklearn.metrics import mean_squared_error
from math import sqrt

################################################################################
#regex = re.compile('[^a-zA-Z0-9\t ]')
#regex_rate = re.compile('[^a-zA-Z0-9\t. ]')

with open("actor_movies.txt",'r') as f:
	read_data = f.readlines()
with open("actress_movies.txt",'r') as f:
	read_data += f.readlines()	

movie_dict = defaultdict(list)
acting = defaultdict(list)

for line in read_data:
	content_dirty = line.strip()
	content_clean = regex.sub('', content_dirty).strip()
	content = content_clean.split("\t\t")
	if len(content) >= 11:
	    name = content[0]
	    movies = [m.strip() for m in content[1:]]
	    acting[name.strip()] = movies
	    for m in movies:
	        movie_dict[m].append(name)

edges = list()
# count = 0
for actor in acting:
	movies = acting[actor]
	for movie in movies:
		# count = count + 1
		# print count 
		edges.append((actor.strip(),movie.strip()))

graph = Graph.TupleList(edges, directed = False)
# print graph.vs["name"]

############################################################
with open("movie_rating.txt",'r') as f:
	movie_ratings = f.readlines()

movie_rating_pair = dict()
for line in movie_ratings:
	content_dirty = line.strip()
	content_clean = regex_rate.sub('', content_dirty).strip()
	content = content_clean.split('\t\t')
	if len(content) < 2:
		continue
	else:
		rating = content[1].strip()
		movie = regex.sub('', content[0]).strip()
		movie_rating_pair[movie] = float(rating)
# print len(movie_rating_pair.keys())
###########################################################
actor_rating = {}
for actor in acting:
	actor = actor.strip()
	try:
		actor_id = graph.vs.find(actor).index
	except:
		continue
	temp = []
	nei = graph.neighbors(actor_id)
	for v in nei:
		# print graph.vs[v]["name"]
		if graph.vs[v]["name"] in movie_rating_pair:
			temp.append(movie_rating_pair[graph.vs[v]["name"]])

	top_10 = nlargest(10,temp)
	if temp:
		actor_rating[actor] = float(sum(top_10))/len(top_10)	
		# actor_rating[actor] = float(sum(temp))/len(temp)
###########################################################

movie_list = "Batman v Superman: Dawn of Justice (2016)\t Mission: Impossible - Rogue Nation (2015)\t Minions (2015)"
content_dirty = movie_list.strip()
content_clean = regex.sub('', content_dirty).strip()
movie_list = content_clean.split("\t")

feature = list()
features_test = list()
y_predicted = []

for movie in movie_list:
	movie_vert = graph.vs.find(movie.strip()).index
	actors = graph.neighbors(movie_vert)
	rates = []
	for a in actors:
	    if graph.vs[a]["name"] in actor_rating:
		rates.append(actor_rating[graph.vs[a]["name"]])
	top_10_test = nlargest(10,rates)
	rate = round(float(sum(top_10_test))/len(top_10_test), 5)
	# rate = round(float(sum(rates))/len(rates), 5)
	y_predicted.append(rate)
	print movie,": ",rate

y_actual = [6.6,7.4,6.4]
rms = sqrt(mean_squared_error(y_actual, y_predicted))
print "RMSE: ",rms