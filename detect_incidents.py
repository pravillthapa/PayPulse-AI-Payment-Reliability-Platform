import pandas as pd

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv("payments.csv")

df["timestamp"] = pd.to_datetime(
    df["timestamp"]
)

# --------------------------------------------------
# CREATE HOURLY METRICS
# --------------------------------------------------

df["hour"] = df["timestamp"].dt.floor("h")

hourly = (
    df.groupby(
        ["hour", "bank", "payment_method"]
    )
    .agg(
        total_transactions=(
            "transaction_id",
            "count"
        ),

        failed_transactions=(
            "status",
            lambda x: (x == "FAILED").sum()
        ),

        total_revenue=(
            "amount",
            "sum"
        )
    )
    .reset_index()
)

hourly["failure_rate"] = (
    hourly["failed_transactions"]
    / hourly["total_transactions"]
)

# --------------------------------------------------
# SORT CHRONOLOGICALLY
# --------------------------------------------------

hourly = hourly.sort_values(
    ["bank", "payment_method", "hour"]
)

# --------------------------------------------------
# CALCULATE PREVIOUS 24-HOUR BASELINE
# --------------------------------------------------

hourly["baseline_failure_rate"] = (
    hourly
    .groupby(["bank", "payment_method"])
    ["failure_rate"]
    .transform(
        lambda x: x.shift(1).rolling(
            window=24,
            min_periods=6
        ).median()
    )
)

# --------------------------------------------------
# CALCULATE DEVIATION
# --------------------------------------------------

hourly["deviation"] = (
    hourly["failure_rate"]
    - hourly["baseline_failure_rate"]
)

# --------------------------------------------------
# MINIMUM SAMPLE SIZE
# --------------------------------------------------

enough_data = (
    hourly["total_transactions"] >= 20
)

# --------------------------------------------------
# INCIDENT DETECTION
# --------------------------------------------------

hourly["incident"] = (
    enough_data
    & hourly["baseline_failure_rate"].notna()
    & (hourly["deviation"] > 0.20)
)

# --------------------------------------------------
# GET INCIDENTS
# --------------------------------------------------

incidents = hourly[
    hourly["incident"]
].copy()

incidents = incidents.sort_values(
    "deviation",
    ascending=False
)

# --------------------------------------------------
# PRINT RESULTS
# --------------------------------------------------

print("=" * 70)
print("PAYPULSE - PAYMENT INCIDENT DETECTOR")
print("=" * 70)

print(
    f"\nTotal hourly observations: "
    f"{len(hourly):,}"
)

print(
    f"Potential incidents detected: "
    f"{len(incidents):,}"
)

print("\nTop detected incidents:")
print("-" * 70)

for _, row in incidents.head(10).iterrows():

    print(
        f"{row['hour']} | "
        f"{row['bank']} | "
        f"{row['payment_method']} | "
        f"Transactions: {int(row['total_transactions'])} | "
        f"Failure: {row['failure_rate']:.1%} | "
        f"Baseline: {row['baseline_failure_rate']:.1%}"
    )

# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

incidents.to_csv(
    "detected_incidents.csv",
    index=False
)

print(
    "\nIncident report saved as "
    "detected_incidents.csv"
)