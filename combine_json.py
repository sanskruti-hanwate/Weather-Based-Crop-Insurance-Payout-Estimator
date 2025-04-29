import json
import pandas as pd

def flatten_insurance_data(json_path, season):
    with open(json_path, 'r') as f:
        raw_data = json.load(f)
    records = []
    for district, crops in raw_data.items():
        for crop, values in crops.items():
            try:
                sum_insured = float(values.get("sum_insured_per_hectare", 0))
                actuarial_rate = float(values.get("actuarial_rate_percent", 0))
                farmer_share = float(values.get("farmer_share_percent", 0))

                total_premium = round((sum_insured * actuarial_rate) / 100, 2)
                farmer_premium = round((sum_insured * farmer_share) / 100, 2)
                govt_premium = round(total_premium - farmer_premium, 2)

                records.append({
                    "district": district.strip(),
                    "crop": crop.strip(),
                    "season": season,
                    "sum_insured_per_hectare": sum_insured,
                    "actuarial_rate_percent": actuarial_rate,
                    "farmer_share_percent": farmer_share,
                    "total_premium": total_premium,
                    "farmer_premium": farmer_premium,
                    "govt_premium": govt_premium
                })
            except Exception as e:
                print(f"Skipping row due to error: {e}")
    return records

# Load and flatten both JSONs
kharif_data = flatten_insurance_data("district_crop_insurance_data(Kharif).json", "Kharif")
rabi_data = flatten_insurance_data("district_crop_insurance_data(Rabi).json", "Rabi")

# Combine and create DataFrame
combined_df = pd.DataFrame(kharif_data + rabi_data)

# Save to CSV
combined_df.to_csv("data/processed/combined_insurance_data.csv", index=False)
print("✅ Final dataset with premiums saved to data/processed/combined_insurance_data.csv")
