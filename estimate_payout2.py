import pandas as pd
from pathlib import Path

# Load predictions
df = pd.read_csv("data/processed/predicted_triggers.csv")

# Correct definitions:
# - SUM_INSURED is what the farmer is insured for (e.g., ₹10,000)
# - PREMIUM is calculated as a % of SUM_INSURED (e.g., 2%)
# - FARMER pays a small part (e.g., 10%), GOVT pays the rest

SUM_INSURED = 10000  # User-defined insured amount (per hectare or fixed)
PREMIUM_RATE = 0.02  # 2% of sum insured
SUBSIDY_RATE = 0.90  # Govt pays 90%, farmer pays 10%

# Calculate premiums
TOTAL_PREMIUM = SUM_INSURED * PREMIUM_RATE
FARMER_PREMIUM = TOTAL_PREMIUM * (1 - SUBSIDY_RATE)
GOVT_PREMIUM = TOTAL_PREMIUM * SUBSIDY_RATE

# Define simple payout rule for now (50% of insured amount if triggered)
def calculate_payout(trigger):
    if trigger == 'NO':
        return 0
    return 0.5 * SUM_INSURED

# Apply columns
df['SUM_INSURED'] = SUM_INSURED
df['PREMIUM_RATE'] = PREMIUM_RATE

df['FARMER_PREMIUM'] = round(FARMER_PREMIUM, 2)
df['GOVT_PREMIUM'] = round(GOVT_PREMIUM, 2)
df['TOTAL_PREMIUM'] = round(TOTAL_PREMIUM, 2)

df['PAYOUT_AMOUNT'] = df['PREDICTED_TRIGGER'].apply(calculate_payout)

# Save result
df.to_csv("data/processed/final_payouts.csv", index=False)
print("\n✅ Final payout logic corrected and saved to data/processed/final_payouts.csv")
