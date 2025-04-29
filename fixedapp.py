import math
import datetime
import calendar
from flask import Flask, render_template, request, jsonify
import pandas as pd
import requests
import joblib
import json

app = Flask(__name__)

# Load models
trigger_model = joblib.load("models/trigger_classifier_model.pkl")
payout_model = joblib.load("models/payout_percentage_regressor.pkl")
sum_insured_model = joblib.load("models/sum_insured_predictor.pkl")
print("✅ Models loaded successfully.")

# District coordinates (27 districts, used internally for lat/lon lookup)
district_coords = {
    "Ahmadnagar": (19.0948, 74.7476),
    "Akola": (20.6976, 77.0081),
    "Amravati": (20.9374, 77.7796),
    "Aurangabad": (19.8762, 75.3433),
    "Bid": (18.9873, 75.7570),
    "Buldana": (20.5293, 76.1804),
    "Dhule": (20.9042, 74.7749),
    "Hingoli": (19.7170, 77.1482),
    "Jalgaon": (21.0077, 75.5626),
    "Jalna": (19.8410, 75.8864),
    "Kolhapur": (16.7050, 74.2433),
    "Latur": (18.4088, 76.5604),
    "Nanded": (19.1383, 77.3210),
    "Nandurbar": (21.3735, 74.2390),
    "Nashik": (19.9975, 73.7898),
    "Osmanabad": (18.1810, 76.0419),
    "Palghar": (19.6967, 72.7656),
    "Parbhani": (19.2707, 76.7600),
    "Pune": (18.5204, 73.8567),
    "Raigarh": (18.6447, 73.3000),
    "Ratnagiri": (16.9902, 73.3120),
    "Sangli": (16.8524, 74.5815),
    "Satara": (17.6805, 74.0183),
    "Sindhudurg": (16.1222, 73.6810),
    "Solapur": (17.6599, 75.9064),
    "Thane": (19.2183, 72.9781),
    "Washim": (20.1112, 77.1333)
}

# New: Districts by season (the subsets you want in the UI)
districts_by_season = {
    "Kharif": [
        'Ahmadnagar','Amravati','Aurangabad','Bid','Buldana','Dhule',
        'Jalgaon','Jalna','Latur','Nashik','Osmanabad','Parbhani',
        'Pune','Sangli','Satara','Solapur','Washim','Akola','Hingoli'
    ],
    "Rabi": [
        'Ahmadnagar','Aurangabad','Bid','Buldana','Dhule','Jalgaon',
        'Jalna','Kolhapur','Latur','Nanded','Nandurbar','Nashik',
        'Osmanabad','Palghar','Parbhani','Pune','Raigarh','Ratnagiri',
        'Sangli','Sindhudurg','Solapur','Thane','Washim'
    ]
}

