import pandas as pd

# ==================================================
# PAYPULSE - UNIFIED INCIDENT ANALYZER
# ==================================================

print("=" * 70)
print("PAYPULSE - UNIFIED INCIDENT ANALYZER")
print("=" * 70)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

payments = pd.read_csv("payments.csv")
incidents = pd.read_csv("incidents.csv")

payments["timestamp"] = pd.to_datetime(
    payments["timestamp"]
)

incidents["start_time"] = pd.to_datetime(
    incidents["start_time"]
)

incidents["end_time"] = pd.to_datetime(
    incidents["end_time"]
)

# --------------------------------------------------
# SELECT INCIDENT
# --------------------------------------------------

incident = incidents.iloc[0]

incident_id = incident["incident_id"]
bank = incident["bank"]
method = incident["payment_method"]

start_time = incident["start_time"]
end_time = incident["end_time"]

# --------------------------------------------------
# INCIDENT TRANSACTIONS
# --------------------------------------------------

incident_df = payments[
    (payments["bank"] == bank)
    & (payments["payment_method"] == method)
    & (payments["timestamp"] >= start_time)
    & (payments["timestamp"] < end_time)
].copy()

# --------------------------------------------------
# BASELINE TRANSACTIONS
# --------------------------------------------------

baseline_df = payments[
    (payments["bank"] == bank)
    & (payments["payment_method"] == method)
    & (
        (payments["timestamp"] < start_time)
        | (payments["timestamp"] >= end_time)
    )
].copy()

# --------------------------------------------------
# FAILURE RATES
# --------------------------------------------------

incident_failures = (
    incident_df["status"] == "FAILED"
).sum()

incident_transactions = len(incident_df)

incident_failure_rate = (
    incident_failures / incident_transactions
    if incident_transactions > 0
    else 0
)

baseline_failures = (
    baseline_df["status"] == "FAILED"
).sum()

baseline_transactions = len(baseline_df)

baseline_failure_rate = (
    baseline_failures / baseline_transactions
    if baseline_transactions > 0
    else 0
)

failure_rate_increase = (
    incident_failure_rate
    - baseline_failure_rate
)

# --------------------------------------------------
# FAILURE REASON ANALYSIS
# --------------------------------------------------

incident_failed_df = incident_df[
    incident_df["status"] == "FAILED"
]

baseline_failed_df = baseline_df[
    baseline_df["status"] == "FAILED"
]

incident_reason_pct = (
    incident_failed_df["failure_reason"]
    .value_counts(normalize=True)
)

baseline_reason_pct = (
    baseline_failed_df["failure_reason"]
    .value_counts(normalize=True)
)

all_reasons = sorted(
    set(incident_reason_pct.index)
    | set(baseline_reason_pct.index)
)

reason_changes = {}

for reason in all_reasons:

    normal_pct = baseline_reason_pct.get(
        reason,
        0
    )

    incident_pct = incident_reason_pct.get(
        reason,
        0
    )

    reason_changes[reason] = (
        incident_pct - normal_pct
    )

# Find strongest positive change
if reason_changes:

    dominant_reason = max(
        reason_changes,
        key=reason_changes.get
    )

    dominant_change = reason_changes[
        dominant_reason
    ]

else:

    dominant_reason = "UNKNOWN"
    dominant_change = 0

# --------------------------------------------------
# ROOT CAUSE ASSESSMENT
# --------------------------------------------------

if (
    dominant_reason == "NETWORK_ERROR"
    and dominant_change >= 0.05
):

    root_cause = (
        "PAYMENT NETWORK / BANK-SIDE "
        "CONNECTIVITY DEGRADATION"
    )

elif (
    dominant_reason == "TIMEOUT"
    and dominant_change >= 0.05
):

    root_cause = (
        "PAYMENT PROCESSING TIMEOUT "
        "OR DOWNSTREAM LATENCY"
    )

elif (
    dominant_reason == "BANK_ERROR"
    and dominant_change >= 0.05
):

    root_cause = (
        "BANK-SIDE PAYMENT PROCESSING "
        "FAILURE"
    )

else:

    root_cause = (
        "UNDETERMINED - FURTHER "
        "INVESTIGATION REQUIRED"
    )

# --------------------------------------------------
# CONFIDENCE
# --------------------------------------------------

confidence = 0

# Large failure-rate increase
if failure_rate_increase >= 0.30:
    confidence += 40

elif failure_rate_increase >= 0.20:
    confidence += 30

elif failure_rate_increase >= 0.10:
    confidence += 20

# Strong failure-reason signal
if dominant_change >= 0.10:
    confidence += 30

elif dominant_change >= 0.05:
    confidence += 20

# Enough transaction volume
if incident_transactions >= 200:
    confidence += 20

elif incident_transactions >= 100:
    confidence += 10

confidence = min(
    confidence,
    100
)

# --------------------------------------------------
# FINANCIAL IMPACT
# --------------------------------------------------

