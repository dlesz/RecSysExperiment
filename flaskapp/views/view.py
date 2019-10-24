import werkzeug
from flask import Flask, request, render_template, flash, session, redirect, url_for, jsonify
from werkzeug.exceptions import BadRequest
import uuid
import logging
from views import alertMessages


def configure_routes(app, view_helper, session_helper, input_helper, f_writer, control, r):

    @app.route('/')
    def login():
        if not session.get('logged_in'):
            u_name = str(uuid.uuid4())
            session['username'] = u_name
            session['logged_in'] = True
            r.incr("counter")

        if not session.get('profile'):
            if int(r.get("counter")) % 2 == 0:
                # creating a user
                session['baseline'] = True
                session_helper.create_user()
            else:
                session['baseline'] = False
                session_helper.create_user()
        return redirect(url_for('index'))

    @app.route('/visits-counter')
    def visits():
        return str((r.get("counter"))) + " visitors"

    @app.route('/index', methods=['POST', 'GET'])
    def index():
        login()
        #logging.debug(session.get('profile'))

        if not session.get('profile')['final_profile']:
            next_profile_html = ''
        else:
            next_profile_html = control.get_profile_html()

        """
            Tag Filtering Button
        """
        if request.method == 'POST':

            if request.form['submit_button'] == 'TagContinue':
                # store the input text in a variable
                raw_input = request.form.get('tags_text')
                #logging.debug("raw tag input: "+str(raw_input))
                #logging.debug(type(raw_input))

                if raw_input:
                    view_helper.tags_click_tracker()
                    trimmed_tag_in = input_helper.trim_input(raw_input)
                    input_helper.validate_tag_input(trimmed_tag_in)
                    # clear input data

                    # if tag_threshold is true, it means that at
                    # least two valid tags has been provided
                    # logging.debug('tag_threshold:')
                    # logging.debug(session.get('profile')['tag_threshold'])
                    if session.get('profile')['tag_threshold']:

                        if control.filter_on_tags():
                            session_helper.pop_candidate_and_set_final()
                            next_profile_html = control.get_profile_html()
                            flash(alertMessages.success_filter_msg, 'success_filter_msg')
                        else:
                            flash(alertMessages.no_match_tags_msg, 'no_matching_profiles_msg')
                    else:
                        flash(alertMessages.min_tags_msg, 'tags_threshold_error')
                else:
                    flash(alertMessages.empty_input_msg, 'tags_threshold_error')

            """
               Tags Filtering Next Button
            """
            if request.form['submit_button'] == 'TagNextProfile':
                # only if the candidate pool has been populated, continue
                if len(session.get('profile')['candidate_pool']):
                    view_helper.tags_click_tracker()

                    if session.get('profile')['candidate_pool']:
                        # logging.debug("PASSED! nextProfile check")
                        flash(alertMessages.success_skip_msg, 'skip_success_msg')
                        session_helper.pop_candidate_and_set_final()
                        next_profile_html = control.get_profile_html()

                    else:
                        flash(alertMessages.pool_empty_msg, 'pool_empty_msg')
                        next_profile_html = control.get_profile_html()

            """
                Clear input Buttons
            """
            if request.form['submit_button'] == 'TagAndArtistClear':
                view_helper.clear_data_click_tracker()
                session_helper.clear_user_data()
                next_profile_html = ''

            """
                Artist Filtering Button
            """
            if request.form['submit_button'] == 'ArtistContinue':
                # store the input text in a variable
                raw_input = request.form.get('artist_text')
                # logging.debug("raw artist input: " + str(raw_input))

                if raw_input:
                    view_helper.artists_click_tracker()
                    trimmed_artist_in = input_helper.trim_input(raw_input)
                    input_helper.validate_artist_input(trimmed_artist_in)

                    # logging.debug('artist_threshold: ')
                    # logging.debug(session.get('profile')['artist_threshold'])
                    if session.get('profile')['artist_threshold']:
                        if control.filter_on_artists():
                            session_helper.pop_candidate_and_set_final()
                            next_profile_html = control.get_profile_html()
                            flash(alertMessages.success_filter_msg, 'success_filter_msg')
                            logging.debug(session.get('profile'))
                        else:
                            flash(alertMessages.no_matching_profiles_msg, 'no_matching_profiles_msg')
                    else:
                        if session.get('profile')['invalid_artists']:
                            # logging.debug(session.get('profile')['invalid_artists'])
                            flash(alertMessages.invalid_artist_msg, 'artist_threshold_error')
                        else:
                            flash(alertMessages.min_artists_msg, 'error')
                else:
                    flash(alertMessages.empty_input_msg, 'artist_threshold_error')

            """
                Artist Filtering Next Button
            """
            if request.form['submit_button'] == 'ArtistNextProfile':
                # only if the candidate pool has been populated, continue
                if len(session.get('profile')['candidate_pool']):
                    view_helper.artists_click_tracker()
                    flash(alertMessages.success_skip_msg, 'skip_success_msg')
                    # logging.debug("PASSED! nextProfile check")
                    session_helper.pop_candidate_and_set_final()
                    next_profile_html = control.get_profile_html()
                else:
                    flash(alertMessages.pool_empty_msg, 'pool_empty_msg')

            """ Get Recommendations Button """
            if request.form['submit_button'] == 'GetRecommendations':
                # if final profile is not empty
                if session.get('profile')['final_profile']:
                    # logging.debug("redirecting_url_for_results")
                    return redirect(url_for('redirect_for_results'))

            """" old Instructions message """
            # if request.form['submit_button'] == 'InstructionsAlert':
            #    flash(alertMessages.welcome_message, 'welcome')

        return render_template('index.html',
                               name="Profile",
                               validTagsHeader="Valid tags:",
                               validTags=', '.join(filter(None, session.get('profile')["valid_tags"])),
                               invalidTagsHeader="Invalid tags:",
                               invalidTags=', '.join(filter(None, session.get('profile')["invalid_tags"])),
                               validArtistsHeader="Valid artists:",
                               validArtists=', '.join(filter(None, session.get('profile')["valid_artists"])),
                               invalidArtistsHeader=u'Invalid artists:',
                               invalidArtists=', '.join(filter(None, session.get('profile')["invalid_artists"])),
                               data=next_profile_html,
                               profile="Music Profile")

    """Checks if session has been created, if not redirects"""

    def check_session():
        if not session.get('logged_in'):
            redirect(url_for('login'))
        return render_template('index.html')

    @app.route('/recommendations', methods=['GET', 'POST'])
    def redirect_for_results():
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        if request.method == 'POST':
            if request.form['submit'] == 'Done':
                f_writer.results_to_json()

        profile_html = control.confirm_profile_and_get_html()

        user_data = session.get('profile')
        # logging.debug("experiment mode, baseline: "+str(user_data['baseline']))
        # logging.debug("Recommending for user object: "+str(user_data))

        if user_data['baseline'] is True:
            results_html = control.baseline_recommend()
            flash(get_id(), 'get_id')
            return render_template('result.html',
                                   profile=profile_html,
                                   name="Recommendations",
                                   data=results_html)

        else:
            html_profile = control.get_adjustable_profile()
            control.adjusted_recommend(False)

            flash(get_id(), 'get_id')
            return render_template('adjust_results.html', profile=html_profile)

    @app.route('/api/recommendations', methods=['GET'])
    def api_recommendations():
        return jsonify(session.get('profile'))

    @app.route('/buttonup', methods=['POST'])
    def button_up():
        # logging.debug("button up")

        if not session.get('logged_in'):
            return redirect(url_for('login'))

        btn_id = request.data.decode('utf-8')
        if btn_id:
            # logging.debug(str(type(text)) + " " + str(text))
            btn_id = int(btn_id.strip("\""))
            # logging.debug(str(type(text)) + " " + str(text))
            control.adjust_column(btn_id, True)
            # start = time.time()
            control.adjusted_recommend(True)
            view_helper.boost_up_click_tracker()

        # logging.debug("btn up in took: " + str(time.time()-start))
        return jsonify(session.get('profile'))

    @app.route('/buttondown', methods=['POST'])
    def button_down():
        # logging.debug("button down")
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        btn_id = request.data.decode('utf-8')
        if btn_id:
            # logging.debug(str(type(text)) + " " + str(text))
            btn_id = int(btn_id.strip("\""))
            # logging.debug(str(type(text)) + " " + str(text))
            control.adjust_column(btn_id, False)
            control.adjusted_recommend(True)
            view_helper.boost_down_click_tracker()
        return jsonify(session.get('profile'))

    @app.route('/allzero', methods=['POST'])
    def button_all_zero():
        # logging.debug("======> all_zero btn()")
        if not session.get('logged_in'):
            return redirect(url_for('login'))

        control.zero_column()
        view_helper.zero_all_click_tracker()

        return jsonify(session.get('profile'))

    @app.route('/restart', methods=['GET', 'POST'])
    def button_restart():
        # logging.debug("======> restart btn()")
        if session.get('profile'):
            session.pop('profile')
            return redirect(url_for('logout'))

    @app.route('/done', methods=['POST'])
    def button_done():
        logging.debug("======> done btn()")
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        f_writer.results_to_json()
        view_helper.zero_all_click_tracker()

        return jsonify(session.get('profile'))

    @app.route("/get_id", methods=["GET", "PUT"])
    def get_id():
        """ API call to get current user id, used by the google form evaluation view."""
        # if no session raise bad request
        if not session.get('username'):
            raise BadRequest()
        else:
            return session['username']
            # return jsonify(session['username'])

    @app.route("/terms", methods=["GET"])
    def terms_page():
        return render_template('terms.html')

    @app.errorhandler(404)
    def page_not_found(error):
        return redirect(url_for('index'))
