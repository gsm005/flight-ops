from flask import Flask, request, jsonify
from datetime import datetime, timezone
import requests
import re, time

base_url = "https://www.flightstats.com/v2"

track_url = (
    base_url
    + "/api-next/flick/%%flightId%%?guid=34b64945a69b9cac:5ae30721:13ca699d305:XXXX&airline=%%airline%%&flight=%%flight%%&flightPlan=true&rqid=xd2cssu74sf"
)

def get_details(flight_id, airline, flight):
    url = (
        track_url.replace("%%flightId%%", flight_id)
        .replace("%%airline%%", airline)
        .replace("%%flight%%", flight)
    )
    response = requests.get(url)
    response_json = response.json()
    return response_json


def get_flight_id(airline, flight):
    now_utc = datetime.now(timezone.utc)
    year = now_utc.strftime("%Y")
    month = now_utc.strftime("%m")
    date = now_utc.strftime("%d")
    
    url = base_url + "/flight-tracker/" + airline + "/" + flight + "?year=" + year + "&month=" + month + "&date=" + date
    response = requests.get(url)
    response_text = response.text

    match = re.search(r"flightId=(\d+)", response_text)
    if match:
        return match.group(1)
    else:
        return None


def get_flight_details(flightcode):
    airline = flightcode[:2]
    flight = flightcode[2:]

    flight_id = get_flight_id(airline, flight)
    if flight_id is not None:
        data = get_details(flight_id, airline, flight)
        data['success'] = True
        return jsonify(data)
    else:
        response = {"success": True, "message": "Flight ID not found"}
        return jsonify(response)