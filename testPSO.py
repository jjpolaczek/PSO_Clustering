import os
import pickle
from library import Book, Library
import logging
import sys
from time import time
from vectorizer import TextVectorizer
from clusterizer import PSO_Clusterizer



logger = logging.getLogger(__name__)

html_dir_path="./books/indexes"
library_listing_file="library_listing.pickle"

with open("vectorised2.pickle", 'rb') as f:
    obj = pickle.load(f)
englishBooks, featureVector = obj

print type(featureVector)
result = PSO_Clusterizer.clusterize(featureVector, no_clusters=10, t_max=5)
print result