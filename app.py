# ==============================
# 🌤️ Temperature Prediction (Flask + 7-Day Forecast + Fuzzy Matching)
# ==============================

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from fuzzywuzzy import process
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta

app = Flask(__name__)

# ---- Load Dataset ----
DATA_PATH = "india_weather_rainfall_data.xlsx"
df = pd.read_excel(DATA_PATH)

# ---- Clean & Prepare Data ----
df = df.dropna(subset=["avg_temp", "date_of_record"])
df["date_of_record"] = pd.to_datetime(df["date_of_record"])
df["year"] = df["date_of_record"].dt.year
df["month_num"] = df["date_of_record"].dt.month
df["day"] = df["date_of_record"].dt.day

for col in ['station_name', 'district', 'state']:
    df[col] = df[col].astype(str).str.lower().str.strip()

features = ['wind_speed', 'air_pressure', 'rainfall', 'elevation',
            'latitude', 'longitude', 'year', 'month_num', 'day']
target = 'avg_temp'


# ---- Helper: Recommendation based on temperature ----
def get_recommendation(temp):
    if temp > 32:
        return "🔥 It's quite hot! Stay hydrated and avoid going out during noon."
    elif 25 <= temp <= 32:
        return "🌤️ Pleasant weather! Great time for outdoor activities."
    elif 20 <= temp < 25:
        return "☁️ Mildly cool weather — consider light clothing."
    elif 15 <= temp < 20:
        return "❄️ Cool weather — wear something warm."
    else:
        return "🥶 Cold conditions — stay warm and drink something hot!"


# ---- Flask Routes ----
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    location = data.get("location", "").strip().lower()
    date_str = data.get("date", "").strip()

    if not location or not date_str:
        return jsonify({"error": "Please provide both location and date."})

    # ---- Fuzzy Match ----
    all_locations = pd.concat([
        df['station_name'], df['district'], df['state']
    ]).dropna().unique().tolist()

    best_match = process.extractOne(location, all_locations)
    if not best_match:
        return jsonify({"error": "No similar location found."})

    matched_location = best_match[0]
    df_loc = df[
        (df['station_name'] == matched_location) |
        (df['district'] == matched_location) |
        (df['state'] == matched_location)
    ]

    if df_loc.empty:
        return jsonify({"error": f"No data found for {location}."})

    # ---- Train Random Forest ----
    X = df_loc[features]
    y = df_loc[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)

    # ---- Single Day Prediction ----
    future_date = pd.to_datetime(date_str)
    if future_date < datetime.now():
        return jsonify({"error": "Date must be in the future."})

    f_wind = df_loc['wind_speed'].mean()
    f_press = df_loc['air_pressure'].mean()
    f_rain = df_loc['rainfall'].mean()
    f_elev = df_loc['elevation'].mean()
    f_lat = df_loc['latitude'].mean()
    f_lon = df_loc['longitude'].mean()

    day_input = pd.DataFrame([[
        f_wind, f_press, f_rain, f_elev, f_lat, f_lon,
        future_date.year, future_date.month, future_date.day
    ]], columns=features)

    predicted_temp = float(model.predict(day_input)[0])

    # ---- Generate 7-Day Forecast ----
    today = datetime.now()
    forecast = []
    for i in range(7):
        d = today + timedelta(days=i)
        df_input = pd.DataFrame([[
            f_wind, f_press, f_rain, f_elev, f_lat, f_lon,
            d.year, d.month, d.day
        ]], columns=features)
        temp = float(model.predict(df_input)[0])
        forecast.append({
            "date": d.strftime("%Y-%m-%d"),
            "temp": round(temp, 2)
        })

    # ---- Recommendation ----
    recommendation = get_recommendation(predicted_temp)

    return jsonify({
        "location": matched_location.title(),
        "date": future_date.strftime("%Y-%m-%d"),
        "temperature": round(predicted_temp, 2),
        "forecast": forecast,
        "recommendation": recommendation
    })


if __name__ == "__main__":
    app.run(debug=True)
