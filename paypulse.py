import subprocess
import sys


def run_step(script):
    print("\n" + "=" * 70)
    print(f"RUNNING: {script}")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, script]
    )

    if result.returncode != 0:
        print(f"\nERROR: {script} failed.")
        sys.exit(result.returncode)


print("=" * 70)
print("PAYPULSE - PAYMENT INCIDENT INTELLIGENCE PLATFORM")
print("=" * 70)

print("\nStarting PayPulse pipeline...")

# 1. Generate payment data
run_step("generate_data.py")

# 2. Detect abnormal payment behavior
run_step("detect_incidents.py")

# 3. Group related alerts into incidents
run_step("aggregate_incidents.py")

# 4. Analyze the complete incident
run_step("incident_analyzer.py")

print("\n" + "=" * 70)
print("PAYPULSE PIPELINE COMPLETE")
print("=" * 70)

print("\nGenerated outputs:")
print("  payments.csv")
print("  detected_incidents.csv")
print("  incidents.csv")
print("  incident_report.csv")

print("\nPayPulse successfully analyzed the payment environment.")