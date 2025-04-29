import pandas as pd
from pathlib import Path
import os

# Paths
input_dir = Path("data/raw")
output_path = Path("data/processed/maharashtra_fortnightly_weather.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

#helper-- convert date to month and fortnight
def get_month_fortnight(date_str):
    date_str = str(date_str)  
    day = int(date_str[-2:])
    month = int(date_str[4:6])
    return month, 1 if day <= 15 else 2

# Process all district files
records = []
for file in input_dir.glob("*_weather.csv"):
    df = pd.read_csv(file)
    if df.empty: continue

    district = df['DISTRICT'].iloc[0]
    df['MONTH'], df['FORTNIGHT'] = zip(*df['DATE'].map(get_month_fortnight))
    df['YEAR'] = df['DATE'].astype(str).str[:4].astype(int)

    grouped = df.groupby(['YEAR', 'MONTH', 'FORTNIGHT']).agg({
        'T2M_MAX': 'mean',
        'T2M_MIN': 'mean',
        'PRECTOTCORR': 'sum',
        'RH2M': 'mean',
        'WS2M': 'mean' 
    }).reset_index()

    grouped['DISTRICT'] = district
    grouped['MEAN_TEMP'] = (grouped['T2M_MAX'] + grouped['T2M_MIN']) / 2

    # ✅ Rename BEFORE selecting
    grouped = grouped.rename(columns={
        'PRECTOTCORR': 'RAINFALL',
        'RH2M': 'HUMIDITY',
        'WS2M': 'WIND_SPEED'
    })

    grouped = grouped[['DISTRICT', 'YEAR', 'MONTH', 'FORTNIGHT', 'MEAN_TEMP', 'RAINFALL', 'HUMIDITY', 'WIND_SPEED']]
    records.append(grouped)

# Merge and save
final_df = pd.concat(records, ignore_index=True)
final_df.to_csv(output_path, index=False)
print(f"✅ Saved processed fortnightly data to {output_path}")
