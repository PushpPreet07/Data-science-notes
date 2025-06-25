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
