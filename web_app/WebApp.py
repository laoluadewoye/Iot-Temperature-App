# from flask import Flask, jsonify, Response
# import waitress


# # App object
# app: Flask = Flask(__name__)


# @app.route('/')
# def index() -> tuple[Response, int]:
#     """
#     Get the home page of the web app.

#     :returns: A tuple containing a JSON response and an HTTP status code.
#     """

#     return app.send_static_file('index.html'), 200


# @app.route('/api/v1/web/status', methods=['GET'])
# def get_web_status() -> tuple[Response, int]:
#     """
#     Get the status of the web app.

#     :returns: A tuple containing a JSON response and an HTTP status code.
#     """

#     return jsonify({'status': 'running'}), 200


# if __name__ == '__main__':
#     waitress.serve(app, host='0.0.0.0', port=8080)

# Install required libraries: pip install fastapi uvicorn psycopg2-binary SQLAlchemy apscheduler
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, text
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.templating import Jinja2Templates
import datetime
import uvicorn
import os

# Create FastAPI app
app = FastAPI()

# Define PostgreSQL Database URL (Replace with your actual connection string)
DATABASE_URL = "postgresql://postgres:iot_admin@localhost:5432/PostgreSQL_IoT_Weather_DB"
engine = create_engine(DATABASE_URL)

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")
os.makedirs("templates", exist_ok=True)
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>IoT Sensor Data</title>
    <style>
        body { font-family: Times New Roman, sans-serif; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Real-Time Sensor Data</h1>
    <table>
        <thead>
            <tr>
                {% for col in columns %}<th>{{ col }}</th>{% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in rows %}
            <tr>
                {% for col in columns %}<td>{{ row[col] }}</td>{% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""
with open("templates/data.html", "w") as f:
    f.write(html_template)


# API Endpoint for PowerBI
@app.get("/data")
def get_data():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM sensor_data"))  # Specify actual table name
        return [dict(row._mapping) for row in result]


# Function to update the database at scheduled intervals
def update_data():
    with engine.connect() as conn:
        timestamp = datetime.datetime.now()
        conn.execute(text("UPDATE sensor_data SET last_updated = :timestamp"), {"timestamp": timestamp})
        conn.commit()
        print(f"Database Updated at {timestamp}")


# Initialize Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(update_data, "interval", minutes=5)  # Update every 5 minutes
scheduler.start()


@app.get("/status")
def home():
    return {"message": "APScheduler is running!"}


# Shutdown scheduler when API stops
@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()


# Run the FastAPI app using Uvicorn
if __name__ == "__main__":
    uvicorn.run("WebApp:app", host="0.0.0.0", port=8080, reload=True)
