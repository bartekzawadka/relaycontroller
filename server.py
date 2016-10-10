import flask
import flask.ext
import json
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
from gpiolistener import GpioListener


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


app = flask.Flask(__name__)


@app.route('/get_states')
@crossdomain(origin='*')
def get_states():
    return json.dumps(listener.get_states()), 200, {'ContentType': 'application/json' }


@app.route('/get_state')
@crossdomain(origin='*')
def get_state():
    return json.dumps(listener.get_state()), 200, {'ContentType': 'application/json'}


@app.route('/set_state')
@crossdomain(origin='*')
def set_state():
    state_string = flask.request.args.get('value')
    state = int(state_string)
    listener.set_state(state)
    return json.dumps({'success': True, 'state': state}), 200, {'ContentType': 'application/json'}


@app.route('/get_alive_time')
@crossdomain(origin='*')
def get_alive_time():
    return json.dumps({'success': True, 'value': listener.get_relay_alive_time()}), 200, {'ContentType': 'application/json'}


@app.route('/set_alive_time')
@crossdomain(origin='*')
def set_alive_time():
    alive_time_string = flask.request.args.get('value')
    print 'Value: %s' % alive_time_string

    if alive_time_string is not None:
        alive_time_value = int(alive_time_string)
        listener.set_relay_timeout(alive_time_value)
        return json.dumps({'success': True, 'value':alive_time_value}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False, 'error': 'Cannot parse input value to integer'}), 200, {
            'ContentType': 'application/json'}

if __name__ == '__main__':
    conf = {}
    execfile('/home/pi/relaycontroller/config/relaycontroller.conf', conf)
    port = conf["port"]

    listener = GpioListener()
    listener.start()
    app.run(host='0.0.0.0', port=port, debug=False)