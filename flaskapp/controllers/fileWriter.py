import time
import logging
import json


class FileWriter:
    def __init__(self, session):
        self.session = session

    """
        Saves session data to json
    """
    def results_to_json(self):
        start = time.time()
        ts = time.time()
        profile = self.session.get('profile')
        # shaping data
        # rec = data.set_index('artist').T.to_dict('int')
        result = {'username': profile['username'],
                  'ts': str(ts),
                  'baseline': str(profile['baseline']),
                  'final_profile': profile['final_profile'],
                  'valid_tags': profile['valid_tags'],
                  'invalid_tags': profile['invalid_tags'],
                  'valid_artists': profile['valid_artists'],
                  'invalid_artists': profile['invalid_artists'],
                  'tags_clicks': profile['tags_clicks'],
                  'artists_clicks': profile['artists_clicks'],
                  'zero_all_clicks': profile['zero_all_clicks'],
                  'boost_up_clicks': profile['boost_up_clicks'],
                  'boost_down_clicks': profile['boost_down_clicks'],
                  'clear_data_clicks': profile['clear_data_clicks'],
                  'plays_row': profile['plays_row'],
                  'plays_data': profile['plays_data'],
                  'recommendations': profile['recommendations']}

        with open('output/' + str(profile['username']) + ',' + str(ts) + '.json', 'w') as filename:
            json.dump(result, filename, indent=4, )
        logging.debug('json file successfully written in: ' + str(time.time() - start))

