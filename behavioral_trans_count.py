import pandas as pd
import numpy as np

# ---------------------------------------------
# STEP 1: Split 'beneidnumber' into acc_id and beneficiary_id
# ---------------------------------------------
df[['acc_id', 'beneficiary_id']] = df['beneidnumber'].str.split('_', expand=True)
df['acc_id'] = df['acc_id'].astype(int)
df['beneficiary_id'] = df['beneficiary_id'].astype(int)

# ---------------------------------------------
# STEP 2: Create 'month' column from transaction date
# ---------------------------------------------
df['valuedatetime'] = pd.to_datetime(df['valuedatetime'])
df['month'] = df['valuedatetime'].dt.to_period('M')

# ---------------------------------------------
# STEP 3: Filter last 6 months of data
# ---------------------------------------------
latest_month = df['month'].max()
last_6_months = pd.period_range(end=latest_month, periods=6, freq='M')
df_6m = df[df['month'].isin(last_6_months)]

# ---------------------------------------------
# STEP 4: Count distinct beneficiaries per account per month
# ---------------------------------------------
monthly_bene = (
    df_6m.groupby(['acc_id', 'month'])['beneficiary_id']
    .nunique()
    .reset_index()
    .pivot(index='acc_id', columns='month', values='beneficiary_id')
    .fillna(0)
)

# Rename columns to consistent format
monthly_bene.columns = [f'bene_count_{str(col)}' for col in monthly_bene.columns]
monthly_bene = monthly_bene.reset_index()

# ---------------------------------------------
# STEP 5: Calculate current month, past avg, diff, z-score
# ---------------------------------------------
# Get month columns (bene_count_YYYY-MM)
month_cols = [col for col in monthly_bene.columns if col.startswith('bene_count_')]
month_cols_sorted = sorted(month_cols)

# Latest month = current month
current_month_col = month_cols_sorted[-1]
past_month_cols = month_cols_sorted[:-1]

# Current month value
monthly_bene["current_month_bene"] = monthly_bene[current_month_col]

# Past 5-month average
monthly_bene["past_5m_avg_bene"] = monthly_bene[past_month_cols].mean(axis=1)

# Difference
monthly_bene["bene_diff"] = monthly_bene["current_month_bene"] - monthly_bene["past_5m_avg_bene"]

# Z-score of difference
mean_diff = monthly_bene["bene_diff"].mean()
std_diff = monthly_bene["bene_diff"].std()
monthly_bene["bene_diff_zscore"] = (monthly_bene["bene_diff"] - mean_diff) / (std_diff + 1e-5)

# Flag for significant spike (Z > 2)
monthly_bene["bene_spike_flag"] = (monthly_bene["bene_diff_zscore"] > 2).astype(int)

# ---------------------------------------------
# Final Output: monthly_bene DataFrame contains
# - Columns per month
# - Current month beneficiary count
# - Past average
# - Difference
# - Z-score
# - Outlier flag
# ---------------------------------------------

import pandas as pd
import numpy as np

# ---------------------------------------------
# STEP 1: Extract acc_id and beneficiary_id
# ---------------------------------------------
df[['acc_id', 'beneficiary_id']] = df['beneidnumber'].str.split('_', expand=True)
df['acc_id'] = df['acc_id'].astype(int)
df['beneficiary_id'] = df['beneficiary_id'].astype(int)
df['valuedatetime'] = pd.to_datetime(df['valuedatetime'])
df['month'] = df['valuedatetime'].dt.to_period('M')

# ---------------------------------------------
# STEP 2: Filter last 6 months of data
# ---------------------------------------------
latest_month = df['month'].max()
last_6_months = pd.period_range(end=latest_month, periods=6, freq='M')
df_6m = df[df['month'].isin(last_6_months)]

# ---------------------------------------------
# STEP 3: Find first interaction date per account-beneficiary
# ---------------------------------------------
first_seen = (
    df.groupby(['acc_id', 'beneficiary_id'])['valuedatetime']
    .min()
    .dt.to_period('M')
    .reset_index()
    .rename(columns={'valuedatetime': 'first_paid_month'})
)

