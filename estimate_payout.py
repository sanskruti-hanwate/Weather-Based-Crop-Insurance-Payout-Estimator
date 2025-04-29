import pandas as pd
from pathlib import Path

# Load predictions
df = pd.read_csv("data/processed/predicted_triggers.csv")

# User-defined input: Farmer premium paid (₹)
FARMER_PREMIUM = 200  # This can be collected via UI/form in real app
GOVT_SUBSIDY_RATE = 0.90  # 90% paid by govt/insurer

# Estimate Sum Insured based on inverse premium rate (e.g., 2%)
# So ₹200 = 2% → Sum Insured = ₹10,000
PREMIUM_RATE = 0.02
SUM_INSURED = FARMER_PREMIUM / PREMIUM_RATE

# Define static payout slabs for demo (could later be ML-based)
def calculate_payout(trigger):
    if trigger == 'NO':
        return 0
    # flat 50% payout if trigger fired
    return 0.50 * SUM_INSURED

# Apply calculations
df['SUM_INSURED'] = SUM_INSURED

# This column can vary if we collect dynamic farmer input per row
df['FARMER_PREMIUM'] = FARMER_PREMIUM

df['GOVT_PREMIUM'] = SUM_INSURED * GOVT_SUBSIDY_RATE - FARMER_PREMIUM

df['PAYOUT_AMOUNT'] = df['PREDICTED_TRIGGER'].apply(calculate_payout)

# Save final result
df.to_csv("data/processed/final_payouts.csv", index=False)
print("\n💸 Payout estimation completed and saved to data/processed/final_payouts.csv")
