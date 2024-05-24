from flask import Flask, render_template, request, jsonify
import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import numpy as np
from math import radians, sin, cos, sqrt, atan2


df = pd.read_csv("airports.csv")

df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")


def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    r = 6371  # Radius of Earth in kilometers
    return c * r


def get_top_nearest_airports(current_lat, current_lon, df, top_n=3):
    df["Distance"] = df.apply(
        lambda row: haversine(
            current_lat, current_lon, row["Latitude"], row["Longitude"]
        ),
        axis=1,
    )
    nearest_airports = df.nsmallest(top_n, "Distance")[
        ["Name", "Distance", "Latitude", "Longitude"]
    ]
    return nearest_airports


def get_nearest_airports(lat, lon):
    current_lat = float(lat)
    current_lon = float(lon)
    nearest_airports = get_top_nearest_airports(current_lat, current_lon, df, top_n=3)
    result = nearest_airports.to_dict(orient="records")
    return jsonify(result)
