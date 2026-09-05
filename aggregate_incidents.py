import pandas as pd

# --------------------------------------------------
# LOAD DETECTED INCIDENTS
# --------------------------------------------------

df = pd.read_csv("detected_incidents.csv")

# Make sure hour is treated as datetime
df["hour"] = pd.to_datetime(df["hour"])

# Sort chronologically
df = df.sort_values(
    ["bank", "payment_method", "hour"]
).reset_index(drop=True)

# --------------------------------------------------
# GROUP RELATED ALERTS INTO INCIDENTS
# --------------------------------------------------

incidents = []

incident_number = 1

for (bank, method), group in df.groupby(
    ["bank", "payment_method"]
):

    group = group.sort_values("hour")

    current_start = None
    current_end = None

    for _, row in group.iterrows():

        current_hour = row["hour"]

        # Start a new incident
        if current_start is None:

            current_start = current_hour
            current_end = current_hour

        # Continue the existing incident
        elif (
            current_hour
            - current_end
            <= pd.Timedelta(hours=1)
        ):

            current_end = current_hour

        # Gap means previous incident ended
        else:

            incidents.append({
                "incident_id":
                    f"INC-{incident_number:03d}",

                "bank":
                    bank,

                "payment_method":
                    method,

                "start_time":
                    current_start,

                "end_time":
                    current_end
                    + pd.Timedelta(hours=1),

                "duration_hours":
                    (
                        (
                            current_end
                            - current_start
                        ).total_seconds()
                        / 3600
                    ) + 1
            })

            incident_number += 1

            current_start = current_hour
            current_end = current_hour

    # Save final incident for this group
    if current_start is not None:

        incidents.append({
            "incident_id":
                f"INC-{incident_number:03d}",

            "bank":
                bank,

            "payment_method":
                method,

            "start_time":
                current_start,

            "end_time":
                current_end
                + pd.Timedelta(hours=1),

            "duration_hours":
                (
                    (
                        current_end
                        - current_start
                    ).total_seconds()
                    / 3600
                ) + 1
        })

        incident_number += 1

# --------------------------------------------------
# CREATE INCIDENT TABLE
# --------------------------------------------------

incident_df = pd.DataFrame(incidents)

# --------------------------------------------------
# SAVE
# --------------------------------------------------

incident_df.to_csv(
    "incidents.csv",
    index=False
)

# --------------------------------------------------
# DISPLAY
# --------------------------------------------------

print("=" * 70)
print("PAYPULSE - INCIDENT AGGREGATION")
print("=" * 70)

print(
    f"\nDetected alerts : {len(df)}"
)

print(
    f"Actual incidents: {len(incident_df)}"
)

print("\nIncident summary:")
print("-" * 70)

for _, incident in incident_df.iterrows():

    print(
        f"{incident['incident_id']} | "
        f"{incident['bank']} | "
        f"{incident['payment_method']} | "
        f"{incident['start_time']} → "
        f"{incident['end_time']} | "
        f"Duration: "
        f"{incident['duration_hours']:.0f}h"
    )

print(
    "\nIncident data saved as incidents.csv"
)