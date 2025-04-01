-- init-db.sql

-- Create NoSQL tables to store and read information
CREATE TABLE IF NOT EXISTS temperature_data (
    time_recorded TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    value_fahr FLOAT NOT NULL,
    PRIMARY KEY (time_recorded)
);

CREATE TABLE IF NOT EXISTS humidity_data (
    time_recorded TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    value_svp_perc FLOAT NOT NULL,
    PRIMARY KEY (time_recorded)
);

CREATE TABLE IF NOT EXISTS air_pressure_data (
    time_recorded TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    value_hpa FLOAT NOT NULL,
    PRIMARY KEY (time_recorded)
);

CREATE TABLE IF NOT EXISTS wind_speed_data (
    time_recorded TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    value_mph FLOAT NOT NULL,
    PRIMARY KEY (time_recorded)
);

CREATE TABLE IF NOT EXISTS wind_direction_data (
    time_recorded TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    value_deg FLOAT NOT NULL,
    PRIMARY KEY (time_recorded)
)

CREATE TABLE IF NOT EXISTS solar_radiation_data (
    time_recorded TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    value_w_m2 FLOAT NOT NULL,
    PRIMARY KEY (time_recorded)
)

CREATE TABLE IF NOT EXISTS uv_index_data (
    time_recorded TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    value_uvi FLOAT NOT NULL,
    PRIMARY KEY (time_recorded)
)

CREATE TABLE IF NOT EXISTS precipitation_data (
    time_recorded TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    value_nm_s FLOAT NOT NULL,
    PRIMARY KEY (time_recorded)
)

-- Create data generation user and set permissions
CREATE USER ${DATA_GEN_USER} WITH ENCRYPTED PASSWORD ${DATA_GEN_PASSWORD};
GRANT CONNECT ON DATABASE postgres TO ${DATA_GEN_USER};
GRANT USAGE ON SCHEMA public TO ${DATA_GEN_USER};
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ${DATA_GEN_USER};

-- Create web viewer user and set permissions
CREATE USER ${WEB_VIEWER_USER} WITH ENCRYPTED PASSWORD ${WEB_VIEWER_PASSWORD};
GRANT CONNECT ON DATABASE postgres TO ${WEB_VIEWER_USER};
GRANT USAGE ON SCHEMA public TO ${WEB_VIEWER_USER};
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ${WEB_VIEWER_USER};