# Fortnight-wise trigger ranges per crop...
trigger_table = {
    # Pomegranate
    ('Pomegranate', (6, 1)): {'rain': (50, 100), 'temp': (28, 34), 'humidity': (55, 75), 'wind': (0, 10)},
    ('Pomegranate', (6, 2)): {'rain': (50, 100), 'temp': (28, 34), 'humidity': (55, 75), 'wind': (0, 10)},
    ('Pomegranate', (7, 1)): {'rain': (60, 120), 'temp': (26, 32), 'humidity': (60, 80), 'wind': (0, 10)},
    ('Pomegranate', (7, 2)): {'rain': (60, 120), 'temp': (26, 32), 'humidity': (60, 80), 'wind': (0, 10)},
    ('Pomegranate', (8, 1)): {'rain': (70, 130), 'temp': (26, 31), 'humidity': (65, 85), 'wind': (0, 10)},
    ('Pomegranate', (8, 2)): {'rain': (70, 130), 'temp': (26, 31), 'humidity': (65, 85), 'wind': (0, 10)},
    ('Pomegranate', (9, 1)): {'rain': (50, 100), 'temp': (27, 33), 'humidity': (55, 75), 'wind': (0, 10)},
    ('Pomegranate', (9, 2)): {'rain': (50, 100), 'temp': (27, 33), 'humidity': (55, 75), 'wind': (0, 10)},
    ('Pomegranate', (10, 1)): {'rain': (30, 80), 'temp': (25, 30), 'humidity': (50, 70), 'wind': (0, 10)},
    ('Pomegranate', (10, 2)): {'rain': (30, 80), 'temp': (25, 30), 'humidity': (50, 70), 'wind': (0, 10)},

    # Mango
    ('Mango', (12, 1)): {'rain': (0, 10), 'temp': (18, 28), 'humidity': (55, 70), 'wind': (0, 10)},
    ('Mango', (12, 2)): {'rain': (0, 10), 'temp': (18, 28), 'humidity': (55, 70), 'wind': (0, 10)},
    ('Mango', (1, 1)): {'rain': (0, 10), 'temp': (15, 25), 'humidity': (50, 70), 'wind': (0, 10)},
    ('Mango', (1, 2)): {'rain': (0, 10), 'temp': (15, 25), 'humidity': (50, 70), 'wind': (0, 10)},
    ('Mango', (2, 1)): {'rain': (0, 15), 'temp': (18, 30), 'humidity': (50, 65), 'wind': (0, 10)},
    ('Mango', (2, 2)): {'rain': (0, 15), 'temp': (18, 30), 'humidity': (50, 65), 'wind': (0, 10)},
    ('Mango', (3, 1)): {'rain': (5, 20), 'temp': (22, 32), 'humidity': (55, 70), 'wind': (0, 10)},
    ('Mango', (3, 2)): {'rain': (5, 20), 'temp': (22, 32), 'humidity': (55, 70), 'wind': (0, 10)},
    ('Mango', (4, 1)): {'rain': (20, 40), 'temp': (28, 35), 'humidity': (60, 75), 'wind': (0, 10)},
    ('Mango', (4, 2)): {'rain': (20, 40), 'temp': (28, 35), 'humidity': (60, 75), 'wind': (0, 10)},
}

season_months = {
    "Kharif": [6, 7, 8, 9, 10],
    "Rabi": [12, 1, 2, 3, 4]
}

crop_info = {
    "Pomegranate": {
        "description": "A fruit-bearing deciduous shrub...",
        "image": "/static/img/pomegranate.jpg",
        "optimal_conditions": "Well-drained soil...",
        "growth_cycle": "10-12 months...",
        "avg_yield": "12-16 tonnes per hectare"
    },
    "Mango": {
        "description": "A tropical tree cultivated for its edible fruit...",
        "image": "/static/img/mango.jpg",
        "optimal_conditions": "Deep, well-drained soil...",
        "growth_cycle": "3-6 months...",
        "avg_yield": "10-15 tonnes per hectare"
    }
}

month_names = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
}

weather_cache = {}

