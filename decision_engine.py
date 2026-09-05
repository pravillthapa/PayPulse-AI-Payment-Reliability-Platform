import pandas as pd

# --------------------------------------------------
# LOAD INCIDENT DATA
# --------------------------------------------------

incidents = pd.read_csv(
    "detected_incidents.csv"
)

# --------------------------------------------------
# LOAD PAYMENT DATA
# --------------------------------------------------

df = pd.read_csv(
    "payments.csv"
)

df["timestamp"] = pd.to_datetime(
    df["timestamp"]
)

# --------------------------------------------------
# SELECT MOST SEVERE INCIDENT
# --------------------------------------------------

incident = incidents.iloc[0]

incident_bank = incident["bank"]
incident_method = incident["payment_method"]

incident_time = pd.to_datetime(
    incident["hour"]
)

# --------------------------------------------------
# FIND INCIDENT TRANSACTIONS
# --------------------------------------------------

incident_start = incident_time

incident_end = (
    incident_time
    + pd.Timedelta(hours=1)
)

incident_df = df[
    (df["bank"] == incident_bank)
    & (df["payment_method"] == incident_method)
    & (df["timestamp"] >= incident_start)
    & (df["timestamp"] < incident_end)
]

# --------------------------------------------------
# CALCULATE FAILURE RATE
# --------------------------------------------------

failure_rate = (
    incident_df["status"]
    .eq("FAILED")
    .mean()
)

# --------------------------------------------------
# ESTIMATE BASELINE
# --------------------------------------------------

normal_df = df[
    (df["bank"] == incident_bank)
    & (df["payment_method"] == incident_method)
    & (
        (df["timestamp"] < incident_start)
        | (df["timestamp"] >= incident_end)
    )
]

baseline_failure_rate = (
    normal_df["status"]
    .eq("FAILED")
    .mean()
)

failure_increase = (
    failure_rate
    - baseline_failure_rate
)

# --------------------------------------------------
# FINANCIAL IMPACT
# --------------------------------------------------

failed_df = incident_df[
    incident_df["status"] == "FAILED"
]

failed_count = len(
    failed_df
)

failed_gmv = failed_df[
    "amount"
].sum()

expected_failures = (
    len(incident_df)
    * baseline_failure_rate
)

excess_failures = max(
    failed_count - expected_failures,
    0
)

if failed_count > 0:

    average_failed_amount = (
        failed_df["amount"].mean()
    )

else:

    average_failed_amount = 0

estimated_recoverable_gmv = (
    excess_failures
    * average_failed_amount
)

# --------------------------------------------------
# CONFIDENCE
# --------------------------------------------------

confidence = 0

if failure_increase >= 0.20:
    confidence += 40

elif failure_increase >= 0.10:
    confidence += 25

if failed_count >= 50:
    confidence += 20

if estimated_recoverable_gmv >= 50000:
    confidence += 20

if incident_method == "UPI":
    confidence += 10

confidence = min(
    confidence,
    100
)

# --------------------------------------------------
# SEVERITY
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
# DECISION ENGINE
# --------------------------------------------------

if (
    severity == "CRITICAL"
    and confidence >= 70
):

    action = (
        "TRAFFIC REDISTRIBUTION"
    )

    priority = "P0 - CRITICAL"

    reason = (
        "Critical financial impact with "
        "high-confidence payment degradation."
    )

elif (
    severity == "HIGH"
    and confidence >= 70
):

    action = (
        "TRAFFIC REDISTRIBUTION"
    )

    priority = "P1 - HIGH"

    reason = (
        "High-confidence degradation with "
        "significant recoverable transaction value."
    )

elif confidence >= 50:

    action = (
        "INCREASE MONITORING"
    )

    priority = "P2 - MEDIUM"

    reason = (
        "Anomaly detected, but confidence "
        "is insufficient for aggressive intervention."
    )

else:

    action = (
        "NO AUTOMATED ACTION"
    )

    priority = "P3 - LOW"

    reason = (
        "Evidence is insufficient to justify "
        "automated intervention."
    )

# --------------------------------------------------
# PRINT REPORT
# --------------------------------------------------

print("=" * 70)
print("PAYPULSE - INCIDENT DECISION ENGINE")
print("=" * 70)

print(
    f"\nIncident: "
    f"{incident_bank} + {incident_method}"
)

print(
    f"Detected at: "
    f"{incident_time}"
)

print("\nRisk Assessment:")
print("-" * 70)

print(
    f"Failure rate          : "
    f"{failure_rate:.1%}"
)

print(
    f"Baseline failure rate : "
    f"{baseline_failure_rate:.1%}"
)

print(
    f"Failure rate increase : "
    f"{failure_increase:+.1%}"
)

print(
    f"Failed transactions   : "
    f"{failed_count}"
)

print(
    f"Failed GMV            : "
    f"₹{failed_gmv:,.2f}"
)

print(
    f"Recoverable GMV       : "
    f"₹{estimated_recoverable_gmv:,.2f}"
)

print(
    f"Severity              : "
    f"{severity}"
)

print(
    f"Confidence            : "
    f"{confidence}%"
)

print("\n" + "=" * 70)
print("RECOMMENDED ACTION")
print("=" * 70)

print(
    f"\nAction: "
    f"{action}"
)

print(
    f"Priority: "
    f"{priority}"
)

print(
    f"\nReason:"
)

print(reason)

print(
    "\nRecommendation:"
)

if action == "TRAFFIC REDISTRIBUTION":

    print(
        f"Temporarily reduce {incident_bank} "
        f"{incident_method} traffic and route "
        "eligible transactions through healthy "
        "alternative payment routes."
    )

elif action == "INCREASE MONITORING":

    print(
        "Continue monitoring the affected route "
        "and collect additional evidence before "
        "taking automated action."
    )

else:

    print(
        "Do not automatically intervene. "
        "Continue observing the payment route."
    )

print(
    "\nDecision complete."
)