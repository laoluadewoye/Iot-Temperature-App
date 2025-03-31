"""Module for interfacing with data generation logic through REST API."""

from flask import Flask, request, jsonify, Response
from typing import Union
import waitress
from DataGen import main_data_gen_loop
from threading import Thread, Event


# App object
app: Flask = Flask(__name__)

# To keep track of the state of the data generation loop
data_gen_thread: Union[Thread, None] = None
data_gen_stop_event: Event = Event()


def start_data_gen_loop() -> None:
    """
    Start the data generation loop in a separate thread.
    """

    global data_gen_thread
    global data_gen_stop_event

    data_gen_stop_event.clear()  # Reset the stop flag
    data_gen_thread = Thread(
        name="data_gen_main_loop", target=main_data_gen_loop, args=(data_gen_stop_event,)
    )
    data_gen_thread.start()


def stop_data_gen_loop() -> None:
    """
    Stop the data generation loop by setting a flag.
    """

    global data_gen_thread
    global data_gen_stop_event

    data_gen_stop_event.set()
    if data_gen_thread is not None:
        data_gen_thread.join()  # Wait for the thread to finish


@app.route('/api/v1/generator/status', methods=['GET'])
def get_generator_status() -> tuple[Response, int]:
    """
    Get the status of the data generator.

    :returns: A tuple containing a JSON response and an HTTP status code.
    """

    if data_gen_thread is None or not data_gen_thread.is_alive():
        return jsonify({'status': 'stopped'}), 200
    else:
        return jsonify({'status': 'running'}), 200


@app.route('/api/v1/generator/toggle', methods=['POST'])
def control_generator() -> tuple[Response, int]:
    """
    Start or stop the data generator based on the received message.

    :returns: A tuple containing a JSON response and an HTTP status code.
    """

    data = request.get_json()

    if 'message' in data:
        message = data['message']

        if message == 'start':
            if data_gen_thread is None or not data_gen_thread.is_alive():
                start_data_gen_loop()
                return jsonify({'status': 'success', 'message': 'Data generation started.'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Data generation is already running.'}), 400
        elif message == 'stop':
            if data_gen_thread and data_gen_thread.is_alive():
                stop_data_gen_loop()
                return jsonify({'status': 'success', 'message': 'Data generation stopped.'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Data generation is not running.'}), 400
        else:
            return jsonify({'status': 'error', 'message': 'Invalid message.'}), 400
    else:
        return jsonify({'status': 'error', 'message': 'No message provided.'}), 400


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8081)
    waitress.serve(app, host='0.0.0.0', port=8081)