def fetch_weather(lat, lon, year, month):
    cache_key = f"{lat}_{lon}_{year}_{month}"
    if cache_key in weather_cache:
        print(f"📊 Using cached data for {year}-{month} | {lat}, {lon}")
        return weather_cache[cache_key]
    
    start_date = f"{year}{month:02d}01"
    end_date = f"{year}{month:02d}{calendar.monthrange(year, month)[1]}"
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters=T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M"
        f"&community=AG&longitude={lon}&latitude={lat}"
        f"&start={start_date}&end={end_date}&format=JSON"
    )
    print(f"📡 Fetching: {year}-{month} | {lat}, {lon}")
    try:
        r = requests.get(url, timeout=15)
        data = r.json()['properties']['parameter']
        tmin = list(data["T2M_MIN"].values())
        tmax = list(data["T2M_MAX"].values())
        rainfall = list(data["PRECTOTCORR"].values())
        humidity = list(data["RH2M"].values())
        wind = list(data["WS2M"].values())

        mean_temp = sum((x + y) / 2 for x, y in zip(tmin, tmax)) / len(tmin)
        total_rain = sum(rainfall)
        avg_humidity = sum(humidity) / len(humidity)
        avg_wind = sum(wind) / len(wind)

        days_in_month = len(tmin)
        mid_point = days_in_month // 2

        # First fortnight
        f1_temp = sum((x + y) / 2 for x, y in zip(tmin[:mid_point], tmax[:mid_point])) / mid_point
        f1_rain = sum(rainfall[:mid_point])
        f1_humidity = sum(humidity[:mid_point]) / mid_point
        f1_wind = sum(wind[:mid_point]) / mid_point

        # Second fortnight
        f2_temp = sum((x + y) / 2 for x, y in zip(tmin[mid_point:], tmax[mid_point:])) / (days_in_month - mid_point)
        f2_rain = sum(rainfall[mid_point:])
        f2_humidity = sum(humidity[mid_point:]) / (days_in_month - mid_point)
        f2_wind = sum(wind[mid_point:]) / (days_in_month - mid_point)

        daily_data = []
        for i in range(days_in_month):
            daily_data.append({
                "date": f"{year}-{month:02d}-{i+1:02d}",
                "temp_min": round(tmin[i], 1),
                "temp_max": round(tmax[i], 1),
                "rainfall": round(rainfall[i], 2),
                "humidity": round(humidity[i], 1),
                "wind": round(wind[i], 1)
            })
        
        result = {
            "monthly": {
                "mean_temp": round(mean_temp, 2),
                "total_rain": round(total_rain, 2),
                "avg_humidity": round(avg_humidity, 2),
                "avg_wind": round(avg_wind, 2)
            },
            "fortnight1": {
                "mean_temp": round(f1_temp, 2),
                "total_rain": round(f1_rain, 2),
                "avg_humidity": round(f1_humidity, 2),
                "avg_wind": round(f1_wind, 2)
            },
            "fortnight2": {
                "mean_temp": round(f2_temp, 2),
                "total_rain": round(f2_rain, 2),
                "avg_humidity": round(f2_humidity, 2),
                "avg_wind": round(f2_wind, 2)
            },
            "daily": daily_data
        }
        
        weather_cache[cache_key] = result
        print(f"📊 Weather Data: mean temp:{round(mean_temp,2)} total_rain:{round(total_rain, 2)}")
        print(f"📊 Weather Data: avg_humidity:{round(avg_humidity, 2)} avg_wind:{round(avg_wind, 2)}")
        return result
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def get_month_fortnight_name(month, fortnight):
    return f"{month_names[month]} {'Early' if fortnight == 1 else 'Late'}"

def calculate_payout(district, season, year, crop, area):
    print("calculate_payout started...")
    lat, lon = district_coords[district]
    triggered_months = []
    payout_percents = []
    weather_data = {}
    trigger_details = []

    for month in season_months[season]:
        actual_year = year + 1 if season == "Rabi" and month in [1, 2, 3, 4] else year
        weather_result = fetch_weather(lat, lon, actual_year, month)
        if weather_result is None:
            continue

        weather_data[month] = weather_result

        for fortnight in [1, 2]:
            key = (crop, (month, fortnight))
            if key not in trigger_table:
                continue

            thresholds = trigger_table[key]
            fortnight_data = weather_result[f"fortnight{fortnight}"]

            def dev(actual, minv, maxv, mode='deficit'):
                if mode == 'deficit' and actual < minv:
                    return round(minv - actual, 2)
                elif mode == 'excess' and actual > maxv:
                    return round(actual - maxv, 2)
                return 0.0

            features = {
                "TEMP_RISE": dev(fortnight_data["mean_temp"], *thresholds['temp'], 'excess'),
                "RAINFALL_DEV": dev(fortnight_data["total_rain"], *thresholds['rain'], 'deficit'),
                "HUMIDITY_DEV": dev(fortnight_data["avg_humidity"], *thresholds['humidity'], 'deficit'),
                "WIND_EXCESS": dev(fortnight_data["avg_wind"], *thresholds['wind'], 'excess')
            }

            triggered = trigger_model.predict(pd.DataFrame([features]))[0]

            trigger_detail = {
                "month": month,
                "fortnight": fortnight,
                "period_name": get_month_fortnight_name(month, fortnight),
                "is_triggered": bool(triggered == 1),
                "actual": {
                    "temp": fortnight_data["mean_temp"],
                    "rain": fortnight_data["total_rain"],
                    "humidity": fortnight_data["avg_humidity"],
                    "wind": fortnight_data["avg_wind"]
                },
                "threshold": {
                    "temp": thresholds['temp'],
                    "rain": thresholds['rain'],
                    "humidity": thresholds['humidity'],
                    "wind": thresholds['wind']
                },
                "deviation": {
                    "temp": features["TEMP_RISE"],
                    "rain": features["RAINFALL_DEV"],
                    "humidity": features["HUMIDITY_DEV"],
                    "wind": features["WIND_EXCESS"]
                }
            }

            trigger_details.append(trigger_detail)
            print(f"triggered: {triggered} | {features}")
            if triggered == 1:
                payout_percent = payout_model.predict(pd.DataFrame([features]))[0]
                triggered_months.append(get_month_fortnight_name(month, fortnight))
            else:
                payout_percent = 0.0

            payout_percents.append(payout_percent)
            trigger_detail["payout_percent"] = round(float(payout_percent) * 100, 2)

    if not payout_percents:
        si_input = pd.DataFrame([{
            "district": district, "crop": crop, "season": season
        }])
        sum_insured = float(sum_insured_model.predict(si_input).flatten()[0])

        return {
            "payout": 0,
            "sum_insured": round(sum_insured, 2),
            "avg_percent": 0,
            "area_used": min(area, 5),
            "triggered": [],
            "trigger_details": trigger_details,
            "weather_data": weather_data
        }

    avg_percent = sum(payout_percents) / len(payout_percents)
    si_input = pd.DataFrame([{
        "district": district, "crop": crop, "season": season
    }])
    sum_insured = float(sum_insured_model.predict(si_input).flatten()[0])

    # Cap area to maximum 5 hectares
    capped_area = min(area, 5)
    estimated_payout = round(avg_percent * sum_insured * capped_area, 2)

    return {
        "payout": estimated_payout,
        "sum_insured": round(sum_insured, 2),
        "avg_percent": round(float(avg_percent) * 100, 2),
        "area_used": capped_area,
        "triggered": triggered_months,
        "trigger_details": trigger_details,
        "weather_data": weather_data
    }

