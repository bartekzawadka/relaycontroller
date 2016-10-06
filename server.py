import flask
import json
from gpiolistener import GpioListener

app = flask.Flask(__name__)


@app.route('/get_states')
def get_states():
    return json.dumps(listener.get_states()), 200, {'ContentType': 'application/json'}


@app.route('/get_state')
def get_state():
    return json.dumps(listener.get_state()), 200, {'ContentType': 'application/json'}


@app.route('/set_state')
def set_state():
    state_string = flask.request.args.get('value')
    state = int(state_string)
    listener.set_state(state)
    return json.dumps({'success': True, 'state': state}), 200, {'ContentType': 'application/json'}


@app.route('/set_alive_time')
def set_alive_time():
    alive_time_string = flask.request.args.get('value')
    if alive_time_string is not None:
        alive_time_value = int(alive_time_string)
        listener.set_relay_timeout(alive_time_value)
        return json.dumps({'success': True, 'value':alive_time_value}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False, 'error': 'Cannot parse input value to integer'}), 200, {
            'ContentType': 'application/json'}

if __name__ == '__main__':
    listener = GpioListener()
    listener.start()
    app.run(host='0.0.0.0', port=8080, debug=False)