import pandas as pd

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv("payments.csv")

df["timestamp"] = pd.to_datetime(
    df["timestamp"]
)

# --------------------------------------------------
# INCIDENT DETAILS
# --------------------------------------------------

incident_bank = "HDFC"
incident_method = "UPI"

incident_start = pd.Timestamp(
    "2026-08-01 18:00:00"
)

incident_end = pd.Timestamp(
    "2026-08-01 20:00:00"
)

# --------------------------------------------------
# INCIDENT TRANSACTIONS
# --------------------------------------------------

incident_df = df[
    (df["bank"] == incident_bank)
    & (df["payment_method"] == incident_method)
    & (df["timestamp"] >= incident_start)
    & (df["timestamp"] < incident_end)
]

# --------------------------------------------------
# NORMAL BASELINE
# --------------------------------------------------

normal_df = df[
    (df["bank"] == incident_bank)
    & (df["payment_method"] == incident_method)
    & (
        (df["timestamp"] < incident_start)
        | (df["timestamp"] >= incident_end)
    )
]

# --------------------------------------------------
# FAILED TRANSACTIONS
# --------------------------------------------------

failed_incident = incident_df[
    incident_df["status"] == "FAILED"
]

# --------------------------------------------------
# CALCULATE BASIC IMPACT
# --------------------------------------------------

failed_count = len(
    failed_incident
)

failed_gmv = failed_incident[
    "amount"
].sum()

average_transaction_value = (
    incident_df["amount"].mean()
)

# --------------------------------------------------
# ESTIMATE EXCESS FAILURES
# --------------------------------------------------

normal_failure_rate = (
    normal_df["status"]
    .eq("FAILED")
    .mean()
)

expected_failures = (
    len(incident_df)
    * normal_failure_rate
)

excess_failures = max(
    failed_count - expected_failures,
    0
)

# --------------------------------------------------
# ESTIMATE RECOVERABLE GMV
# --------------------------------------------------

average_failed_amount = (
    failed_incident["amount"].mean()
)

estimated_recoverable_gmv = (
    excess_failures
    * average_failed_amount
)

# --------------------------------------------------
# INCIDENT SEVERITY
# --------------------------------------------------

if estimated_recoverable_gmv >= 100000:

    severity = "CRITICAL"

elif estimated_recoverable_gmv >= 50000:

    severity = "HIGH"

elif estimated_recoverable_gmv >= 10000:

    severity = "MEDIUM"

else:

    severity = "LOW"

# --------------------------------------------------
# PRINT REPORT
# --------------------------------------------------

print("=" * 70)
print("PAYPULSE - REVENUE IMPACT ANALYSIS")
print("=" * 70)

print(
    f"\nIncident: "
    f"{incident_bank} + {incident_method}"
)

print(
    f"Duration: "
    f"{incident_start} → {incident_end}"
)

print("\nTransaction impact:")
print("-" * 70)

print(
    f"Transactions during incident : "
    f"{len(incident_df):,}"
)

print(
    f"Failed transactions           : "
    f"{failed_count:,}"
)

print(
    f"Normal failure rate           : "
    f"{normal_failure_rate:.1%}"
)

print(
    f"Expected failures             : "
    f"{expected_failures:.1f}"
)

print(
    f"Estimated excess failures     : "
    f"{excess_failures:.1f}"
)

print("\nFinancial impact:")
print("-" * 70)

print(
    f"Failed GMV                    : "
    f"₹{failed_gmv:,.2f}"
)

print(
    f"Average transaction value     : "
    f"₹{average_transaction_value:,.2f}"
)

print(
    f"Estimated recoverable GMV     : "
    f"₹{estimated_recoverable_gmv:,.2f}"
)

print(
    f"\nIncident severity: "
    f"{severity}"
)

print("\nAnalysis complete.")