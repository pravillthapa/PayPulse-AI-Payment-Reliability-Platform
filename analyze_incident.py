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
# INCIDENT DATA
# --------------------------------------------------

incident_df = df[
    (df["bank"] == incident_bank)
    & (df["payment_method"] == incident_method)
    & (df["timestamp"] >= incident_start)
    & (df["timestamp"] < incident_end)
]

# --------------------------------------------------
# NORMAL DATA
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
# FAILURE RATES
# --------------------------------------------------

incident_failure_rate = (
    incident_df["status"]
    .eq("FAILED")
    .mean()
)

normal_failure_rate = (
    normal_df["status"]
    .eq("FAILED")
    .mean()
)

failure_rate_increase = (
    incident_failure_rate
    - normal_failure_rate
)

# --------------------------------------------------
# FAILURE REASON DISTRIBUTION
# --------------------------------------------------

incident_failures = incident_df[
    incident_df["status"] == "FAILED"
]

normal_failures = normal_df[
    normal_df["status"] == "FAILED"
]

incident_reasons = (
    incident_failures["failure_reason"]
    .value_counts(normalize=True)
)

normal_reasons = (
    normal_failures["failure_reason"]
    .value_counts(normalize=True)
)

# --------------------------------------------------
# COMPARE FAILURE REASONS
# --------------------------------------------------

reason_comparison = []

all_reasons = set(
    incident_reasons.index
).union(
    normal_reasons.index
)

for reason in all_reasons:

    incident_pct = incident_reasons.get(
        reason,
        0
    )

    normal_pct = normal_reasons.get(
        reason,
        0
    )

    change = (
        incident_pct
        - normal_pct
    )

    reason_comparison.append({
        "reason": reason,
        "normal": normal_pct,
        "incident": incident_pct,
        "change": change
    })

reason_df = pd.DataFrame(
    reason_comparison
)

reason_df = reason_df.sort_values(
    "change",
    ascending=False
)

# --------------------------------------------------
# PRINT ANALYSIS
# --------------------------------------------------

print("=" * 70)
print("PAYPULSE - ROOT CAUSE ANALYSIS")
print("=" * 70)

print(
    f"\nIncident: "
    f"{incident_bank} + {incident_method}"
)

print(
    f"Time: "
    f"{incident_start} → {incident_end}"
)

print(
    f"\nIncident failure rate: "
    f"{incident_failure_rate:.1%}"
)

print(
    f"Normal failure rate:   "
    f"{normal_failure_rate:.1%}"
)

print(
    f"Failure rate increase: "
    f"{failure_rate_increase:+.1%}"
)

# --------------------------------------------------
# FAILURE REASON REPORT
# --------------------------------------------------

print("\nFailure reason comparison:")
print("-" * 70)

for _, row in reason_df.iterrows():

    print(
        f"{row['reason']:<25}"
        f"Normal: {row['normal']:>6.1%}   "
        f"Incident: {row['incident']:>6.1%}   "
        f"Change: {row['change']:>+6.1%}"
    )

# --------------------------------------------------
# ROOT CAUSE REASONING
# --------------------------------------------------

print("\n" + "=" * 70)
print("ROOT CAUSE ASSESSMENT")
print("=" * 70)

top_reason = reason_df.iloc[0]

top_reason_name = top_reason["reason"]
top_reason_change = top_reason["change"]

# --------------------------------------------------
# CONFIDENCE CALCULATION
# --------------------------------------------------

confidence = 0

# Strong failure-rate degradation
if failure_rate_increase > 0.20:
    confidence += 40

# Strong reason-level evidence
if top_reason_change > 0.05:
    confidence += 30

# Incident is isolated to a specific bank/method
if incident_bank == "HDFC" and incident_method == "UPI":
    confidence += 20

# Sufficient number of transactions
if len(incident_df) >= 50:
    confidence += 10

confidence = min(
    confidence,
    100
)

# --------------------------------------------------
# ROOT CAUSE CLASSIFICATION
# --------------------------------------------------

if top_reason_name in [
    "NETWORK_ERROR",
    "TIMEOUT"
]:

    root_cause = (
        "LIKELY PAYMENT NETWORK / "
        "BANK-SIDE CONNECTIVITY DEGRADATION"
    )

elif top_reason_name == "BANK_ERROR":

    root_cause = (
        "LIKELY BANK-SIDE PAYMENT "
        "PROCESSING DEGRADATION"
    )

elif top_reason_name == "INSUFFICIENT_FUNDS":

    root_cause = (
        "LIKELY CUSTOMER-SIDE "
        "FUNDING ISSUE"
    )

elif top_reason_name == "CUSTOMER_CANCELLED":

    root_cause = (
        "LIKELY CUSTOMER "
        "CANCELLATION BEHAVIOR"
    )

else:

    root_cause = (
        "UNKNOWN - FURTHER "
        "INVESTIGATION REQUIRED"
    )

# --------------------------------------------------
# FINAL REPORT
# --------------------------------------------------

print(
    f"\nLikely root cause:"
)

print(root_cause)

print(
    f"\nConfidence: "
    f"{confidence}%"
)

print("\nEvidence:")

print(
    f"• Failure rate increased "
    f"by {failure_rate_increase:.1%}."
)

print(
    f"• Most significant failure reason: "
    f"{top_reason_name}."
)

print(
    f"• {top_reason_name} contribution "
    f"changed by {top_reason_change:+.1%}."
)

print(
    f"• Affected payment route: "
    f"{incident_bank} + {incident_method}."
)

print(
    f"• Transactions during incident: "
    f"{len(incident_df)}."
)

print("\nAnalysis complete.")