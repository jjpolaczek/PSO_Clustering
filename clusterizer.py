import numpy as np
import os
import pickle
import logging
import time
logger = logging.getLogger(__name__)

class PSO_Clusterizer():

    @staticmethod
    def _fitness(eDist, particle, assignment):
        no_clusters = particle.shape[0]
        # calculate cluster assignment number
        unique, counts = np.unique(assignment, return_counts=True)
        assignmentStats = dict(zip(unique, counts))
        #transform to frequency
#        print eDist.shape[0]
#        for cluster in assignmentStats:
#            assignmentStats[cluster] = float(assignmentStats[cluster]) / eDist.shape[0]

        #print assignmentStats
        #Get sum of distances for each cluster
        clusterPerf =  np.sum(eDist, axis=0)
        fitness = 0.0
        for cluster in range(no_clusters):
            if cluster not in assignmentStats:
                #Cluster is empty penalty
                fitness += clusterPerf[cluster] * 10
            else:
                fitness += clusterPerf[cluster] / assignmentStats[cluster]

        fitness /= no_clusters
        return fitness
    @staticmethod
    def clusterize(dataset, no_clusters, t_max=10, no_particles=None):
        np.random.seed()
        no_dims = dataset.shape[1]
        no_data = dataset.shape[0]
        if no_particles is None:
            no_particles = 4 * no_dims * no_clusters
        #ensure data is normalized 0-1
        minVal = np.amin(dataset)
        maxVal = np.amax(dataset)
        dataset -= minVal
        dataset *= (1/(maxVal-minVal))
        #create Nc centroid vectors
        # 0dim: particle 1dim: centroid 2dim:dimension position
        particles = np.random.rand(no_particles, no_clusters, no_dims)
        #create temporary euclidean dist representation
        eDist=np.zeros((no_data, no_clusters))
        tmpAsign = np.zeros((no_data, 1))
        print "Created %d, %d dimensional particles of %d clusters (%d dimensional problem)" % (no_particles, no_dims, no_clusters, no_dims * no_clusters)

        ##Particle temporary parameters
        #particle weight w
        w = 0.9
        # individual coefficient (local)
        c1=0.6
        # social coefficient (global)
        c2=0.5
        prevV=np.zeros((no_particles, no_clusters, no_dims))
        pBest=np.zeros((no_particles, no_clusters, no_dims))
        pBest_val = no_particles * [float("inf")]
        gBest= np.random.rand(no_clusters, no_dims)
        gBest_val = float("inf")
        fitness=np.zeros(no_particles)

        last_score = float("inf")
        no_stalls=0
        # Main loop algorithm iteration:
        for iteration in xrange(t_max):
            print "Iteration %d/%d" % (iteration, t_max)

            for i in xrange(no_particles):
                particle = particles[i,:,:]

                # calculate the Euclidean distance for all centroids
                #eDist[:,:] = np.sqrt(np.sum(np.power(dataset[:, None, :] - particle[None, :, :], 2), axis=-1))
                for c in xrange(no_clusters):
                    eDist[:, c] = np.linalg.norm(particle[c, :] - dataset, axis=-1)

                #Assign data points to clusters based on the distance (closest first)
                tmpAsign = np.argmin(eDist, axis=-1)
                # Calculate overall fitness of the particle
                fitness[i] = PSO_Clusterizer._fitness(eDist, particle, tmpAsign)

                # Save best cognitive particle
                if fitness[i] < pBest_val[i]:
                    pBest_val[i] = fitness[i]
                    pBest[i, :, :] = particle
            #Handle update of all particles positions

            # get best global value
            gbest_idx = np.argmin(fitness, axis=-1)
            if fitness[gbest_idx] < gBest_val:
                gBest_val = fitness[gbest_idx]
                gBest=particles[gbest_idx, :, :]

            #update particle velocity and position
            for i in xrange(no_particles):
                # Three components: 1: weight times previous velocity, 2: local optimum heuristic, 3: global optimum heuristic
                prevV[i, :, :] = w*prevV[i, :, :] + c1*np.random.rand()*(pBest[i, :, :]-particles[i, :, :]) + c2*np.random.rand()*(gBest-particles[i, :, :])
                #print prevV[i, :, :]
                particles[i, :, :] += prevV[i, :, :]

            #update inertia cofficient linearly
            w = 0.4 + float(t_max - iteration)/t_max * 0.5
            print "Fitness: ", gBest_val
            #convergence criteria logic:
            if last_score != float("inf"):
                pChange = (last_score - gBest_val) / gBest_val
                if pChange < 0.01:
                    no_stalls += 1
                    if no_stalls > 2:
                        print "Convergence criteria reached"
                        break
            last_score=gBest_val

        # get best particle asignments
        best_particle = particles[gbest_idx, :, :]
        # calculate the Euclidean distance for all centroids
        for c in xrange(no_clusters):
            eDist[:, c] = np.linalg.norm(best_particle[c, :] - dataset, axis=-1)
        result =  np.argmin(eDist, axis=-1)

        unique, counts = np.unique(result, return_counts=True)
        print "Label histogram:"
        rdict = dict(zip(unique, counts))
        print rdict
        print "Best Fitness: ", gBest_val
        if no_dims < 10:
            print "\nCluster coordinates:"
            print gBest*(maxVal-minVal) + minVal
        return result, gBest_val, gBest
            #Check end condition
