import pandas as pd
from pathlib import Path

# Input and output paths
input_path = Path("data/processed/maharashtra_fortnightly_weather.csv")
output_path = Path("data/processed/payout_triggers_labeled.csv")

# Load weather data
df = pd.read_csv(input_path)

# Define static trigger thresholds
trigger_table = {
    (6, 1): (28, 45, 60, 6),  # month, fortnight: (temp, rain, humidity, wind)
    (6, 2): (29, 50, 65, 6),
    (7, 1): (30, 55, 65, 6),
    (7, 2): (31, 60, 70, 6),
    (8, 1): (32, 65, 70, 6),
    (8, 2): (33, 70, 75, 6),
    (9, 1): (31, 55, 65, 6),
    (9, 2): (30, 50, 60, 6),
    (10, 1): (29, 45, 55, 6),
    (10, 2): (28, 40, 50, 6),
    (11, 1): (26, 35, 50, 6),
    (11, 2): (25, 30, 45, 6),
    (12, 1): (24, 25, 40, 6),
    (12, 2): (23, 20, 35, 6),
    (1, 1): (22, 20, 35, 6),
    (1, 2): (23, 25, 40, 6),
    (2, 1): (25, 30, 45, 6),
    (2, 2): (26, 35, 50, 6),
    (3, 1): (28, 40, 55, 6),
    (3, 2): (29, 45, 60, 6)
}

# Calculate deviations and trigger
def label_row(row):
    key = (row['MONTH'], row['FORTNIGHT'])
    if key not in trigger_table:
        return pd.Series([None, None, None, None, None])

    temp_th, rain_th, hum_th, wind_th = trigger_table[key]
    temp_rise = max(0, row['MEAN_TEMP'] - temp_th)
    rain_deficit = max(0, rain_th - row['RAINFALL'])
    hum_deficit = max(0, hum_th - row['HUMIDITY'])
    wind_excess = max(0, row['WIND_SPEED'] - wind_th)

    triggered = 'YES' if temp_rise > 2 or rain_deficit > 20 or hum_deficit > 15 or wind_excess > 1 else 'NO'
    return pd.Series([temp_rise, rain_deficit, hum_deficit, wind_excess, triggered])

# Apply labeling
df[['TEMP_RISE', 'RAINFALL_DEFICIT', 'HUMIDITY_DEFICIT', 'WIND_EXCESS', 'TRIGGER']] = df.apply(label_row, axis=1)

# Save final labeled dataset
df.to_csv(output_path, index=False)
print(f"✅ Labeled data with TRIGGER column saved to {output_path}")
