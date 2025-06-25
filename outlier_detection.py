import pandas as pd
import numpy as np
from scipy.stats import kurtosis

# Replace with your actual feature list
features_to_check = ['transaction_amount', 'velocity_score', 'txn_count']  

outlier_summary = {}

for col in features_to_check:
    mean = df[col].mean()
    std = df[col].std()
    k = kurtosis(df[col])  # Excess kurtosis
    
    # Apply μ ± 3σ rule
    lower = mean - 3 * std
    upper = mean + 3 * std
    outlier_mask = (df[col] < lower) | (df[col] > upper)
    
    df[col + '_is_outlier'] = outlier_mask.astype(int)

    outlier_summary[col] = {
        "mean": round(mean, 2),
        "std_dev": round(std, 2),
        "kurtosis": round(k, 2),
        "upper_threshold": round(upper, 2),
        "lower_threshold": round(lower, 2),
        "outlier_count": outlier_mask.sum(),
        "outlier_percent": round(100 * outlier_mask.sum() / len(df), 2)
    }

# Convert to DataFrame
summary_df = pd.DataFrame(outlier_summary).T.sort_values("kurtosis", ascending=False)
print(summary_df)

flagged_df = df[df[[col + '_is_outlier' for col in features_to_check]].any(axis=1)]
df['log_transaction_amount'] = np.log1p(df['transaction_amount'])  # safer for 0s
df['log_velocity'] = np.log1p(df['velocity_score'])

df['amount_risk_bin'] = pd.qcut(df['transaction_amount'], q=4, labels=['Low', 'Medium', 'High', 'Very High'])
df['velocity_risk_bin'] = pd.qcut(df['velocity_score'], q=3, labels=['Safe', 'Moderate', 'Aggressive'])
