"""Module for generating weather data."""

from random import uniform
from datetime import datetime, UTC
from typing import Union
from os import getenv
from psycopg2 import connect
from psycopg2.extensions import connection
from threading import Thread, Event
from time import sleep


def gen_thermostat_data() -> float:
    """
    Simulates the temperature measurements of a thermostat in °F.
    Range: Winter (10-40°F), Summer (60-90°F), Spring/Fall (40-70°F)

    :returns: The temperature in °F.
    """

    month = datetime.now().month
    if month in [12, 1, 2]:
        return uniform(10, 40)  # Winter
    elif month in [6, 7, 8]:
        return uniform(60, 90)  # Summer
    else:
        return uniform(40, 70)  # Spring/Fall


def gen_hygrometer_data() -> float:
    """
    Simulates the humidity measurements of a hygrometer in saturated vapor pressure percentage.
    Range: 30-90%

    :returns: The humidity in saturated vapor pressure percentage.
    """

    return uniform(30, 90)


def gen_barometer_data() -> float:
    """
    Simulates the pressure measurements of a barometer in hPa.
    Typical range: 980-1030 hPa

    :returns: The pressure in hectopascals.
    """

    return uniform(980, 1030)


def gen_anemometer_data() -> float:
    """
    Simulates the wind speed measurements of an anemometer in mph.
    Range: 0-50 mph

    :returns: The wind speed in miles per hour.
    """

    return uniform(0, 50)


def gen_wind_vane_data() -> float:
    """
    Simulates the wind direction measurements of a wind vane in degrees (0-360).

    :returns: The wind direction in degrees of direction.
    """

    return uniform(0, 360)


def gen_pyranometer_data() -> float:
    """
    Simulates the solar radiation measurements of a pyranometer in W/m².
    Range: 0 (night) to 1000 (clear day)

    :returns: The solar radiation in watts per square meter.
    """

    hour = datetime.now().hour
    if 6 <= hour <= 18:
        return uniform(100, 1000)  # Daytime
    else:
        return uniform(0, 100)  # Nighttime


def gen_radiometer_data() -> float:
    """
    Simulates the UV index measurements of a UV radiometer.
    Range: 0-11+ (Low to Extreme risk)

    :returns: The UV index.
    """

    hour = datetime.now().hour
    if 10 <= hour <= 15:
        return uniform(3, 11)  # Peak UV hours
    elif 6 <= hour < 10 or 15 < hour <= 18:
        return uniform(0, 3)  # Morning/Evening
    else:
        return 0  # Nighttime


def gen_rain_gauge_data() -> float:
    """
    Simulates the precipitation height measurements of a rain gauge in nanometers per second.
    Range: 0 (dry) to 58 (heavy rainfall)

    :returns: The precipitation height in nanometers per second.
    """

    return uniform(0, 58)


def generate_weather_snapshot(previous_step: Union[dict, None] = None,
                              likelihoods: Union[dict, None] = None) -> tuple[dict, dict]:
    """
    Generates a snapshot of weather data every second, modifying previous values gradually if provided.

    :param previous_step: The previous step of the weather data.
    :param likelihoods: The likelihoods of the changes in the weather data.
    :return: A tuple containing the new step and the likelihoods of the changes in the weather data.
    """

    # Check if previous_step is provided if likelihoods are provided
    if likelihoods is not None and previous_step is None:
        raise ValueError("previous_step must be provided if likelihoods are provided")

    # Check if likelihoods are not provided
    if likelihoods is None:
        new_likelihoods = {
            "temperature": uniform(-0.00005, 0.00005),
            "humidity": uniform(-0.0005, 0.0005),
            "pressure": uniform(-0.0000002, 0.0000002),
            "wind_speed": uniform(-0.05, 0.05),
            "wind_direction": uniform(-0.01, 0.01),
            "solar_radiation": uniform(-0.0003, 0.0003),
            "uv_index": uniform(-0.0006, 0.0006),
            "precipitation": uniform(-0.04, 0.03)
        }
    else:
        new_likelihoods = likelihoods

    # Generate new step
    if previous_step is not None:
        new_step = {
            "temperature": previous_step["temperature"] + gen_thermostat_data() * new_likelihoods["temperature"],
            "humidity": max(0, min(
                100, previous_step["humidity"] + gen_hygrometer_data() * new_likelihoods["humidity"]
            )),
            "pressure": previous_step["pressure"] + gen_barometer_data() * new_likelihoods["pressure"],
            "wind_speed": max(0, previous_step["wind_speed"] + gen_anemometer_data() * new_likelihoods["wind_speed"]),
            "wind_direction": (previous_step["wind_direction"] +
                               gen_wind_vane_data() * new_likelihoods["wind_direction"]) % 360,
            "solar_radiation": max(
                0, previous_step["solar_radiation"] + gen_pyranometer_data() * new_likelihoods["solar_radiation"]
            ),
            "uv_index": max(0, min(
                11, previous_step["uv_index"] + gen_radiometer_data() * new_likelihoods["uv_index"]
            )),
            "precipitation": max(
                0, previous_step["precipitation"] + gen_rain_gauge_data() * new_likelihoods["precipitation"]
            )
        }

        # Adjust likelihoods
        new_likelihoods['temperature'] += uniform(-0.00005, 0.00005)
        new_likelihoods['humidity'] += uniform(-0.0005, 0.0005)
        new_likelihoods['pressure'] += uniform(-0.0000002, 0.0000002)
        new_likelihoods['wind_speed'] += uniform(-0.05, 0.05)
        new_likelihoods['wind_direction'] += uniform(-0.01, 0.01)
        new_likelihoods['solar_radiation'] += uniform(-0.0003, 0.0003)
        new_likelihoods['uv_index'] += uniform(-0.0006, 0.0006)
        new_likelihoods['precipitation'] += uniform(-0.04, 0.03)
    else:
        new_step = {
            "temperature": gen_thermostat_data(),
            "humidity": gen_hygrometer_data(),
            "pressure": gen_barometer_data(),
            "wind_speed": gen_anemometer_data(),
            "wind_direction": gen_wind_vane_data(),
            "solar_radiation": gen_pyranometer_data(),
            "uv_index": gen_radiometer_data(),
            "precipitation": gen_rain_gauge_data()
        }

    return new_step, new_likelihoods


