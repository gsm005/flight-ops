from flask import Flask, request, jsonify
import requests
import re, time, json
from flight_details_api import get_flight_details
from flight_safe_api import get_flight_safe
from flight_nearest_airport import get_nearest_airports

app = Flask(__name__)


@app.route("/")
def hello():
    return "Check the endpoint!"

@app.route("/flight-details")
def getflightDetails():
    flight = request.args.get("flight", "6E17")
    return get_flight_details(flight)

def getAllFlightInfo(lat, lon):
    all_flight_info = get_flight_safe(lat, lon).get_json()
    is_safe = all_flight_info.get("is_safe", False)
    # is_safe = True
    if is_safe == False:
        nearest_airports = get_nearest_airports(lat, lon).get_json()
        all_flight_info["nearest_airports"] = nearest_airports
    return jsonify(all_flight_info)

@app.route("/flight-safe")
def getFlightSafe():
    lat = request.args.get("lat", "0")
    lon = request.args.get("lon", "0")
    if lat != "0" and lon != "0":
        return getAllFlightInfo(lat, lon)

    flight = request.args.get("flight", "6E17")
    flight_details = get_flight_details(flight).get_json()

    positions = flight_details.get("data", {}).get("positions", [])
    if len(positions) > 0:
        lat = positions[0].get("lat", "0")
        lon = positions[0].get("lon", "0")
        
    all_flight_info = getAllFlightInfo(lat, lon).get_json()
    all_flight_info['flight_details'] = flight_details
    return jsonify(all_flight_info)

if __name__ == "__main__":
    app.run(debug=True)
