# source for flask: https://github.com/openfaas/python-flask-template/blob/master/template/python3-flask/index.py

# signal handling imports
import signal
import sys

# flask imports
from flask import Flask, request
import handler
# from waitress import serve
import os

from helpers import logger

serve_port = os.getenv('PORT', 8080)

# add signal handling logic
def handler_stop_signals(signum, frame):
    # handle stop signal
    print('Received SIGTERM or SIGINT, stopping service...')
    sys.exit(0)

signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

app = Flask(__name__)

# distutils.util.strtobool() can throw an exception
def is_true(val):
    return len(val) > 0 and val.lower() == "true" or val == "1"

@app.before_request
def fix_transfer_encoding():
    """
    Sets the "wsgi.input_terminated" environment flag, thus enabling
    Werkzeug to pass chunked requests as streams.  The gunicorn server
    should set this, but it's not yet been implemented.
    """

    transfer_encoding = request.headers.get("Transfer-Encoding", None)
    if transfer_encoding == u"chunked":
        request.environ["wsgi.input_terminated"] = True

@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def main_route(path):
    raw_body = os.getenv("RAW_BODY", "false")

    as_text = True

    if is_true(raw_body):
        as_text = False
    
    ret = handler.handle(request.get_data(as_text=as_text))
    return ret

if __name__ == '__main__':
    print("starting the app...")

    # register signal handlers
    logger.register_signal_handlers()

    # start asyncio thread
    logger.start_thread()

    # using the main flask app.run to allow threaded execution
    # serve(app, host='0.0.0.0', port=serve_port)
    app.run(host='0.0.0.0', port=serve_port, threaded=True)

