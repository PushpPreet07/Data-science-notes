import pandas as pd
import numpy as np
from scipy.stats import entropy

# Rename columns (edit mapping as needed)
rename_map = {
    'payment_ref_number': 'expertsequence',
    'account': 'accountname',
    'beneficiary': 'beneficiarytext',
}
df.rename(columns=rename_map, inplace=True)

# Make sure datetimes are parsed
df['storeddatetime'] = pd.to_datetime(df['storeddatetime'])

# Sort for rolling/aggregation
df = df.sort_values(['accountname', 'storeddatetime'])

# Grouping for account-level features
group = df.groupby('accountname')

# Example: Aggregate features at accountname level
features = group.agg(
    total_transactions = ('expertsequence', 'count'),
    total_amount = ('amount', 'sum'),
    mean_amount = ('amount', 'mean'),
    std_amount = ('amount', 'std'),
    median_amount = ('amount', 'median'),
    unique_beneficiaries = ('beneficiarytext', 'nunique'),
    countries_used = ('country', 'nunique'),
    currencies_used = ('currency', 'nunique'),
    earliest_tx = ('storeddatetime', 'min'),
    latest_tx = ('storeddatetime', 'max')
).reset_index()

# Calculating account-level behavioral entropy of beneficiarytext
def beneficiary_entropy(series):
    counts = series.value_counts()
    return entropy(counts, base=2)

features['beneficiary_entropy'] = group['beneficiarytext'].apply(beneficiary_entropy).values

# More features: e.g., average transactions per week
features['weeks_active'] = ((features['latest_tx'] - features['earliest_tx']).dt.days / 7).replace(0, 1)
features['avg_txn_per_week'] = features['total_transactions'] / features['weeks_active']

# Example: Ratio of unique beneficiaries per transaction
features['beneficiary_uniqueness_ratio'] = features['unique_beneficiaries'] / features['total_transactions']

# Drop helpers
features.drop(columns=['weeks_active'], inplace=True)

print(features.head())
