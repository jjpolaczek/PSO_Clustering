import numpy as np
import os
import pickle
import logging

logger = logging.getLogger(__name__)

class PSO_Clusterizer():
    def __init__(self):
        pass

    def _fitness(self, dataset, particle, assignment):
    def clusterize(self, dataset, no_clusters, t_max=100):
        #ensure data is normalized 0-1
        #create Nc centroid vectors
        # MAin loop algorithm iteration:
            #For reach particle do:
                #for each data vector
                    #calculate the Euclidean distance for all centroids
                    #Assign particles to clusters based on the distance (closest first)
                    #Calculate overall fitness of the particle
                #Update global best and local best positiosn
                #Update cluster centroids
            #Check end condition
        pass