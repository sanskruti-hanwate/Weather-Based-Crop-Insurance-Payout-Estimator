import requests
import pandas as pd
import os
from datetime import datetime

# Directory to save CSVs
os.makedirs("data/raw", exist_ok=True)

# District coordinates
districts = {
    "Ahmednagar": (19.0833, 74.8000),
    "Akola": (20.7000, 77.0333),
    "Amravati": (20.9333, 77.8000),
    "Aurangabad": (19.8762, 75.3433),
    "Beed": (18.9900, 75.7600),
    "Bhandara": (21.1700, 79.6500),
    "Buldhana": (20.5333, 76.1833),
    "Chandrapur": (19.9500, 79.3000),
    "Dhule": (20.9031, 74.7750),
    "Gadchiroli": (20.1850, 79.9840),
    "Gondia": (21.4598, 80.1950),
    "Hingoli": (19.7200, 77.1500),
    "Jalgaon": (21.0042, 75.5639),
    "Jalna": (19.8500, 75.9333),
    "Kolhapur": (16.6913, 74.2449),
    "Latur": (18.4080, 76.5768),
    "Mumbai": (18.9667, 72.8967),
    "Nagpur": (21.1498, 79.0806),
    "Nanded": (19.1698, 77.3197),
    "Nandurbar": (21.3890, 74.1830),
    "Nashik": (19.9975, 73.7898),
    "Osmanabad": (18.1861, 76.0419),
    "Palghar": (19.6971, 72.7637),
    "Parbhani": (19.5000, 76.7500),
    "Pune": (18.5167, 73.8563),
    "Raigad": (18.6400, 72.8600),
    "Ratnagiri": (16.9944, 73.3000),
    "Sangli": (16.8676, 74.5704),
    "Satara": (17.6800, 73.9800),
    "Sindhudurg": (16.1278, 73.6700),
    "Solapur": (17.6600, 75.9100),
    "Thane": (19.2183, 72.9781),
    "Wardha": (20.7500, 78.6000),
    "Washim": (20.1667, 77.2500),
    "Yavatmal": (20.3888, 78.1204)
}

# Time range
start = "20190101"
end = "20240331"

# NASA POWER API URL builder
def build_url(lat, lon):
    return (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M"
        f"&community=AG&longitude={lon}&latitude={lat}&start={start}&end={end}&format=JSON"
    )

# Fetch and save func
def fetch_and_save():
    for name, (lat, lon) in districts.items():
        print(f"Fetching weather data for {name}...")
        url = build_url(lat, lon)
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            records = data['properties']['parameter']
            dates = records['T2M_MAX'].keys()

            df = pd.DataFrame({
                "DATE": list(dates),
                "T2M_MAX": list(records['T2M_MAX'].values()),
                "T2M_MIN": list(records['T2M_MIN'].values()),
                "PRECTOTCORR": list(records['PRECTOTCORR'].values()),
                "RH2M": list(records['RH2M'].values()),
                "WS2M": list(records['WS2M'].values()),
                "DISTRICT": name
            })

            df.to_csv(f"data/raw/{name.lower()}_weather.csv", index=False)
            print(f"Saved: {name.lower()}_weather.csv")
        except Exception as e:
            print(f"Failed to fetch for {name}: {e}")

if __name__ == "__main__":
    fetch_and_save()