# ---------------------------------------------
# STEP 4: Join with original df to get which month was the "first payment"
# ---------------------------------------------
df_6m = df_6m.merge(first_seen, on=['acc_id', 'beneficiary_id'], how='left')

# Keep only rows where the current transaction month is the first time that beneficiary was paid
df_6m_new = df_6m[df_6m['month'] == df_6m['first_paid_month']]

# ---------------------------------------------
# STEP 5: Count new beneficiaries per account per month
# ---------------------------------------------
monthly_new_bene = (
    df_6m_new.groupby(['acc_id', 'month'])['beneficiary_id']
    .nunique()
    .reset_index()
    .pivot(index='acc_id', columns='month', values='beneficiary_id')
    .fillna(0)
)

# Rename columns
monthly_new_bene.columns = [f'new_bene_count_{str(m)}' for m in monthly_new_bene.columns]
monthly_new_bene = monthly_new_bene.reset_index()

# ---------------------------------------------
# STEP 6: Compute current, past avg, diff, z-score, flag
# ---------------------------------------------
month_cols = [col for col in monthly_new_bene.columns if col.startswith('new_bene_count_')]
month_cols_sorted = sorted(month_cols)

current_month_col = month_cols_sorted[-1]
past_month_cols = month_cols_sorted[:-1]

monthly_new_bene["current_month_new_bene"] = monthly_new_bene[current_month_col]
monthly_new_bene["past_5m_avg_new_bene"] = monthly_new_bene[past_month_cols].mean(axis=1)
monthly_new_bene["new_bene_diff"] = monthly_new_bene["current_month_new_bene"] - monthly_new_bene["past_5m_avg_new_bene"]

# Z-score
mean_diff = monthly_new_bene["new_bene_diff"].mean()
std_diff = monthly_new_bene["new_bene_diff"].std()
monthly_new_bene["new_bene_diff_zscore"] = (monthly_new_bene["new_bene_diff"] - mean_diff) / (std_diff + 1e-5)

# Flag spike
monthly_new_bene["new_bene_spike_flag"] = (monthly_new_bene["new_bene_diff_zscore"] > 2).astype(int)

# ---------------------------------------------
# Final Output: monthly_new_bene contains per-account
# - New bene counts per month
# - 5-month avg
# - Current month
# - Diff, z-score, spike flag
# ---------------------------------------------

import pandas as pd
import numpy as np

# ---------------------------------------------
# STEP 1: Prepare datetime and extract month
# ---------------------------------------------
df['valuedatetime'] = pd.to_datetime(df['valuedatetime'])
df['month'] = df['valuedatetime'].dt.to_period('M')

# ---------------------------------------------
# STEP 2: Filter last 6 months of data
# ---------------------------------------------
latest_month = df['month'].max()
last_6_months = pd.period_range(end=latest_month, periods=6, freq='M')
df_6m = df[df['month'].isin(last_6_months)]

# ---------------------------------------------
# STEP 3: Compute per-account avg & std of transaction amount
# ---------------------------------------------
account_stats = (
    df_6m.groupby('acc_id')['transaction_amount']
    .agg(['mean', 'std'])
    .rename(columns={'mean': 'txn_amt_mean_6m', 'std': 'txn_amt_std_6m'})
    .reset_index()
)

# ---------------------------------------------
# STEP 4: Merge stats back to original df
# ---------------------------------------------
df = df.merge(account_stats, on='acc_id', how='left')

# ---------------------------------------------
# STEP 5: Compute Z-score (with smoothing for std = 0)
# ---------------------------------------------
df['transaction_amount_zscore'] = (
    (df['transaction_amount'] - df['txn_amt_mean_6m']) /
    (df['txn_amt_std_6m'] + 1e-5)
)

# Optional: Flag as anomaly
df['transaction_amount_zscore_flag'] = (df['transaction_amount_zscore'].abs() > 3).astype(int)

# Final feature: transaction_amount_zscore
