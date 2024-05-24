from flask import Flask, render_template, request, jsonify
import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib, requests, os

module_dir = os.path.abspath(os.path.dirname(__file__))
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
file = os.path.join(module_dir, "RandomForest.joblib")
#model = joblib.load("RandomForest.joblib")
model = joblib.load(file)

def preprocess_data(data):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    return scaled_data


def predict_safety(weather_data):
    scaled_data = preprocess_data(weather_data)
    prediction = model.predict(scaled_data)
    return prediction[0]


def get_flight_safe(lat, lon):
    lat = float(lat)
    lon = float(lon)
    
    nominatim_url = (
        f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&sensor=true&key=AIzaSyAMgo2JZRGoR9NOBbyytTzw4yktex573aw"
    )
    city_response = requests.get(nominatim_url)
    try:
        city_data = city_response.json()
    except ValueError:
        print("ERROR IN FETCHING OPENSTREET MAP")
        city_data = { "plus_code": { "compound_code": "Unknown" } }

    city = city_data.get("plus_code", {}).get("compound_code", "Unknown")
    try:
        city = city.split(" ", 1)[1]
    except IndexError:
        city = "Unknown"

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
            "wind_gusts_10m",
        ],
        "hourly": "temperature_2m",
    }
    responses = openmeteo.weather_api(url, params=params)
    weather_data = responses[0]
    current = weather_data.Current()

    temperature = round(current.Variables(0).Value(), 4)
    precipitation = round(current.Variables(1).Value(), 4)
    weather_code = round(current.Variables(2).Value(), 4)
    wind_speed = round(current.Variables(3).Value(), 4)
    wind_gust = round(current.Variables(4).Value(), 4)

    input_data = np.array(
        [[lat, lon, temperature, wind_speed, wind_gust, precipitation, weather_code]]
    )

    prediction = predict_safety(input_data)

    return jsonify(
        {
            "city": city,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "temperature": temperature,
            "wind_speed": wind_speed,
            "wind_gust": wind_gust,
            "precipitation": precipitation,
            "weather_code": weather_code,
            "is_safe": bool(prediction),
        }
    )
