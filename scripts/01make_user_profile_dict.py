import logging
import time
import numpy as np
import json
import tqdm
import h5py
import operator
from scipy.sparse import csr_matrix

def read_data_set(filepath):
    """
    Returns a tuple of (artistids, userids, plays) where plays is a CSR matrix
    :param filepath:
    :return:
    """
    st = time.time()
    with h5py.File(filepath, 'r') as f:
        m = f.get('artist_user_plays')
        plays = csr_matrix((m.get('data'), m.get('indices'), m.get('indptr')))
        logger.debug('data loaded in:\t' + str(time.time() - st))
        return np.array(f['artist']), np.array(f['user']), plays

def make_sorted_profile_dict():
    """
    Script for creating dict of profiles, used for fast query if artist is in top-n (sorted on plays)
    :return:
    """
    user_indices = np.unique(plays.indices)
    user_indices = np.sort(user_indices, axis=-1, kind='quicksort', order=None)
    profiles = {}
    with tqdm.tqdm(total=len(user_indices)) as progress:
        for u_i in user_indices:
            """ results in: dict of { u_i : list[a_i] } sorted plays view """
            p = tuple(zip([a for a in plays.getcol(u_i).tocoo().row], plays.getcol(u_i).tocoo().data))
            p = sorted(p, key=operator.itemgetter(1), reverse=True)
            list1, list2 = zip(*p)

            """ results in: dict of { u_i : tupe[(artist_name, plays), ..., n] } sorted plays view """
            profiles[str(u_i)] = list(map(int, list1))
            
            progress.update(1)
        return profiles


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    start = time.time()

    artists, users, plays = read_data_set('../flaskapp/data/lastfm_360k.hdf5')

    artists = artists[0:10]
    users = users[0:10]
    plays = plays[0:10]

    logger.debug('data processed in:\t' + str(time.time()-start))

    final_dict = make_sorted_profile_dict()
  
    with open('../flaskapp/data/profile_dict.json', 'w') as outfile:
        json.dump(final_dict, outfile)


