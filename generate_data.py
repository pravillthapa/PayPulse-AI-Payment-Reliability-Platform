import numpy as np
import pandas as pd

np.random.seed(42)

# Number of transactions
N = 150_000

# --------------------------------------------------
# 1. GENERATE RANDOM TIMESTAMPS
# --------------------------------------------------

start_time = pd.Timestamp("2026-07-25 00:00:00")
end_time = pd.Timestamp("2026-08-02 23:59:59")

time_range_seconds = int(
    (end_time - start_time).total_seconds()
)

random_seconds = np.random.randint(
    0,
    time_range_seconds,
    N
)

timestamps = (
    start_time
    + pd.to_timedelta(random_seconds, unit="s")
)

timestamps = pd.Series(timestamps).sort_values().reset_index(drop=True)

# --------------------------------------------------
# 2. TRANSACTION IDS
# --------------------------------------------------

transaction_ids = [
    f"TXN{100000 + i}"
    for i in range(N)
]

# --------------------------------------------------
# 3. TRANSACTION AMOUNTS
# --------------------------------------------------

amounts = np.round(
    np.random.lognormal(
        mean=6.5,
        sigma=0.8,
        size=N
    ),
    2
)

amounts = np.clip(amounts, 50, 100000)

# --------------------------------------------------
# 4. PAYMENT METHODS
# --------------------------------------------------

payment_methods = np.random.choice(
    ["UPI", "CARD", "NETBANKING"],
    size=N,
    p=[0.65, 0.25, 0.10]
)

# --------------------------------------------------
# 5. BANKS
# --------------------------------------------------

banks = np.random.choice(
    ["HDFC", "ICICI", "SBI", "AXIS", "KOTAK"],
    size=N,
    p=[0.24, 0.22, 0.24, 0.18, 0.12]
)

# --------------------------------------------------
# 6. CUSTOMER TYPE
# --------------------------------------------------

customer_types = np.random.choice(
    ["NEW", "RETURNING"],
    size=N,
    p=[0.35, 0.65]
)

# --------------------------------------------------
# 7. NORMAL SUCCESS PROBABILITY
# --------------------------------------------------

success_probability = np.full(
    N,
    0.94
)

# --------------------------------------------------
# 8. SIMULATED PAYMENT INCIDENT
# --------------------------------------------------

# HDFC + UPI suffers a degradation on August 1
# between 18:00 and 20:00.

incident_mask = (
    (banks == "HDFC")
    & (payment_methods == "UPI")
    & (timestamps >= "2026-08-01 18:00:00")
    & (timestamps < "2026-08-01 20:00:00")
)

success_probability[incident_mask] = 0.55

# --------------------------------------------------
# 9. GENERATE PAYMENT OUTCOMES
# --------------------------------------------------

random_values = np.random.random(N)

successful = random_values < success_probability

status = np.where(
    successful,
    "SUCCESS",
    "FAILED"
)

# --------------------------------------------------
# 10. FAILURE REASONS
# --------------------------------------------------

failure_reasons = np.full(
    N,
    None,
    dtype=object
)

failed_mask = status == "FAILED"

failure_reasons[failed_mask] = np.random.choice(
    [
        "TIMEOUT",
        "BANK_ERROR",
        "INSUFFICIENT_FUNDS",
        "NETWORK_ERROR",
        "CUSTOMER_CANCELLED"
    ],
    size=failed_mask.sum(),
    p=[0.25, 0.25, 0.20, 0.20, 0.10]
)

# --------------------------------------------------
# 11. RETRY COUNT
# --------------------------------------------------

retry_count = np.where(
    status == "FAILED",
    np.random.choice(
        [0, 1, 2],
        size=N,
        p=[0.60, 0.30, 0.10]
    ),
    0
)

# --------------------------------------------------
# 12. CREATE DATAFRAME
# --------------------------------------------------

df = pd.DataFrame({
    "transaction_id": transaction_ids,
    "timestamp": timestamps,
    "amount": amounts,
    "payment_method": payment_methods,
    "bank": banks,
    "customer_type": customer_types,
    "status": status,
    "failure_reason": failure_reasons,
    "retry_count": retry_count
})

# --------------------------------------------------
# 13. SAVE DATA
# --------------------------------------------------

df.to_csv(
    "payments.csv",
    index=False
)

# --------------------------------------------------
# 14. SUMMARY
# --------------------------------------------------

print("=" * 60)
print("PAYPULSE PAYMENT DATASET")
print("=" * 60)

print(f"Total transactions : {len(df):,}")

successful_count = (
    df["status"] == "SUCCESS"
).sum()

failed_count = (
    df["status"] == "FAILED"
).sum()

print(f"Successful payments: {successful_count:,}")
print(f"Failed payments    : {failed_count:,}")

success_rate = (
    successful_count / len(df)
) * 100

print(f"Overall success rate: {success_rate:.2f}%")

print(
    f"\nData period: "
    f"{df['timestamp'].min()} "
    f"to "
    f"{df['timestamp'].max()}"
)

print("\nDataset saved as payments.csv")