@app.route("/", methods=["GET", "POST"])
def index():
    crops_by_season = {"Kharif": ["Pomegranate"], "Rabi": ["Mango"]}
    current_year = datetime.datetime.now().year
    error_message = None

    # Defaults if GET
    selected_district = None
    selected_season = "Kharif"
    selected_year = current_year
    selected_crop = None
    selected_area = 1.0
    result = None

    if request.method == "POST":
        print("Form data received:", request.form)
        district = request.form.get("district")
        season = request.form.get("season")
        year = request.form.get("year")
        crop = request.form.get("crop")
        area = request.form.get("area")
        
        # Keep them for re-render
        selected_district = district
        selected_season = season
        selected_year = year
        selected_crop = crop
        selected_area = area
        
        # Validate form data
        if not district or not season or not year or not crop or not area:
            error_message = "Please fill in all required fields."
            return render_template(
                "index.html",
                crops_by_season=crops_by_season,
                districts_by_season=districts_by_season,   # new
                crop_info=crop_info,
                current_year=current_year,
                error=error_message,
                district=selected_district,
                season=selected_season,
                year=selected_year,
                crop=selected_crop,
                area=selected_area,
                result=None
            )

        try:
            int_year = int(year)
            float_area = float(area)
        except ValueError:
            error_message = "Invalid year or area value provided."
            return render_template(
                "index.html",
                crops_by_season=crops_by_season,
                districts_by_season=districts_by_season, 
                crop_info=crop_info,
                current_year=current_year,
                error=error_message,
                district=selected_district,
                season=selected_season,
                year=selected_year,
                crop=selected_crop,
                area=selected_area,
                result=None
            )

        # Calculate
        result = calculate_payout(district, season, int_year, crop, float_area)
        result["district"] = district
        result["district_coords"] = district_coords.get(district, (0,0))
        result["crop_info"] = crop_info[crop]
        result["selected_crop"] = crop
        result["selected_season"] = season
        result["selected_year"] = int_year
        result["selected_area"] = float_area

    return render_template(
        "index.html",
        crops_by_season=crops_by_season,
        districts_by_season=districts_by_season,  
        crop_info=crop_info,
        current_year=current_year,
        error=error_message,
        district=selected_district,
        season=selected_season,
        year=selected_year,
        crop=selected_crop,
        area=selected_area,
        result=result
    )

# Optional APIs
@app.route("/api/district_coords", methods=["GET"])
def get_district_coords():
    return jsonify(district_coords)

@app.route("/api/crop_info", methods=["GET"])
def get_crop_info():
    return jsonify(crop_info)

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    try:
        data = request.json
        district = data["district"]
        season = data["season"]
        year = int(data["year"])
        crop = data["crop"]
        area = float(data["area"])
        
        result = calculate_payout(district, season, year, crop, area)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
