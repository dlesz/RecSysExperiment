import numpy as np
import pandas as pd
import time
import random
import sys
import json
import math
import scipy.sparse as sp
import logging
random.seed(43)


class Controller:

    def __init__(self, model, session, s_controller, f_writer):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        self.plays, self.w_plays, self.artists, self.users, self.user_indices, self.tag_set, self.artist_tag_dict, \
            self.tag_frequency_dict, self.trained_model, self.profile_dict = model.get_model()
        self.session = session
        self.s_control = s_controller
        self.file_writer = f_writer

    """
    Filters the data set for potential music profile matches, based the input (valid tags)
    If artist_filtering=True, the function returns a bigger candidate pool for artist filtering  
    """
    def filter_on_tags(self, artist_filtering=False):
        tag_threshold = 0.5
        n = 5
        if artist_filtering:
            #logging.debug("======> filter on input tags, for artist filtering")
            #logging.debug("user indices size: "+str(len(self.user_indices)))
            time_limit = 5
            pool_size = 360000
        else:
            #logging.debug("======> filter on input tags, base")
            # Limit query time to 2 seconds
            time_limit = 3
            # limiting the number of profiles to at most 500, due to the cookie size limit restriction
            pool_size = 500

        profile = self.session.get('profile')
        valid_tags = profile['valid_tags']
        profiles_subset = []
        start = time.time()
        # random iteration, since query time is limited, the whole data set cannot be search.
        random.shuffle(self.user_indices)
        false_tags_count = 0
        for u in self.user_indices:
            # timer if needed
            if time.time() > start + time_limit or len(profiles_subset) > pool_size:
                logging.debug("timeout reached in: "+str(time.time() - start))
                break
            is_candidate = True
            for tag in valid_tags:
                # sorting the tag count in descending order, before evaluation
                stp = sorted(self.tag_frequency_dict[u].items(), key=lambda kv: kv[1], reverse=True)
                # only considering top n tags
                # TODO, tune this hyper param. top-n tags.
                top_tags = [i[0] for i in stp[0:n]]
                if tag not in top_tags:
                    false_tags_count += 1
                    # TODO validate this
                    #  false_tag_count approach
                    #logging.debug("if false_tags_count "+str(false_tags_count))
                    #logging.debug("is greater than > " + str(math.ceil(len(valid_tags)*0.5)))
                    #logging.debug()
                # if the profile does not have at least half of
                # the valid tags then disregard the profile
                if false_tags_count > math.ceil(len(valid_tags)*tag_threshold):
                    is_candidate = False
                    break
            false_tags_count = 0
            if is_candidate:
                profiles_subset.append(str(u))

        if artist_filtering:
            #logging.debug("artist filtering pool in the making")
            #logging.debug("pool size: " + str(len(profiles_subset)) + " in: "+str(time.time() - start))
            #logging.debug()
            return profiles_subset

        else:
            #logging.debug("profile subset")
            #logging.debug(profiles_subset)
            if profiles_subset:
                # finally update the session cookie
                profile["candidate_pool"] = profiles_subset
                profile["num_candidates"] = len(profiles_subset)
                self.session["profile"] = profile
                #logging.debug("filtered tags object")
                logging.debug(self.session.get('profile'))
                #logging.debug(time.time() - start)
                return True
            else:
                #logging.debug("no candidates found in "+str(time.time() - start))
                #logging.debug()
                return False

    """
    Filters a subset of the data set for potential music profile matches, based the input (valid_artists) 
    """
    def filter_on_artists(self):
        profile = self.session.get('profile')
        valid_tags = profile['valid_tags']
        subset_u_i = self.filter_on_tags(artist_filtering=True)
        #logging.debug("======> filter on input artists")
        valid_artists = profile['valid_artists']
        top_n = 10

        artist_threshold = 0.6 # ensure more than 0.6 of input artists are represented
        time_limit = 7
        start = time.time()
        valid_artist_indices = []
        for a in valid_artists:
            valid_artist_indices.append(self.get_artist_index(a))

        profiles_subset = []
        outliers = []
        p_count = 0
        for u_p in subset_u_i:
            # limiting the number of profiles to at most 500, due to the cookie size limit restriction
            if time.time() > start + time_limit or len(profiles_subset) > 500:
                logging.debug("timeout reached in: "+str(time.time() - start))

                break
            p = self.profile_dict[int(u_p)]
            val = 0
            for v_a in valid_artist_indices:
                if v_a in p[0:top_n]:
                    # TODO validate this approach!
                    val += 1 / len(valid_artist_indices)
            if val >= artist_threshold:
                profiles_subset.append(str(u_p))
            else:
                outliers.append(str(u_p))
            p_count += 1

        # if threshold reached we update the session data
        if profiles_subset:
            profile["candidate_pool"] = profiles_subset
            profile["num_candidates"] = len(profiles_subset)
            profile["valid_artists"] = valid_artists
            self.session['profile'] = profile
            #logging.debug(str(len(profiles_subset))+" candidates found in " + str(time.time() - start))
            #logging.debug(str(p_count) + " profiles scanned")
            return True
        else:
            #logging.debug("no candidates found in " + str(time.time() - start))
            #logging.debug(str(p_count) + " profiles scanned")
            return False

    """Takes artist index and returns list of top n tags"""
    def get_artist_tags(self, a_i):
        n = 3
        try:
            tags = self.artist_tag_dict[a_i][0:n]
        except:
            tags = ['n/a']
        return tags

    """
    Takes user artist indices and return a 
    list containing tags for each artist
    """
    def get_profile_tags(self, u_a_i):
        tags = []
        for i in range(0, len(u_a_i)):
            a_tags = self.get_artist_tags(u_a_i[i])
            a_tags = ', '.join(filter(None, a_tags))
            tags.append(a_tags)
        return tags

    """
       Returns profile from the data set as a dataframe
    """
    def get_profile_html(self):
        #logging.debug("======> get_profile_html")
        u_i = self.session.get('profile')['final_profile']
        u_i = int(u_i)
        u_a_i = list(self.plays.getcol(u_i).tocoo().row)
        tags = self.get_profile_tags(u_a_i)

        u_a = [self.artists[i] for i in self.plays.getcol(u_i).tocoo().row]
        a_p = self.plays.getcol(u_i).tocoo().data
        a_p = a_p.astype(int)
        df = pd.DataFrame({'artist': u_a, 'plays': a_p, 'tags': tags}).sort_values(by=['plays'], ascending=False)
        df_html = df.to_html(index=False, escape=False, classes=["table-bordered", "table-striped", "table-hover"])
        return df_html

    """
    Returns profile from the data set as a dataframe and deletes the redundant
    session data, such as candidate_pool 
    """
    # TODO is this handy?
    def confirm_profile_and_get_html(self):
        #logging.debug("======> confirm_finalprofile_and_get_html")
        #logging.debug(self.session.get('profile')['final_profile'])
        u_i = int(self.session.get('profile')['final_profile'])
        u_a = [self.artists[i] for i in self.plays.getcol(u_i).tocoo().row]
        a_p = self.plays.getcol(u_i).tocoo().data
        a_p = a_p.astype(int)
        df = pd.DataFrame({'artist': u_a, 'plays': a_p}).sort_values(by=['plays'], ascending=False)
        df_html = df.to_html(index=False, escape=False, classes=["table-bordered", "table-striped", "table-hover"])

        # finale updating the session data
        self.s_control.update_ses_matrix_data(a_p, u_a)
        return df_html

    """
        Returns a df with buttons for adjustable recommendation.
    """
    def get_adjustable_profile(self):
        #logging.debug("======> getting adjusted profile")
        u_i = int(self.session.get('profile')['final_profile'])
        u_a = [self.artists[i] for i in self.plays.getcol(u_i).tocoo().row]
        u_a_indices = list(self.plays.getcol(u_i).tocoo().row)

        a_p = self.plays.getcol(u_i).tocoo().data
        a_p = a_p.astype(int)

        pd.set_option('display.max_colwidth', -1)
        pd.set_option('colheader_justify', 'center')

        df = pd.DataFrame(columns=['artist', 'plays', 'tags', 'increase', 'decrease'])
        for i in range(0, len(u_a)):
            tags = self.get_artist_tags(u_a_indices[i])
            df = df.append({'artist': u_a[i],
                            'plays': a_p[i],
                            'tags': ', '.join(filter(None, tags)),
                            'increase': '<button class="btn btn-success btnUp " id="' + str(i) +
                                        '" onclick="adjustBtnTimeOut(this);"><span class="fa '
                                        'fa-plus fa-lg" aria-hidden="true"></span></button>',
                            'decrease': '<button class="btn btn-danger btnDn "  id="' + str(i) +
                                        '" onclick="adjustBtnTimeOut(this);"><i class="fa '
                                        'fa-minus fa-lg" aria-hidden="true"></></button>'
                            }, ignore_index=True)

        # sorted representation disabled for easier indexing and jquery bindings
        #df = df.sort_values(by=['plays'], ascending=False)
        df_html = df.to_html(index=False, escape=False, classes=["table-bordered", "table-striped", "table-hover"])
        return df_html

    """
    Gets recommendations from the trained model, returns dataframe for view and 
    calls data_to_json()
    """
    def baseline_recommend(self):
        #logging.debug("======> baseline recommend")
        profile = self.session.get('profile')
        user_profile = profile['final_profile']
        #logging.debug('getting recommendations for u_i: '+str(user_profile))
        pd.set_option('display.max_colwidth', -1)
        df = pd.DataFrame(columns=['artist', 'tags'])

        user_plays = self.plays.T.tocsr()
        recommendations = dict()

        for artist_id, score in self.trained_model.recommend(int(user_profile), user_plays, N=10, recalculate_user=False):
            tags = self.get_artist_tags(artist_id)
            # save recommendations to def
            df = df.append({'artist': self.artists[artist_id],
                            'tags': ', '.join(filter(None, tags)),
                            'listen': " <a href=\"https://open.spotify.com/search/results/" +
                                    self.artists[artist_id].replace(" ", "-") +
                                    "\" target=\"_blank\"><i class=\"fa fa-spotify fa-lg\""
                                    "aria-hidden=\"true\"></></a>"}, ignore_index=True)
            recommendations[self.artists[artist_id]] = [[np.array2string(score)], [', '.join(filter(None, tags[0:3])),
                                                        " <a href=\"https://open.spotify.com/search/results/" +
                                                        self.artists[artist_id].replace(" ", "-") +
                                                        "\" target=\"_blank\"><i class=\"fa fa-spotify fa-lg\""
                                                        "aria-hidden=\"true\"></></a>"]]

        profile['recommendations'] = recommendations
        self.session['profile'] = profile
        self.file_writer.results_to_json()

        df_html = df.to_html(index=False, escape=False, classes=["table-bordered", "table-striped", "table-hover"])
        return df_html

    """
     Gets recommendations from the trained model, returns dataframe for view and 
     calls data_to_json()
     """
    def adjusted_recommend(self, adjust):
        #logging.debug("======> adjusted recommend")
        profile = self.session.get('profile')
        u_i = int(profile['final_profile'])
        #logging.debug('getting recommendations for u_i: ' + str(u_i))

        if adjust:
            #logging.debug("adjusting recommendations True")
            plays_data = profile['plays_data']
            plays_data = list(map(np.float32, plays_data))
            user_plays = self.adjust_plays_matrix(u_i, plays_data)
            #logging.debug("adjusted column: "+str(plays_data))
            user_plays = user_plays.T.tocsr()
        else:
            user_plays = self.plays.T.tocsr()

        recommendations = dict()
        for artist_id, score in self.trained_model.recommend(u_i, user_plays, N=10, recalculate_user=adjust):
            tags = self.artist_tag_dict[artist_id]
            recommendations[self.artists[artist_id]] = [np.array2string(score), ', '.join(filter(None, tags[0:3])),
                                                        " <a href=\"https://open.spotify.com/search/results/" +
                                                        self.artists[artist_id].replace(" ","-") +
                                                        "\" target=\"_blank\"><i class=\"fa fa-spotify fa-lg\""
                                                        "aria-hidden=\"true\"></></a>"]

        profile['recommendations'] = recommendations
        self.session['profile'] = profile

    """Takes a csr matrix, user index u_i and the plays_data array"""
    def adjust_plays_matrix(self, u_i, plays_data):
        #logging.debug("======> adjusted plays_matrix()")
        plays = sp.csr_matrix(self.plays.copy())
        profile_col = self.plays.getcol(u_i).tocoo()
        plays_row = profile_col.row
        i = 0
        for a in plays_row:
            plays[a, u_i] = plays_data[i]
            i += 1
        return plays

    """
        Adjusts the plays for a given artist a in user column u_i, 
        stores in sessions and returns plays_data 
    """
    def adjust_column(self, a, up):
        #logging.debug("======> adjust column()")

        val = 200
        # plays_col is the user in self.plays
        profile = self.session.get('profile')
        #plays_col = self.plays.getcol(u_i)
        #plays_row = profile['plays_row'] #plays_col.tocoo().row
        plays_data = profile['plays_data'] #plays_col.tocoo().data
        plays_data = list(map(int, plays_data))

        adjust_index = int(a)
        #b_index = int(np.where(plays_row == a)[0])

        if up:
            plays_data[adjust_index] += val
        else:
            if plays_data[adjust_index] > 0 and plays_data[adjust_index] > val:
                plays_data[adjust_index] -= val
            else:
                plays_data[adjust_index] -= 0

        profile = self.session.get('profile')
        profile['plays_data'] = list(map(str, plays_data))
        #profile['plays_row'] = list(map(str, plays_row))
        self.session['profile'] = profile

    """set all plays in column to zero"""
    def zero_column(self):
        #logging.debug("======> adjust column()")

        # plays_col is the user in self.plays
        profile = self.session.get('profile')
        plays_data = profile['plays_data']  # plays_col.tocoo().data
        plays_data = list(map(int, plays_data))
        #set all to zero
        plays_data = [0 for x in plays_data]
        profile['plays_data'] = list(map(str, plays_data))
        # profile['plays_row'] = list(map(str, plays_row))
        self.session['profile'] = profile
        #logging.debug("zero column -->")
        #logging.debug(self.session.get('profile'))

    """Get artist Index Helper"""
    def get_artist_index(self, a):
        #logging.debug("======> get_artist_index()")
        if a in self.artists:
            return int(np.where(self.artists == a)[0])

    """ get list of artist indices """
    def get_list_of_indices(self, a_list):
        #logging.debug("======> get_list_of_indices()")
        f_list = []
        for s in a_list:
            try:
                res = self.get_artist_index(s)
                f_list.append(res)
            except:
                pass
        return f_list
