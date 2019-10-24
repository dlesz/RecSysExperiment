import tqdm
import h5py
from scipy.sparse import csr_matrix
import numpy as np
import pandas as pd
import logging
import json
from collections import defaultdict
import pandas as pd


def read_json(filepath):
    """
    :param filepath:
    :return: data
    """
    with open(filepath) as json_file:
            data = json.load(json_file)
    return data


def write_json(filepath, data):
    """
    :param filepath:
    :param data:
    """
    with open(filepath, 'w') as outfile:
        json.dump(data, outfile)
            

def get_lastfm(filepath):
    """
    Returns a tuple of (artistids, userids, plays) where plays is a CSR matrix
    method borrowed from https://github.com/benfred/implicit, modified to read the file locally instead of downloading it.
    :return:  artists np array, users np array and plays csr matrix
    """

    with h5py.File(filepath, 'r') as f:
        m = f.get('artist_user_plays')
        #print(type(m.get('indptr')))
        plays = csr_matrix((m.get('data'), m.get('indices'), m.get('indptr')))
        return np.array(f['artist']), np.array(f['user']), plays


def make_artist_tag_dict(artists_array, artist_list, tag_list):
    """
    Making a dict of artist, tags {artist_index : list[tags] }
    :return: artist_tag_dict
    """
    artist_tag_dict = dict()
    with tqdm.tqdm(total=len(artists_array)) as progress:
        for a in artists_array:
            try:
                a_index = int(np.where(artists_array==a)[0])
                a_tag_index = artist_list.index(a)
                artist_tag_dict[str(a_index)] = tag_list[a_tag_index].split("|")
            except:
                pass
            progress.update(1)
    return artist_tag_dict


def count_words(tags_list, threshold):
    """
        Count words (tags) in list and discard all occurences below threshold

    :param tags_list:
    :param threshold:
    :return: frequency count dictionary
    """
    fq = defaultdict(int)
    for w in tags_list:
        fq[w] += 1
    # deleting count below threshold
    for k, v in list(fq.items()):
        if v < threshold:
            del fq[k]
    return fq


def get_p_tags(p_i):
    """
    Takes profile index and returns a unordered list of all its tags
    :param p_i:
    :return:
    """

    p = profile_dict[str(p_i)] # self.profile_dict
    p_tags = []
    for a in p:
        # get tags and append to list
        try:
            p_tags.extend(tag_dict[a]) 
        except:
            pass
    return p_tags


def make_profile_tag_count_dict(threshold):
    """
    Makes a dict dict of profile, threshold defines the minimum occurrences considered
    """

    with tqdm.tqdm(total=len(users)) as progress:
        all_p_tag_counts = {}
        c = 0
        for u in range(0, len(users)):
            p_counts = get_p_tags(u)
            all_p_tag_counts[u] = count_words(p_counts, threshold)
            progress.update(1)
            p_counts = 0
    return all_p_tag_counts


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    output_dir = '../flaskapp/data/'

    # loading data    
    artists, users, plays = get_lastfm('../flaskapp/data/lastfm_360k.hdf5')
    
    # delete eventually
    artists = artists[0:100]
    users = users[0:100]
    
    profile_dict = read_json("../flaskapp/data/profile_dict.json")
    
    # converting strings to ints
    for k in profile_dict.keys():
        profile_dict[k] = list(map(int, profile_dict[k]))

    df_tags = pd.read_csv('../flaskapp/data/lastfm_tags_cleaned.csv')
    
    df_tags['tags'].replace('', np.nan, inplace=True)
    logger.debug('is na: '+ str(df_tags['tags'].isna().sum()))
    df_tags = df_tags.dropna()
    df_tags.isna().sum()

    artist_list1 = df_tags.artist.tolist()
    tag_list1 = df_tags.tags.tolist()

    tag_dict = make_artist_tag_dict(artists, artist_list1, tag_list1)
    
    write_json(output_dir+"artist_tags_dict.json", tag_dict)

    # make tag_set
    tag_list = [item for sublist in tag_dict.values() for item in sublist]
    tag_set = set(tag_list)
    tag_set = pd.DataFrame(list(tag_set))
    tag_set.to_csv(output_dir+"tag_set.csv", index=False)
   
    # approx 10% of artists miss tags
    logger.debug('artists without tags: '+str(len(artists)-len(tag_dict)))
    
    profile_tag_frequency_dict = make_profile_tag_count_dict(5)
    
    write_json(output_dir+"profile_tag_frequency_dict.json", profile_tag_frequency_dict)
