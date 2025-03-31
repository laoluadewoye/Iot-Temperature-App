from flask import Flask, jsonify, Response
import waitress


# App object
app: Flask = Flask(__name__)


@app.route('/')
def index() -> tuple[Response, int]:
    """
    Get the home page of the web app.

    :returns: A tuple containing a JSON response and an HTTP status code.
    """

    return app.send_static_file('index.html'), 200


@app.route('/api/v1/web/status', methods=['GET'])
def get_web_status() -> tuple[Response, int]:
    """
    Get the status of the web app.

    :returns: A tuple containing a JSON response and an HTTP status code.
    """

    return jsonify({'status': 'running'}), 200


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8080)
    waitress.serve(app, host='0.0.0.0', port=8080)
