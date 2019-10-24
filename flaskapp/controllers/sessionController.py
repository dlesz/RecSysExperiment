import logging


class SessionController:
    def __init__(self, session):
        self.session = session

    """
        Creating user object
    """
    def create_user(self):
        logging.debug("======> creating new user in session")
        usr_name = self.session['username']
        baseline = self.session['baseline']
        profile = {"username": usr_name,
                   "baseline": baseline,
                   "new_session": True,
                   "valid_tags": '',
                   "invalid_tags": '',
                   "tag_threshold": False,
                   "artist_threshold": False,
                   "valid_artists": '',
                   "invalid_artists": '',
                   "candidate_pool": '',
                   "num_candidates": '',
                   "final_profile": '',
                   "plays_row": '',
                   "plays_data": '',
                   "recommendations": '',
                   "tags_clicks": '0',
                   "artists_clicks": '0',
                   "boost_up_clicks": '0',
                   "boost_down_clicks": '0',
                   "clear_data_clicks": '0',
                   "zero_all_clicks": '0'}
        self.session["profile"] = profile

    """ clearing all user data except clicks"""
    def clear_user_data(self):
        logging.debug("======> clearing user data in session")
        profile = self.session.get('profile')
        profile['valid_tags'] = ''
        profile['invalid_tags'] = ''
        profile['tag_threshold'] = False
        profile['artist_threshold'] = False
        profile['artist_threshold'] = False
        profile['valid_artists'] = ''
        profile['invalid_artists'] = ''
        profile['candidate_pool'] = ''
        profile['num_candidates'] = ''
        profile['final_profile'] = ''
        profile['plays_row'] = ''
        profile['plays_data'] = ''
        profile['recommendations'] = ''
        self.session["profile"] = profile


    """
       Updates the session profile
       with profile plays matrix, plays_data and plays_row 
    """
    def update_ses_matrix_data(self, plays_data, plays_row):
        logging.debug("======> update_session_matrix_data")
        profile = self.session.get('profile')
        plays_data = list(map(str, plays_data))
        plays_row = list(map(str, plays_row))
        profile['candidate_pool'] = ''
        profile['plays_data'] = plays_data
        profile['plays_row'] = plays_row
        self.session['profile'] = profile

    """
        Pops candidate from pool and deletes that user. 
        Never returns the same candidate twice  
    """
    def pop_candidate_and_set_final(self):
        logging.debug("======> poping candidate")
        profile = self.session.get('profile')
        candidates = profile['candidate_pool']

        while candidates:
            elem = candidates[0]
            # direct deletion, no search needed
            del candidates[0]
            profile["candidate_pool"] = candidates
            profile["final_profile"] = elem
            profile["num_candidates"] = len(candidates)
            self.session['profile'] = profile
            break
    """
        Updates artist user-input
    """
    def update_ses_artist_input(self, valid_input, invalid_input):
        logging.debug("======> updating artist in session")
        profile = self.session.get('profile')
        logging.debug(type(profile['valid_artists']))

        if profile['valid_artists']:
            for s in valid_input:
                if s not in profile['valid_artists']:
                    profile['valid_artists'].extend(valid_input)
        else:
            profile['valid_artists'] = valid_input

        if profile['invalid_artists']:
            profile['invalid_artists'].extend(invalid_input)
        else:
            logging.debug("invalid_artists is empty")
            profile['invalid_artists'] = invalid_input

        if len(profile['valid_artists']) >= 2:
            profile['artist_threshold'] = True

        self.session['profile'] = profile
        logging.debug(self.session.get('profile'))

    """
        Updates tags user-input
    """
    def update_ses_tags_input(self, valid_input, invalid_input):
        logging.debug("======> updating tags in session")
        profile = self.session.get('profile')

        if profile['valid_tags']:
            for s in valid_input:
                if s not in profile['valid_tags']:
                    profile['valid_tags'].extend(valid_input)
        else:
            logging.debug("valid_tags is empty")
            profile['valid_tags'] = valid_input

        if profile['invalid_tags']:
            profile['invalid_tags'].extend(invalid_input)
        else:
            profile['invalid_tags'] = invalid_input

        if len(profile['valid_tags']) >= 2:
            profile['tag_threshold'] = True
        self.session['profile'] = profile
        logging.debug(self.session.get('profile'))
