import pandas as pd
import numpy as np
from scipy.stats import kurtosis

# Assume df is your DataFrame and you want to check all numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns

# 1. KURTOSIS: Identify high-tailed features
kurtosis_scores = df[numeric_cols].kurtosis()  # Fisher's definition (excess kurtosis)

# Flag features with high kurtosis
high_kurtosis_feats = kurtosis_scores[kurtosis_scores > 3].index.tolist()
print("High-kurtosis (potentially outlier-prone) features:", high_kurtosis_feats)

# 2. IQR OUTLIER DETECTION
outlier_summary = {}

for col in high_kurtosis_feats:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    # Outlier mask
    outlier_mask = (df[col] < lower) | (df[col] > upper)
    df[col + "_is_outlier"] = outlier_mask.astype(int)

    outlier_summary[col] = {
        "kurtosis": kurtosis_scores[col],
        "outlier_count": outlier_mask.sum(),
        "outlier_percent": 100 * outlier_mask.sum() / len(df)
    }

# Convert summary to DataFrame
outlier_df = pd.DataFrame(outlier_summary).T.sort_values("outlier_count", ascending=False)
print(outlier_df)


# Optional Add-on: Visualize Distributions

import seaborn as sns
import matplotlib.pyplot as plt

for col in high_kurtosis_feats:
    sns.histplot(df[col], kde=True)
    plt.title(f"Distribution of {col} (Kurtosis = {kurtosis_scores[col]:.2f})")
    plt.show()