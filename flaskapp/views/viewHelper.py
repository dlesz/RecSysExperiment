class ViewHelper:

    def __init__(self, session):
        self.session = session

    def tags_click_tracker(self):
        self.set_new_session_to_false()
        profile = self.session.get('profile')
        clicks = profile['tags_clicks']
        clicks = int(clicks)
        clicks += 1
        self.session['profile']['tags_clicks'] = str(clicks)

    def artists_click_tracker(self):
        self.set_new_session_to_false()
        profile = self.session.get('profile')
        clicks = profile['artists_clicks']
        clicks = int(clicks)
        clicks += 1
        self.session['profile']['artists_clicks'] = str(clicks)

    def boost_up_click_tracker(self):
        self.set_new_session_to_false()
        profile = self.session.get('profile')
        clicks = profile['boost_up_clicks']
        clicks = int(clicks)
        clicks += 1
        self.session['profile']['boost_up_clicks'] = str(clicks)

    def boost_down_click_tracker(self):
        self.set_new_session_to_false()
        profile = self.session.get('profile')
        clicks = profile['boost_down_clicks']
        clicks = int(clicks)
        clicks += 1
        self.session['profile']['boost_down_clicks'] = str(clicks)

    def zero_all_click_tracker(self):
        self.set_new_session_to_false()
        profile = self.session.get('profile')
        clicks = profile['zero_all_clicks']
        clicks = int(clicks)
        clicks += 1
        self.session['profile']['zero_all_clicks'] = str(clicks)

    def clear_data_click_tracker(self):
        self.set_new_session_to_false()
        profile = self.session.get('profile')
        clicks = profile['clear_data_clicks']
        clicks = int(clicks)
        clicks += 1
        self.session['profile']['clear_data_clicks'] = str(clicks)

    def set_new_session_to_false(self):
        self.session['profile']['new_session'] = False