def insert_data(conn: connection, current_step: dict) -> None:
    """
    Inserts data into each of the tables in the database.
    
    :param conn: The connection object passed into the method.
    :param current_step: The current step of the weather data.
    """
    
    with conn.cursor() as cur_cursor:
        # Create timestamp
        # utc_timestamp = datatime.now(datetime.UTC)
        # utc_timestamp = utc_timestamp.replace(microsecond=(utc_timestamp.microsecond // 1000 * 1000))
        # utc_timestamp = str(ts).replace('000+', '+')
        utc_timestamp = datetime.now(UTC)
        
        # Insert data
        cur_cursor.execute(
            "INSERT INTO temperature_data (time_recorded, value_fahr) VALUES (%s, %s);",
            (utc_timestamp, current_step["temperature"])
        )
        cur_cursor.execute(
            "INSERT INTO humidity_data (time_recorded, value_svp_perc) VALUES (%s, %s);",
            (utc_timestamp, current_step["humidity"])
        )
        cur_cursor.execute(
            "INSERT INTO air_pressure_data (time_recorded, value_hpa) VALUES (%s, %s);",
            (utc_timestamp, current_step["pressure"])
        )
        cur_cursor.execute(
            "INSERT INTO wind_speed_data (time_recorded, value_mph) VALUES (%s, %s);",
            (utc_timestamp, current_step["wind_speed"])
        )
        cur_cursor.execute(
            "INSERT INTO wind_direction_data (time_recorded, value_deg) VALUES (%s, %s);",
            (utc_timestamp, current_step["wind_direction"])
        )
        cur_cursor.execute(
            "INSERT INTO solar_radiation_data (time_recorded, value_w_m2) VALUES (%s, %s);",
            (utc_timestamp, current_step["solar_radiation"])
        )
        cur_cursor.execute(
            "INSERT INTO uv_index_data (time_recorded, value_uvi) VALUES (%s, %s);",
            (utc_timestamp, current_step["uv_index"])
        )
        cur_cursor.execute(
            "INSERT INTO precipitation_data (time_recorded, value_nm_s) VALUES (%s, %s);",
            (utc_timestamp, current_step["precipitation"])
        )
        cur_cursor.execute('COMMIT;')
        print('Added information recorded at', str(utc_timestamp))


def data_generator(conn: connection, stop_event: Event) -> None:
    """
    Method that specifically handles the data generation loop.

    :param conn: The connection object passed into the generator.
    :param stop_event: The event object passed into the generator.
    """

    # Generate first initial step and add it to database
    step, likelihoods = generate_weather_snapshot()
    if not stop_event.is_set():
        insert_data(conn, step)
    sleep(1)

    # Get into the loop
    while not stop_event.is_set():
        step, likelihoods = generate_weather_snapshot(step, likelihoods)
        if not stop_event.is_set():
            insert_data(conn, step)
        sleep(1)


def main_data_gen_loop(stop_event: Event):
    """
    Method that starts and manages the data generation loop.

    :param stop_event: The event object passed into the main thread.
    """

    # Get environmental variables
    try:
        env_db_host = getenv("DB_HOST")
        env_db_name = getenv("DB_NAME")
        env_db_user = getenv("DB_USER")
        env_db_password = getenv("DB_PASSWORD")
        env_db_port = getenv("DB_PORT")
    except KeyError:
        raise ValueError("The right environmental variables are not set.")

    # Connect to the database
    db_conn = connect(
        host=env_db_host, database=env_db_name, user=env_db_user, password=env_db_password, port=env_db_port
    )

    # Start the data generation thread
    data_generator_thread = Thread(target=data_generator, args=(db_conn, stop_event,))
    data_generator_thread.start()

    # Wait for the data generation thread to finish and close the connection
    while not stop_event.is_set():
        sleep(1)
    data_generator_thread.join()
    db_conn.close()
