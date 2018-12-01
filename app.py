###################################################################################################
# Step 2 - Climate App
#
#  Now that you have completed your initial analysis, design a Flask API 
#   based on the queries that you have just developed.
#
#     * Use FLASK to create your routes.
#
#  Routes
#
#   * /api/v1.0/precipitation
#      | Convert the query results to a Dictionary using date as the key and prcp as the value.
#      | Return the JSON representation of your dictionary.
#
#   * /api/v1.0/stations
#      | Return a JSON list of stations from the dataset.
#
#   * /api/v1.0/tobs
#      | query for the dates and temperature observations from a year from the last data point.
#      | Return a JSON list of Temperature Observations (tobs) for the previous year.
#
#    * /api/v1.0/<start> and /api/v1.0/<start>/<end>
#      | Return a JSON list of the minimum temperature, the average temperature, and the max 
#           temperature for a given start or start-end range.
#      | When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and 
#           equal to the start date.
#      | When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between 
#           the start and end date inclusive.
###################################################################################################

# import dependencies 
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Hawaii.sqlite")
# reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of rain totals from the prior year for all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of temperatures from the prior year for all stations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for all dates from the start date onward<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end dates (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates from the start date to the end date, inclusively<br/>"
    )
#########################################################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""
    #    * Query for the dates and precipitation observations from the last year.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

    # Create a list of dicts with `date` as the keys and `prcp` as the values
    rain_total = []
    for result in rain:
        row = {}
        row["date"] = rain[0]
        row["prcp"] = rain[1]
        rain_total.append(row)

    # Return the json representation of your dictionary.
    return jsonify(rain_total)

#########################################################################################
@app.route("/api/v1.0/stations")
def stations():
    station_query = session.query(Station.name, Station.station)
    station = pd.read_sql(station_query.statement, station_query.session.bind)

    # Return a JSON list of stations from the dataset.
    return jsonify(station.to_dict())

#########################################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
    #    * Query for the dates and temperature observations from the last year.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

    # Create a list of dicts with `date` and `tobs` as the keys and values
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        temperature_totals.append(row)
    # Return the json representation of your dictionary.
    return jsonify(temperature_totals)

#########################################################################################
@app.route("/api/v1.0/<start>")
def trip1(start):

    # go back one year from start date and go until end of data for Min/Avg/Max temp.   
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)

    # calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))

    # Return a JSON list of the minimum temp, average temp, and max temp for a given start until end of data. 
    return jsonify(trip)

#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):

  # go back one year from start/end date and get Min/Avg/Max temp     
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year

    # calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))

    # Return a JSON list of the minimum temp, average temp, and max temp for a given start-end range. 
    return jsonify(trip)

#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)