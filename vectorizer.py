import os
import pickle
from library import Book, Library
import logging
import sys
from time import time
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer


logger = logging.getLogger(__name__)

VECTORIZED_FILE_CHECKPOINT = "feature_vector.pickle"
LSA_FILE_CHECKPOINT = "lsa_vector.pickle"


class TextVectorizer():
    def __init__(self, bookList, opts):
        self.opts=opts
        self.bookList=bookList
        self.tmpVectorisedFile1 = VECTORIZED_FILE_CHECKPOINT
        self.tmpVectorisedFile2 = LSA_FILE_CHECKPOINT

    def process(self):
        # Vectorizer settings
        logger.info("Extracting features from the training dataset using a sparse vectorizer")
        t0 = time()

        vectorizer = TfidfVectorizer(max_df=0.5, max_features=self.opts.n_features,
                                         min_df=2, stop_words='english',
                                         use_idf=True)


        X = vectorizer.fit_transform(self.bookList)
        logger.info("done in %fs", (time() - t0))
        logger.info("n_samples: %d, n_features: %d\n" % X.shape)
        logger.info("Saving feature vector to %s\n" % self.tmpVectorisedFile1)

        vectorisedData = (self.bookList, X)

        with open(self.tmpVectorisedFile1, 'wb') as f:
            pickle.dump(vectorisedData, f, pickle.HIGHEST_PROTOCOL)

        if self.opts.n_components:
            logger.info("Performing dimensionality reduction using LSA")
            t0 = time()
            # Vectorizer results are normalized, which makes KMeans behave as
            # spherical k-means for better results. Since LSA/SVD results are
            # not normalized, we have to redo the normalization.
            svd = TruncatedSVD(self.opts.n_components)
            normalizer = Normalizer(copy=False)
            lsa = make_pipeline(svd, normalizer)

            X = lsa.fit_transform(X)

            logger.info("done in %fs", (time() - t0))

            explained_variance = svd.explained_variance_ratio_.sum()
            logger.info("Explained variance of the SVD step: %d\n", int(explained_variance * 100))

            logger.info("Saving LSA output vector to %s\n" % self.tmpVectorisedFile2)
            vectorisedData = (self.bookList, X)
            with open(self.tmpVectorisedFile2, 'wb') as f:
                pickle.dump(vectorisedData, f, pickle.HIGHEST_PROTOCOL)



        logger.info("Extracted feature vector of %d dimensions, shape: %s", X.shape[1], X.shape)
        return vectorisedData
    def loadCheckpoint(self):
        with open(self.tmpVectorisedFile2, 'rb') as f:
            obj = pickle.load(f)
        return obj