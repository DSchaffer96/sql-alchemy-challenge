# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
from flask import Flask,jsonify


#################################################
# Database Setup
#################################################
engine=create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base=automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app=Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(starting date)<br/>"
        f"/api/v1.0/(starting date)/(ending date)<br/>"
        f"Please enter the date using YYYY-MM-DD format"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return date and precipitation data from the last year from the measurement table"""
    most_recent=dt.date(2017,8,23)
    one_year_ago=most_recent-dt.timedelta(days=365)
    prcp_results=session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date>=one_year_ago).all()

    yearly_prcp=[]
    for date,prcp in prcp_results:
        prcp_dict={}
        prcp_dict["date"]=date
        prcp_dict["prcp"]=prcp
        yearly_prcp.append(prcp_dict)

    return jsonify(yearly_prcp)

@app.route("/api/v1.0/stations")
def stations():
    """Return station info from the station table"""
    station_results=session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation)
    
    station_info=[]
    for station,name,latitude,longitude,elevation in station_results:
        station_dict={}
        station_dict["station id"]=station
        station_dict["name"]=name
        station_dict["latitude"]=latitude
        station_dict["longitude"]=longitude
        station_dict["elevation"]=elevation
        station_info.append(station_dict)

    return jsonify(station_info)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the date and temperature data from the last year from the most active station"""
    most_recent=dt.date(2017,8,23)
    one_year_ago=most_recent-dt.timedelta(days=365)
    station_year_data=session.query(Measurement.tobs,Measurement.station,Measurement.date).\
        filter(Measurement.station=='USC00519281').\
        filter(Measurement.date>=one_year_ago).\
        order_by(Measurement.tobs).all()
    
    yearly_temp=[]
    for tobs,station,date in station_year_data:
        temp_dict={}
        temp_dict["tobs"]=tobs
        temp_dict["station"]=station
        temp_dict["date"]=date
        yearly_temp.append(temp_dict)
    
    return jsonify(yearly_temp)
    
@app.route("/api/v1.0/<starting_date>")
def start_date_only(starting_date):
    """Return the min temperature, the average temperature, and the max temperature from the present, going back to the specified start date"""
    start_date_results=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date>=starting_date).all()
    
    start_date=[]
    for min,avg,max in start_date_results:
        start_dict={}
        start_dict["Minimum Temp"]=min
        start_dict["Average Temp"]=avg
        start_dict["Maximum Temp"]=max
        start_date.append(start_dict)
    
    return jsonify(start_date)

@app.route("/api/v1.0/<starting_date>/<ending_date>")
def start_to_end(starting_date,ending_date):
    """Return the min temp, avg temp, and max temp from specified start date to specified end date"""
    start_to_end_results=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date>=starting_date).filter(Measurement.date<=ending_date).all()
    
    start_to_end=[]
    for min,avg,max in start_to_end_results:
        start_to_end_dict={}
        start_to_end_dict["Minimum Temp"]=min
        start_to_end_dict["Average Temp"]=avg
        start_to_end_dict["Maximum Temp"]=max
        start_to_end.append(start_to_end_dict)
    
    return jsonify(start_to_end)
if __name__ == '__main__':
    app.run(debug=True)

session.close()