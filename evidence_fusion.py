import pandas as pd


print("=" * 70)
print("PAYPULSE - EVIDENCE FUSION ENGINE")
print("=" * 70)


# ---------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------

payments = pd.read_csv("payments.csv")
incidents = pd.read_csv("incidents.csv")
ml = pd.read_csv("ml_anomalies.csv")


# ---------------------------------------------------------
# 2. Prepare timestamps
# ---------------------------------------------------------

payments["timestamp"] = pd.to_datetime(payments["timestamp"])

incidents["start_time"] = pd.to_datetime(incidents["start_time"])
incidents["end_time"] = pd.to_datetime(incidents["end_time"])

ml["timestamp"] = pd.to_datetime(ml["timestamp"])


# ---------------------------------------------------------
# 3. Select primary incident
# ---------------------------------------------------------

incident = incidents.iloc[0]

incident_id = incident["incident_id"]
bank = incident["bank"]
payment_method = incident["payment_method"]

start_time = incident["start_time"]
end_time = incident["end_time"]


# ---------------------------------------------------------
# 4. Get transactions during incident
# ---------------------------------------------------------

incident_data = payments[
    (payments["bank"] == bank) &
    (payments["payment_method"] == payment_method) &
    (payments["timestamp"] >= start_time) &
    (payments["timestamp"] <= end_time)
]


# ---------------------------------------------------------
# 5. Calculate incident failure rate
# ---------------------------------------------------------

incident_transactions = len(incident_data)

incident_failed = (
    incident_data["status"] == "FAILED"
).sum()


if incident_transactions > 0:
    incident_failure_rate = (
        incident_failed / incident_transactions
    )
else:
    incident_failure_rate = 0


# ---------------------------------------------------------
# 6. Calculate baseline
# ---------------------------------------------------------

# Use transactions from the same bank/payment route
# outside the incident period.

baseline_data = payments[
    (payments["bank"] == bank) &
    (payments["payment_method"] == payment_method) &
    (
        (payments["timestamp"] < start_time) |
        (payments["timestamp"] > end_time)
    )
]


baseline_failed = (
    baseline_data["status"] == "FAILED"
).sum()


if len(baseline_data) > 0:
    baseline_failure_rate = (
        baseline_failed / len(baseline_data)
    )
else:
    baseline_failure_rate = 0


# ---------------------------------------------------------
# 7. Failure increase
# ---------------------------------------------------------

failure_increase = (
    incident_failure_rate -
    baseline_failure_rate
)


# ---------------------------------------------------------
# 8. Find matching ML anomalies
# ---------------------------------------------------------

matching_ml = ml[
    (ml["bank"] == bank) &
    (ml["payment_method"] == payment_method) &
    (ml["timestamp"] >= start_time) &
    (ml["timestamp"] <= end_time)
]


# ---------------------------------------------------------
# 9. Evidence scoring
# ---------------------------------------------------------

score = 0
evidence = []


# Signal 1: Severe failure rate

if incident_failure_rate >= 0.30:

    score += 30

    evidence.append(
        "Severe payment failure rate"
    )

elif incident_failure_rate >= 0.15:

    score += 20

    evidence.append(
        "Elevated payment failure rate"
    )


# Signal 2: Increase compared with baseline

if failure_increase >= 0.20:

    score += 25

    evidence.append(
        "Failure rate significantly above baseline"
    )

elif failure_increase >= 0.10:

    score += 15

    evidence.append(
        "Failure rate above baseline"
    )


# Signal 3: ML anomaly

if len(matching_ml) > 0:

    score += 25

    evidence.append(
        "Machine-learning anomaly detected"
    )


# Signal 4: Persistent anomaly

if len(matching_ml) >= 2:

    score += 10

    evidence.append(
        "ML anomaly persisted across multiple observations"
    )


# ---------------------------------------------------------
# 10. Determine confidence
# ---------------------------------------------------------

if score >= 70:

    confidence = "HIGH"
    severity = "HIGH"

elif score >= 45:

    confidence = "MEDIUM"
    severity = "MEDIUM"

else:

    confidence = "LOW"
    severity = "LOW"


# ---------------------------------------------------------
# 11. Recommended action
# ---------------------------------------------------------

if confidence == "HIGH":

    action = "TRAFFIC REDISTRIBUTION"
    priority = "P1"

elif confidence == "MEDIUM":

    action = "INCREASE MONITORING"
    priority = "P2"

else:

    action = "CONTINUE MONITORING"
    priority = "P3"


# ---------------------------------------------------------
# 12. Display results
# ---------------------------------------------------------

print("\nIncident:")
print(f"  ID          : {incident_id}")
print(f"  Route       : {bank} + {payment_method}")
print(f"  Time        : {start_time} -> {end_time}")


print("\nPayment Evidence:")
print(
    f"  Transactions during incident : "
    f"{incident_transactions}"
)

print(
    f"  Failed transactions           : "
    f"{incident_failed}"
)

print(
    f"  Incident failure rate        : "
    f"{incident_failure_rate * 100:.1f}%"
)

print(
    f"  Baseline failure rate        : "
    f"{baseline_failure_rate * 100:.1f}%"
)

print(
    f"  Failure rate increase        : "
    f"{failure_increase * 100:+.1f}%"
)


print("\nML Evidence:")
print(
    f"  Matching ML anomalies        : "
    f"{len(matching_ml)}"
)


print("\nEvidence:")
for item in evidence:
    print(f"  + {item}")


print("\nEvidence Score:")
print(f"  {score}/100")


print("\nAssessment:")
print(f"  Confidence  : {confidence}")
print(f"  Severity    : {severity}")


print("\nRecommended Action:")
print(f"  Action      : {action}")
print(f"  Priority    : {priority}")


# ---------------------------------------------------------
# 13. Save result
# ---------------------------------------------------------

result = pd.DataFrame([{

    "incident_id": incident_id,

    "bank": bank,

    "payment_method": payment_method,

    "start_time": start_time,

    "end_time": end_time,

    "incident_transactions": incident_transactions,

    "failed_transactions": incident_failed,

    "incident_failure_rate":
        incident_failure_rate,

    "baseline_failure_rate":
        baseline_failure_rate,

    "failure_increase":
        failure_increase,

    "ml_matching_anomalies":
        len(matching_ml),

    "evidence_score":
        score,

    "confidence":
        confidence,

    "severity":
        severity,

    "action":
        action,

    "priority":
        priority

}])


result.to_csv(
    "evidence_fusion.csv",
    index=False
)


print(
    "\nEvidence fusion result saved as "
    "evidence_fusion.csv"
)

print("\nEvidence fusion complete.")