import subprocess
import sys


print("=" * 70)
print("PAYPULSE - AI PAYMENT RELIABILITY PLATFORM")
print("=" * 70)


steps = [
    ("Incident Detection", "detect_incidents.py"),
    ("ML Anomaly Detection", "ml_detector.py"),
    ("Incident Aggregation", "aggregate_incidents.py"),
    ("Root Cause Analysis", "analyze_incident.py"),
    ("Financial Impact Analysis", "calculate_impact.py"),
    ("Decision Engine", "decision_engine.py"),
    ("Evidence Fusion", "evidence_fusion.py"),
    ("Unified Incident Analyzer", "incident_analyzer.py"),
]


for name, script in steps:

    print("\n")
    print("=" * 70)
    print(f"RUNNING: {name}")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, script]
    )

    if result.returncode != 0:

        print("\n")
        print("=" * 70)
        print(f"ERROR: {name} failed")
        print("=" * 70)

        sys.exit(1)


print("\n")
print("=" * 70)
print("PAYPULSE PIPELINE COMPLETE")
print("=" * 70)

print("\nAll analysis stages completed successfully.")
print("PayPulse has generated a complete payment incident assessment.")