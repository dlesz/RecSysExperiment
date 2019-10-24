import time
import logging
from scipy.sparse import csr_matrix
import numpy as np
from implicit.als import AlternatingLeastSquares
import json
import pandas as pd
import os
import os.path
import pickle
import h5py
from implicit.nearest_neighbours import (bm25_weight)


class Model:
    def __init__(self, dev=bool):
        logger = logging.getLogger()
        logging.basicConfig(level=logging.DEBUG)
        
        logging.debug('loading data')
        self.artists, self.users, self.plays = self.read_lastfm_data('data/lastfm_360k.hdf5')
        
        self.profile_dict = self.read_json('data/profile_dict.json')
        self.profile_dict = {int(k): v for k, v in self.profile_dict.items()}
        
        self.tag_frequency_dict = self.read_json('data/profile_tag_frequency_dict.json')
        self.tag_frequency_dict = {int(k): v for k, v in self.tag_frequency_dict.items()}
        
        self.artist_tag_dict = self.read_json('data/artists_tags_dict.json')
        self.artist_tag_dict = {int(k): v for k, v in self.artist_tag_dict.items()}
        
        self.tag_set = self.read_tags_meta = pd.read_csv('data/tag_set.csv')
        self.tag_set = list(self.tag_set['0'])
        
        # user indices used to randomly shuffle through the indices/users in the matrix
        self.user_indices = np.unique(self.plays.indices)
        self.user_indices = np.sort(self.user_indices, axis=-1, kind='quicksort', order=None)

        # weighting the matrix plays by BM25 corresponding to α in the original paper.
        logging.debug("weighting matrix by bm25_weight")
        self.w_plays = bm25_weight(self.plays, K1=100, B=0.8)

        # if pickled model already exists, load it
        if os.path.exists('data/model.pickle'):
            logging.debug('loading model from model.pickle')
            start = time.time()
            model = open('data/model.pickle', 'rb')
            self.trained_model = pickle.load(model)
            logging.debug('model loaded in: ' + str(time.time()-start))
            
        else:
            # training model
            start = time.time()
            logging.debug("training AlternatingLeastSquares model %s", "for 15 iterations")
            self.trained_model = AlternatingLeastSquares(factors=128, regularization=.02, iterations=15)
            os.environ['OPENBLAS_NUM_THREADS'] = "1"
            self.trained_model.fit(self.plays)
            logging.debug("trained model '%s' in %0.2fs", "ALS", time.time() - start)
            
            start = time.time()
            pickle_on = open("data/model.pickle", "wb")
            pickle.dump(self.trained_model, pickle_on)
            pickle_on.close()
            logging.debug('model object pickled in: ' + str(time.time()-start))

    @staticmethod
    def read_json(filepath):
        start = time.time()
        with open(filepath) as json_file:
            data = json.load(json_file)
        logging.debug(filepath+' loaded in ' + str(time.time() - start))
        return data

    @staticmethod
    def read_lastfm_data(filepath):
        """Returns a tuple of (artistids, userids, plays) where plays is a CSR matrix """
        start = time.time()
        with h5py.File(filepath, 'r') as f:
            m = f.get('artist_user_plays')
            plays = csr_matrix((m.get('data'), m.get('indices'), m.get('indptr')))
            logging.debug('lastfm_360k.hdf5 loaded in ' + str(time.time() - start))
            return np.array(f['artist']), np.array(f['user']), plays

    def get_model(self):
        return self.plays, self.w_plays, self.artists, self.users, self.user_indices, self.tag_set, self.artist_tag_dict,\
               self.tag_frequency_dict, self.trained_model, self.profile_dict