failed_gmv = incident_failed_df[
    "amount"
].sum()

average_failed_amount = (
    incident_failed_df["amount"].mean()
    if len(incident_failed_df) > 0
    else 0
)

expected_failures = (
    incident_transactions
    * baseline_failure_rate
)

excess_failures = max(
    incident_failures - expected_failures,
    0
)

recoverable_gmv = (
    excess_failures
    * average_failed_amount
)

# --------------------------------------------------
# SEVERITY
# --------------------------------------------------

if recoverable_gmv >= 100000:
    severity = "CRITICAL"

elif recoverable_gmv >= 50000:
    severity = "HIGH"

elif recoverable_gmv >= 10000:
    severity = "MEDIUM"

else:
    severity = "LOW"

# --------------------------------------------------
# DECISION
# --------------------------------------------------

if (
    severity == "CRITICAL"
    and confidence >= 70
):

    action = "TRAFFIC REDISTRIBUTION"
    priority = "P0 - CRITICAL"

elif (
    severity == "HIGH"
    and confidence >= 70
):

    action = "TRAFFIC REDISTRIBUTION"
    priority = "P1 - HIGH"

elif (
    failure_rate_increase >= 0.20
    and confidence >= 50
):

    action = "ESCALATE + INCREASE MONITORING"
    priority = "P1 - HIGH"

elif confidence >= 40:

    action = "INCREASE MONITORING"
    priority = "P2 - MEDIUM"

else:

    action = "NO AUTOMATED ACTION"
    priority = "P3 - LOW"

# --------------------------------------------------
# PRINT INCIDENT REPORT
# --------------------------------------------------

print(f"\nIncident ID : {incident_id}")
print(f"Route       : {bank} + {method}")
print(
    f"Duration    : {start_time} → {end_time}"
)

print("\n" + "-" * 70)
print("PAYMENT HEALTH")
print("-" * 70)

print(
    f"Transactions        : "
    f"{incident_transactions}"
)

print(
    f"Failed transactions : "
    f"{incident_failures}"
)

print(
    f"Incident failure    : "
    f"{incident_failure_rate:.1%}"
)

print(
    f"Baseline failure    : "
    f"{baseline_failure_rate:.1%}"
)

print(
    f"Failure increase    : "
    f"{failure_rate_increase:+.1%}"
)

print("\n" + "-" * 70)
print("ROOT CAUSE ANALYSIS")
print("-" * 70)

print(
    f"Dominant reason     : "
    f"{dominant_reason}"
)

print(
    f"Reason contribution : "
    f"{dominant_change:+.1%}"
)

print(
    f"Likely root cause   : "
    f"{root_cause}"
)

print(
    f"Confidence          : "
    f"{confidence}%"
)

print("\n" + "-" * 70)
print("FINANCIAL IMPACT")
print("-" * 70)

print(
    f"Failed GMV          : "
    f"₹{failed_gmv:,.2f}"
)

print(
    f"Expected failures   : "
    f"{expected_failures:.1f}"
)

print(
    f"Excess failures     : "
    f"{excess_failures:.1f}"
)

print(
    f"Recoverable GMV     : "
    f"₹{recoverable_gmv:,.2f}"
)

print(
    f"Severity            : "
    f"{severity}"
)

print("\n" + "=" * 70)
print("RECOMMENDED ACTION")
print("=" * 70)

print(
    f"\nAction   : {action}"
)

print(
    f"Priority : {priority}"
)

if action == "TRAFFIC REDISTRIBUTION":

    print(
        "\nRecommendation:"
    )

    print(
        "Reduce traffic through the affected "
        "payment route and route eligible "
        "transactions through healthier "
        "alternatives."
    )

elif action == "ESCALATE + INCREASE MONITORING":

    print(
        "\nRecommendation:"
    )

    print(
        "Escalate the incident to payment "
        "operations and closely monitor the "
        "affected route."
    )

else:

    print(
        "\nRecommendation:"
    )

    print(
        "Continue monitoring the affected "
        "payment route."
    )

# --------------------------------------------------
# SAVE STRUCTURED REPORT
# --------------------------------------------------

report = pd.DataFrame([{
    "incident_id": incident_id,
    "bank": bank,
    "payment_method": method,
    "start_time": start_time,
    "end_time": end_time,
    "transactions": incident_transactions,
    "failed_transactions": incident_failures,
    "incident_failure_rate": incident_failure_rate,
    "baseline_failure_rate": baseline_failure_rate,
    "failure_rate_increase": failure_rate_increase,
    "dominant_failure_reason": dominant_reason,
    "likely_root_cause": root_cause,
    "confidence": confidence,
    "failed_gmv": failed_gmv,
    "recoverable_gmv": recoverable_gmv,
    "severity": severity,
    "recommended_action": action,
    "priority": priority
}])

report.to_csv(
    "incident_report.csv",
    index=False
)

print(
    "\nComplete incident report saved as "
    "incident_report.csv"
)