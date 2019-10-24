import logging


class InputHelper:

    def __init__(self, model, session, s_controller):
        self.plays, self.w_plays, self.artists, self.users, self.user_indices, self.tag_set, self.artist_tag_dict, \
            self.tag_frequency_dict, self.trained_model, self.profile_dict = model.get_model()
        self.session = session
        self.s_control = s_controller


    """
        Trims user input, remember to wrap param in a str()
    """
    @staticmethod
    def trim_input(user_input):
        #logging.debug("======> trim_input()")
        user_input = str(user_input)
        #logging.debug("raw input: " + str(user_input))
        #logging.debug("raw input type: " + str(type(user_input)))
        if ',' in user_input:
            user_input = user_input.split(',')
            user_input = [s.casefold() for s in user_input]
            return list(map(str.strip, user_input))
        else:
            user_input = user_input.casefold()
            new_list = [user_input]
            return new_list

    """
       Checks if the user input (tags) exist in the
       data set and returns two lists.
       """
    def validate_tag_input(self, user_input):
        #logging.debug("======> validate_tag_input()")
        valid_tags = []
        invalid_tags = []

        if type(user_input) is str:
            if user_input not in self.tag_set:
                invalid_tags.append(user_input)
            else:
                if valid_tags not in self.session['profile']['valid_tags']:
                    valid_tags.append(user_input)
        else:
            for s in user_input:
                if s not in self.tag_set:
                    invalid_tags.append(s)
                    #logging.debug('\"' + s + '\" is not a tag will not be considered. please check for typos')
                else:
                    valid_tags.append(s)
        self.s_control.update_ses_tags_input(valid_tags, invalid_tags)

    """
       Checks if the user input (artists) exist in the
       data set and returns two lists.
    """
    def validate_artist_input(self, user_input):
        #logging.debug("======> validate_artist_input()")
        valid_artists = []
        invalid_artists = []

        if type(user_input) is str:
            if user_input not in self.artists:
                invalid_artists.append(user_input)
            else:
                if valid_artists not in self.session['profile']['valid_artists']:
                    valid_artists.append(user_input)
        else:
            for s in user_input:
                if s not in self.artists:
                    invalid_artists.append(s)
                    #logging.debug(s + " not available, will not be considered. please check for typos")
                else:
                    valid_artists.append(s)
        self.s_control.update_ses_artist_input(valid_artists, invalid_artists)


