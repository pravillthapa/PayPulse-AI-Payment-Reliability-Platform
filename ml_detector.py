import pandas as pd
from sklearn.ensemble import IsolationForest


print("=" * 70)
print("PAYPULSE - ML ANOMALY DETECTOR")
print("=" * 70)


# ---------------------------------------------------------
# 1. Load payment data
# ---------------------------------------------------------

df = pd.read_csv("payments.csv")

print(f"\nTransactions loaded: {len(df):,}")


# ---------------------------------------------------------
# 2. Convert timestamp
# ---------------------------------------------------------

df["timestamp"] = pd.to_datetime(df["timestamp"])

df["hour"] = df["timestamp"].dt.hour


# ---------------------------------------------------------
# 3. Create hourly payment metrics
# ---------------------------------------------------------

hourly = (
    df.groupby(
        [
            pd.Grouper(key="timestamp", freq="1h"),
            "bank",
            "payment_method"
        ]
    )
    .agg(
        transactions=("transaction_id", "count"),
        failed_transactions=("status", lambda x: (x == "FAILED").sum()),
        avg_amount=("amount", "mean"),
        avg_retries=("retry_count", "mean")
    )
    .reset_index()
)


# ---------------------------------------------------------
# 4. Calculate failure rate
# ---------------------------------------------------------

hourly["failure_rate"] = (
    hourly["failed_transactions"]
    / hourly["transactions"]
)


# ---------------------------------------------------------
# 5. Features for ML
# ---------------------------------------------------------

features = [
    "transactions",
    "failure_rate",
    "avg_amount",
    "avg_retries"
]

X = hourly[features].fillna(0)


# ---------------------------------------------------------
# 6. Train Isolation Forest
# ---------------------------------------------------------

model = IsolationForest(
    contamination=0.02,
    random_state=42
)

model.fit(X)


# ---------------------------------------------------------
# 7. Detect anomalies
# ---------------------------------------------------------

hourly["anomaly"] = model.predict(X)

hourly["anomaly_score"] = model.decision_function(X)


# Isolation Forest:
#  1  = normal
# -1  = anomaly

anomalies = hourly[
    hourly["anomaly"] == -1
].copy()


# ---------------------------------------------------------
# 8. Sort strongest anomalies first
# ---------------------------------------------------------

anomalies = anomalies.sort_values(
    "anomaly_score"
)


# ---------------------------------------------------------
# 9. Display results
# ---------------------------------------------------------

print(
    f"Hourly observations analyzed: {len(hourly):,}"
)

print(
    f"ML anomalies detected: {len(anomalies):,}"
)

print("\nTop ML anomalies:")
print("-" * 70)


for _, row in anomalies.head(10).iterrows():

    print(
        f"{row['timestamp']} | "
        f"{row['bank']} | "
        f"{row['payment_method']} | "
        f"Transactions: {int(row['transactions'])} | "
        f"Failure: {row['failure_rate'] * 100:.1f}% | "
        f"Retries: {row['avg_retries']:.2f} | "
        f"Score: {row['anomaly_score']:.4f}"
    )


# ---------------------------------------------------------
# 10. Save results
# ---------------------------------------------------------

hourly.to_csv(
    "ml_anomaly_results.csv",
    index=False
)

anomalies.to_csv(
    "ml_anomalies.csv",
    index=False
)


print("\nML results saved:")
print("  ml_anomaly_results.csv")
print("  ml_anomalies.csv")

print("\nML anomaly detection complete.")