from flask import Flask, session
import os
from model import model
from controllers import controller, sessionController, inputHelper, fileWriter
from views import viewHelper, view
from datetime import timedelta
import logging
import redis

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# set to True if development mode, otherwise production mode.
dev_mode = False

app = Flask(__name__)

app.config.update(
    TESTING=dev_mode,
    DEBUG=dev_mode,
    USE_RELOADER=dev_mode,
    THREADED=True,
    SECRET_KEY=os.urandom(24),
    JSON_SORT_KEYS=False,
    permanent_session_lifetime=timedelta(minutes=30)
)


@app.after_request
def apply_caching(response):
    """
        Flask security measures added:
        http://flask.pocoo.org/docs/1.0/security/
    """
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # TODO include domain in line below: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy
    # response.headers['Content-Security-Policy'] = "default-src 'self'"
    # response.headers['Content-Security-Policy'] = "script-src 'self' https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"
    # response.headers['Content-Security-Policy'] = "script-src 'self'       https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js"
    # response.headers['Content-Security-Policy'] = "script-src 'self' https://maxcdn.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js"
    # response.headers['Content-Security-Policy'] = "script-src 'self' https://use.fontawesome.com/65cbe4828e.js"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


if dev_mode:
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool, charset="utf-8", decode_responses=True)
else:
    pool = redis.ConnectionPool(host='redis', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool, charset="utf-8", decode_responses=True)

r.set("counter", "0")

print("Redis counter is: " + str(r.get("counter")))


# initialize and train model as first thing. dev=True runs sample data
model = model.Model(dev_mode)

# create global controllers for the app.
view_helper = viewHelper.ViewHelper(session)
session_helper = sessionController.SessionController(session)
input_helper = inputHelper.InputHelper(model, session, session_helper)
f_writer = fileWriter.FileWriter(session)
control = controller.Controller(model, session, session_helper, f_writer)

view.configure_routes(app, view_helper, session_helper, input_helper, f_writer, control, r)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='6543')
