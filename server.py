from flask import Flask, request, jsonify
import requests
import re, time, json
from flight_details_api import get_flight_details
from flight_safe_api import get_flight_safe

app = Flask(__name__)


@app.route("/flight-details")
def getflightDetails(flight=None):
    if flight is None:
        flight = request.args.get("flight", "6E17")
    return get_flight_details(flight)


@app.route("/flight-safe")
def getFlightSafe():
    lat = request.args.get("lat", "0")
    lon = request.args.get("lon", "0")
    if lat != "0" and lon != "0":
        return get_flight_safe(lat, lon)

    flight = request.args.get("flight", "6E17")
    flight_details = get_flight_details(flight).get_json()
    if flight_details.get("success", "false") == "false":
        return flight_details

    positions = flight_details.get("data", {}).get("positions", [])
    if len(positions) > 0:
        lat = positions[0].get("lat", "0")
        lon = positions[0].get("lon", "0")
    return get_flight_safe(lat, lon)


if __name__ == "__main__":
    app.run(debug=True)
