import pandas as pd
import joblib
from pathlib import Path

# Load the trained model
model = joblib.load("models/trigger_classifier.pkl")

# Load new/unlabeled weather data
# It must contain the 4 required feature columns
data_path = Path("data/processed/maharashtra_fortnightly_weather.csv")
df = pd.read_csv(data_path)

# Calculate deviation features (TEMP_RISE, RAINFALL_DEFICIT, etc.)

# Define thresholds to compute deviations (same as labeling script)
trigger_table = {
    (6, 1): (28, 45, 60, 6), (6, 2): (29, 50, 65, 6), (7, 1): (30, 55, 65, 6),
    (7, 2): (31, 60, 70, 6), (8, 1): (32, 65, 70, 6), (8, 2): (33, 70, 75, 6),
    (9, 1): (31, 55, 65, 6), (9, 2): (30, 50, 60, 6), (10, 1): (29, 45, 55, 6),
    (10, 2): (28, 40, 50, 6), (11, 1): (26, 35, 50, 6), (11, 2): (25, 30, 45, 6),
    (12, 1): (24, 25, 40, 6), (12, 2): (23, 20, 35, 6), (1, 1): (22, 20, 35, 6),
    (1, 2): (23, 25, 40, 6), (2, 1): (25, 30, 45, 6), (2, 2): (26, 35, 50, 6),
    (3, 1): (28, 40, 55, 6), (3, 2): (29, 45, 60, 6)
}

# Compute deviations for prediction
def compute_deviation(row):
    key = (row['MONTH'], row['FORTNIGHT'])
    if key not in trigger_table:
        return pd.Series([0, 0, 0, 0])

    temp_th, rain_th, hum_th, wind_th = trigger_table[key]
    temp_rise = max(0, row['MEAN_TEMP'] - temp_th)
    rain_deficit = max(0, rain_th - row['RAINFALL'])
    hum_deficit = max(0, hum_th - row['HUMIDITY'])
    wind_excess = max(0, row['WIND_SPEED'] - wind_th)
    return pd.Series([temp_rise, rain_deficit, hum_deficit, wind_excess])

# Apply deviation logic
df[['TEMP_RISE', 'RAINFALL_DEFICIT', 'HUMIDITY_DEFICIT', 'WIND_EXCESS']] = df.apply(compute_deviation, axis=1)

# Predict using the model
X = df[['TEMP_RISE', 'RAINFALL_DEFICIT', 'HUMIDITY_DEFICIT', 'WIND_EXCESS']]
df['PREDICTED_TRIGGER'] = pd.Series(model.predict(X)).map({0: 'NO', 1: 'YES'})

# Save predictions
df.to_csv("data/processed/predicted_triggers.csv", index=False)
print("✅ Predictions saved to data/processed/predicted_triggers.csv")
