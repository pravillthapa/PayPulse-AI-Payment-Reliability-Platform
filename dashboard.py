from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PayPulse Dashboard
# Payment Reliability & Incident Intelligence Platform
# ============================================================

st.set_page_config(
    page_title="PayPulse",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Global UI styling — Step 1
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.20);
    }

    [data-testid="stSidebar"] h1 {
        font-size: 1.65rem;
        margin-bottom: 0.25rem;
    }

    [data-testid="stSidebar"] .stRadio > label {
        font-weight: 600;
    }

    [data-testid="stMetric"] {
        padding: 1rem 1.05rem;
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 14px;
        background: rgba(128, 128, 128, 0.035);
        min-height: 112px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.82rem;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.65rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    hr {
        margin: 1.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)



# ============================================================
# Helpers
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


def load_csv(filename):
    """Load a CSV from the PayPulse project folder."""
    path = BASE_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def find_column(df, candidates):
    """Return the first matching column from a list of candidates."""
    if df.empty:
        return None

    lookup = {str(col).strip().lower(): col for col in df.columns}

    for candidate in candidates:
        key = candidate.strip().lower()
        if key in lookup:
            return lookup[key]

    # Also allow partial matches.
    for col in df.columns:
        col_lower = str(col).strip().lower()
        for candidate in candidates:
            if candidate.strip().lower() in col_lower:
                return col

    return None


def format_inr(value):
    try:
        return f"₹{float(value):,.0f}"
    except Exception:
        return "₹0"


def safe_numeric(df, column):
    if column is None or df.empty:
        return pd.Series(dtype="float64")
    return pd.to_numeric(df[column], errors="coerce")


def failure_mask(df):
    """Identify failed transactions across common status formats."""
    status_col = find_column(df, ["status", "payment_status", "transaction_status"])

    if status_col is None:
        return pd.Series(False, index=df.index)

    values = df[status_col].astype(str).str.upper().str.strip()

    return values.isin(
        [
            "FAILED",
            "FAILURE",
            "FAIL",
            "DECLINED",
            "REJECTED",
            "ERROR",
        ]
    )


def success_mask(df):
    """Identify successful transactions across common status formats."""
    status_col = find_column(df, ["status", "payment_status", "transaction_status"])

    if status_col is None:
        return pd.Series(False, index=df.index)

    values = df[status_col].astype(str).str.upper().str.strip()

    return values.isin(
        [
            "SUCCESS",
            "SUCCESSFUL",
            "SUCCEEDED",
            "COMPLETED",
            "PAID",
        ]
    )


# ============================================================
# Load project data
# ============================================================

payments = load_csv("payments.csv")
incidents = load_csv("incidents.csv")
detected_incidents = load_csv("detected_incidents.csv")
incident_report = load_csv("incident_report.csv")
ml_anomalies = load_csv("ml_anomalies.csv")
ml_anomaly_results = load_csv("ml_anomaly_results.csv")


# ============================================================
# Derived payment metrics
# ============================================================

amount_col = find_column(
    payments,
    ["amount", "transaction_amount", "payment_amount", "value", "gmv"],
)

bank_col = find_column(
    payments,
    ["bank", "bank_name", "issuer_bank"],
)

method_col = find_column(
    payments,
    ["payment_method", "method", "payment_type", "channel", "instrument"],
)

status_col = find_column(
    payments,
    ["status", "payment_status", "transaction_status"],
)

amounts = safe_numeric(payments, amount_col)

total_transactions = len(payments)

successful = int(success_mask(payments).sum())
failed = int(failure_mask(payments).sum())

# If the dataset uses statuses we don't recognize, use the
# total minus failures so the dashboard still works.
if successful == 0 and failed > 0:
    successful = max(total_transactions - failed, 0)

if total_transactions > 0:
    success_rate = successful / total_transactions * 100
    failure_rate = failed / total_transactions * 100
else:
    success_rate = 0.0
    failure_rate = 0.0

total_gmv = float(amounts.sum()) if not amounts.empty else 0.0
avg_transaction = float(amounts.mean()) if not amounts.empty else 0.0
failed_gmv = (
    float(amounts[failure_mask(payments)].sum())
    if not amounts.empty
    else 0.0
)


# ============================================================
# Sidebar
# ============================================================

st.sidebar.title("💳 PayPulse")

st.sidebar.caption(
    "Payment Reliability Intelligence"
)

st.sidebar.divider()

st.sidebar.subheader("Navigation")

page = st.sidebar.radio(
    "Choose a workspace",
    [
        "📊 Overview",
        "🚨 Incident Intelligence",
        "💳 Payment Analytics",
        "🤖 ML Anomalies",
    ],
    label_visibility="collapsed",
)

# Convert navigation label back to the page name
page = page.split(" ", 1)[1]

st.sidebar.divider()

st.sidebar.subheader("System Status")

st.sidebar.success("All systems operational")

st.sidebar.divider()

st.sidebar.caption("PayPulse v1.0")
st.sidebar.caption("Payment monitoring & decision intelligence")


# ============================================================
# Header
# ============================================================

st.markdown(
    """
    <style>
    .paypulse-header {
        padding: 28px 32px;
        border: 1px solid #263142;
        border-radius: 18px;
        background: linear-gradient(135deg, #111722, #0d1119);
        margin-bottom: 32px;
    }

    .paypulse-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .paypulse-subtitle {
        font-size: 18px;
        color: #aeb7c5;
        margin-bottom: 18px;
    }

    .status {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 999px;
        background: #123c2a;
        color: #5ee39b;
        font-weight: 600;
        font-size: 14px;
    }
    </style>

    <div class="paypulse-header">
        <div class="paypulse-title">💳 PayPulse</div>
        <div class="paypulse-subtitle">
            Real-time payment monitoring, incident intelligence, and anomaly detection
        </div>
        <div class="status">● LIVE PAYMENT MONITORING</div>    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    st.header("📊 OVERVIEW")

    st.caption(
        "A real-time summary of payment reliability, transaction performance, "
    "and key operational risks."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Transactions",
        f"{total_transactions:,}",
        help="Total number of payment transactions analysed.",
    )

    col2.metric(
        "Success Rate",
        f"{success_rate:.2f}%",
        help="Percentage of transactions completed successfully.",
    )

    col3.metric(
        "Failed Transactions",
        f"{failed:,}",
        help="Number of transactions that were unsuccessful.",
    )

    col4.metric(
        "Total GMV",
        f"₹{total_gmv:,.0f}",
        help="Total value of all payment transactions processed.",
    )

    st.divider()

    # --------------------------------------------------------
    # Active Incident
    # --------------------------------------------------------

    st.header("🚨 Attention Required")

    st.caption(
        "Current payment issues requiring immediate investigation."
    )

    incident_source = (
        detected_incidents
        if not detected_incidents.empty
        else incidents
    )

    if not incident_source.empty:

        incident_id_col = find_column(
            incident_source,
            ["incident_id", "id", "incident"],
        )

        title_col = find_column(
            incident_source,
            ["title", "name", "description", "incident_name"],
        )

        bank_incident_col = find_column(
            incident_source,
            ["bank", "bank_name"],
        )

        method_incident_col = find_column(
            incident_source,
            ["payment_method", "method", "channel"],
        )

        severity_incident_col = find_column(
            incident_source,
            ["severity", "priority", "level", "risk"],
        )

        iincident_id = "ACTIVE INCIDENT"

        incident_title = (
            str(incident_source.iloc[0][title_col])
            if title_col
            else "Payment reliability incident detected"
        )

        incident_bank = (
            str(incident_source.iloc[0][bank_incident_col])
            if bank_incident_col
            else "Unknown"
        )

        incident_method = (
            str(incident_source.iloc[0][method_incident_col])
            if method_incident_col
            else "Unknown"
        )

        incident_severity = (
            str(incident_source.iloc[0][severity_incident_col]).upper()
            if severity_incident_col
            else "HIGH"
        )

        with st.container(border=True):

            st.markdown(
                f"### 🔴 Payment Reliability Incident Detected"
            )

            st.caption(
                "Payment reliability incident currently requiring attention."
            )

            i1, i2, i3, i4 = st.columns(4)

            i1.metric(
                "Status",
                "ACTIVE",
            )

            i2.metric(
                "Bank",
                incident_bank,
            )

            i3.metric(
                "Payment Method",
                incident_method,
            )

            i4.metric(
                "Severity",
                incident_severity,
            )

    else:
        st.success("✓ No active incidents detected.")

    st.divider()

       # --------------------------------------------------------
    # Payment Status
    # --------------------------------------------------------

    st.subheader("💳 Payment Health")
    st.caption("Overall reliability of payment processing across the platform.")

    if total_transactions > 0:

        success_percentage = (
            successful / total_transactions
        )

        failed_percentage = (
            failed / total_transactions
        )

        status_col1, status_col2 = st.columns(2)

        with status_col1:
            st.metric(
                "Successful",
                f"{successful:,}",
                f"{success_percentage * 100:.2f}%",
            )

        with status_col2:
            st.metric(
                "Failed",
                f"{failed:,}",
                f"{failed_percentage * 100:.2f}%",
            )

        st.progress(
            success_percentage,
            text=f"Payment success rate — {success_percentage * 100:.2f}%",
        )

    else:
        st.warning("No payment data available.")

    st.divider()

    # --------------------------------------------------------
    # Dataset Summary
    # --------------------------------------------------------

    st.subheader("📈 Business Snapshot")
    st.caption("Key transaction and financial indicators from the current dataset.")

    summary_c1, summary_c2 = st.columns(2)

    with summary_c1:
        st.metric(
            "💰 Total GMV",
            f"₹{total_gmv:,.0f}"
        )

    with summary_c2:
        st.metric(
            "💳 Average Transaction",
            f"₹{avg_transaction:,.0f}"
        )


# ============================================================
# INCIDENT INTELLIGENCE
# ============================================================

if page == "Incident Intelligence":

    st.header("🚨 Incident Intelligence")

    st.caption(
        "Investigate detected payment incidents, assess their financial impact, and identify recommended actions."
    )

    source = (
        incident_report
        if not incident_report.empty
        else detected_incidents
    )

    if source.empty:
        source = incidents

    if source.empty:
        st.warning("No incident data was found.")
    else:

        # --------------------------------------------------------
        # Incident Overview
        # --------------------------------------------------------
        st.subheader("Incident Overview")
        st.caption(
            "Key indicators for the most significant detected incident."
        )

        incident_row = source.iloc[0]

        incident_failure_rate_col = find_column(
            source,
            ["incident_failure_rate", "failure_rate"],
        )

        failed_gmv_col = find_column(
            source,
            ["failed_gmv", "failure_gmv"],
        )

        severity_col = find_column(
            source,
            ["severity", "priority", "level", "risk"],
        )

        action_col = find_column(
            source,
            ["recommended_action", "action", "recommendation"],
        )

        overview_c1, overview_c2, overview_c3 = st.columns(3)

        with overview_c1:
            if incident_failure_rate_col:
                failure_value = pd.to_numeric(
                    incident_row[incident_failure_rate_col],
                    errors="coerce",
                )

                if pd.notna(failure_value):
                    st.metric(
                        "Incident Failure Rate",
                        f"{failure_value * 100:.2f}%",
                    )
                else:
                    st.metric("Incident Failure Rate", "N/A")
            else:
                st.metric("Incident Failure Rate", "N/A")

        with overview_c2:
            st.metric(
                "Total GMV",
                format_inr(total_gmv),
            )

        with overview_c3:
            if severity_col:
               st.metric(
                   "Severity",
                   str(incident_row[severity_col]).upper(),
                )
            else:
                st.metric("Severity", "N/A")

        if action_col:
            st.info(
                f"💡 **Recommended Action:** {str(incident_row[action_col])}"
            )
        st.divider()
                


# ============================================================
# PAYMENT ANALYTICS
# ============================================================

elif page == "Payment Analytics":

    st.header("📈 Payment Analytics")

    st.caption(
        "Analyse payment performance, failure patterns, and financial impact across banks and payment methods."
    )

    # --------------------------------------------------------
    # Payment Method Performance
    # --------------------------------------------------------

    left, right = st.columns(2)

    with left:
        st.subheader("Payment Method Performance")
        st.caption("Failure rate by payment method.")

        if method_col:
            method_failure = (
                payments.assign(_failed=failure_mask(payments))
                .groupby(method_col)["_failed"]
                .mean()
                .mul(100)
                .sort_values(ascending=False)
            )

            if not method_failure.empty:
                method_failure.name = "Failure Rate (%)"

                st.bar_chart(
                    method_failure,
                    height=320,
                )
            else:
                st.info("No payment method data available.")
        else:
            st.info("Payment method column not found.")

    with right:
        st.subheader("Bank Performance")
        st.caption("Failure rate by issuing bank.")

        if bank_col:
            bank_failure = (
                payments.assign(_failed=failure_mask(payments))
                .groupby(bank_col)["_failed"]
                .mean()
                .mul(100)
                .sort_values(ascending=False)
            )

            if not bank_failure.empty:
                bank_failure.name = "Failure Rate (%)"

                st.bar_chart(
                    bank_failure,
                    height=320,
                )
            else:
                st.info("No bank data available.")
        else:
            st.info("Bank column not found.")

    st.divider()

    # --------------------------------------------------------
    # Transaction Amount Distribution
    # --------------------------------------------------------

    st.subheader("Transaction Amount Distribution")

    if not amounts.empty:

        # Use fixed, meaningful ranges instead of many equal-width
        # bins. This avoids slow rendering and unreadable labels.
        bins = [
            0,
            500,
            1000,
            1500,
            2000,
            3000,
            5000,
            10000,
            25000,
            50000,
            float("inf"),
        ]

        labels = [
            "₹0–500",
            "₹500–1K",
            "₹1K–1.5K",
            "₹1.5K–2K",
            "₹2K–3K",
            "₹3K–5K",
            "₹5K–10K",
            "₹10K–25K",
            "₹25K–50K",
            "₹50K+",
        ]

        amount_distribution = (
            pd.cut(
                amounts,
                bins=bins,
                labels=labels,
                include_lowest=True,
            )
            .value_counts()
            .reindex(labels, fill_value=0)
        )

        import altair as alt

        chart_data = amount_distribution.reset_index()
        chart_data.columns = ["Amount Range", "Transaction Count"]

        chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                x=alt.X(
                    "Amount Range:N",
                    sort=labels,
                    title="Transaction Amount",
                ),
                y=alt.Y(
                    "Transaction Count:Q",
                    title="Number of Transactions",
                    scale=alt.Scale(domainMin=0),
                ),
                tooltip=[
                    "Amount Range:N",
                     "Transaction Count:Q",
                ],
            )
            .properties(height=400)
        )
        st.altair_chart(chart, use_container_width=True)

    else:
        st.warning("Transaction amount column was not found.")

    st.divider()

    # --------------------------------------------------------
    # Key Analytics
    # --------------------------------------------------------

    st.subheader("Key Payment Metrics")
    st.caption("Key financial and reliability indicators.")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total GMV",
        format_inr(total_gmv),
    )

    c2.metric(
        "Average Transaction",
        format_inr(avg_transaction),
    )

    c3, c4 = st.columns(2)

    c3.metric(
        "Failure Rate",
        f"{failure_rate:.2f}%",
    )

    c4.metric(
        "Failed GMV",
        format_inr(failed_gmv),
    )


# ============================================================
# ML ANOMALIES
# ============================================================

elif page == "ML Anomalies":

    # ============================================================
    # ML ANOMALIES
    # ============================================================

    st.header("🤖 ML Anomalies")

    st.caption(
        "Machine-learning based identification of unusual payment behaviour "
        "and high-risk transactions."
    )

    # ============================================================
    # LOAD ANOMALY DATA
    # ============================================================

    source = (
        ml_anomaly_results
        if not ml_anomaly_results.empty
        else ml_anomalies
    )

    if source.empty:

        st.warning("No ML anomaly data was found.")

    else:

        # ============================================================
        # DETECT RELEVANT COLUMNS
        # ============================================================

        anomaly_col = find_column(
            source,
            [
                "anomaly",
                "is_anomaly",
                "anomaly_flag",
                "outlier",
                "prediction",
            ],
        )

        score_col = find_column(
            source,
            [
                "anomaly_score",
                "score",
                "risk_score",
            ],
        )

        payment_method_col = find_column(
            source,
            [
                "payment_method",
                "payment method",
                "payment_type",
                "method",
            ],
        )

        bank_col = find_column(
            source,
            [
                "bank",
                "bank_name",
                "issuing_bank",
            ],
        )


        # ============================================================
        # DETECT ANOMALIES
        # ============================================================

        if score_col:

            numeric_scores = pd.to_numeric(
                source[score_col],
                errors="coerce",
            )

            valid_scores = numeric_scores.dropna()

            if not valid_scores.empty:

                # Lowest 5% of scores are considered anomalies.
                anomaly_threshold = valid_scores.quantile(0.05)

                anomaly_mask = (
                    numeric_scores <= anomaly_threshold
                )

                anomaly_results = source[
                    anomaly_mask
                ].copy()

            else:

                anomaly_results = pd.DataFrame()

        elif anomaly_col:

            anomaly_values = source[anomaly_col]

            if pd.api.types.is_bool_dtype(anomaly_values):

                anomaly_mask = anomaly_values

            else:

                normalized = (
                    anomaly_values
                    .astype(str)
                    .str.upper()
                    .str.strip()
                )

                anomaly_mask = normalized.isin(
                    [
                        "1",
                        "TRUE",
                        "YES",
                        "ANOMALY",
                        "ANOMALOUS",
                        "-1",
                    ]
                )

            anomaly_results = source[
                anomaly_mask
            ].copy()

        else:

            anomaly_results = pd.DataFrame()


        # ============================================================
        # CALCULATE METRICS
        # ============================================================

        anomaly_count = len(anomaly_results)

        if len(source) > 0:

            anomaly_rate = (
                anomaly_count / len(source) * 100
            )

        else:

            anomaly_rate = 0


        # ============================================================
        # RISK CLASSIFICATION
        # ============================================================

        if (
            not anomaly_results.empty
            and score_col
        ):

            anomaly_results["_numeric_score"] = pd.to_numeric(
                anomaly_results[score_col],
                errors="coerce",
            )

            valid_scores = pd.to_numeric(
                source[score_col],
                errors="coerce",
            ).dropna()

            high_risk_threshold = valid_scores.quantile(0.01)

            medium_risk_threshold = valid_scores.quantile(0.03)


            def classify_risk(score):

                if score <= high_risk_threshold:

                    return "🔴 High"

                elif score <= medium_risk_threshold:

                    return "🟠 Medium"

                else:

                    return "🟡 Low"


            anomaly_results["Risk Level"] = (
                anomaly_results["_numeric_score"]
                .apply(classify_risk)
            )

            anomaly_results = anomaly_results.sort_values(
                "_numeric_score",
                ascending=True,
            )

            anomaly_results = anomaly_results.drop(
                columns=["_numeric_score"]
            )


        # ============================================================
        # DETECTION OVERVIEW
        # ============================================================

        st.subheader("Detection Overview")

        overview_c1, overview_c2, overview_c3 = st.columns(3)

        with overview_c1:

            st.metric(
                "Records Analysed",
                f"{len(source):,}",
            )

        with overview_c2:

            st.metric(
                "Anomalies Detected",
                f"{anomaly_count:,}",
            )

        with overview_c3:

            st.metric(
                "Anomaly Rate",
                f"{anomaly_rate:.2f}%",
            )


        st.divider()


        # ============================================================
        # KEY INSIGHTS
        # ============================================================

        st.subheader("🔍 Key Insights")

        if not anomaly_results.empty:

            insight_c1, insight_c2, insight_c3 = st.columns(3)


            # Highest-risk payment method
            if payment_method_col:

                payment_counts = (
                    anomaly_results[payment_method_col]
                    .astype(str)
                    .value_counts()
                )

                top_payment_method = payment_counts.idxmax()

                top_payment_count = payment_counts.max()

                with insight_c1:

                    st.info(
                        f"💳 **{top_payment_method}** has the highest "
                        f"anomaly activity ({top_payment_count} anomalies)."
                    )


            # Bank with most anomalies
            if bank_col:

                bank_counts = (
                    anomaly_results[bank_col]
                    .astype(str)
                    .value_counts()
                )

                top_bank = bank_counts.idxmax()

                top_bank_count = bank_counts.max()

                with insight_c2:

                    st.info(
                        f"🏦 **{top_bank}** has the highest "
                        f"anomaly activity ({top_bank_count} anomalies)."
                    )


            # High-risk count
            if "Risk Level" in anomaly_results.columns:

                high_risk_count = (
                    anomaly_results["Risk Level"]
                    .astype(str)
                    .str.contains("High")
                    .sum()
                )

                with insight_c3:

                    st.info(
                        f"🚨 **{high_risk_count} transactions** "
                        f"require immediate attention."
                    )


        st.divider()


        # ============================================================
        # ANOMALY ANALYSIS
        # ============================================================

        st.subheader("📊 Anomaly Analysis")


        # -------------------------
        # PAYMENT METHOD ANALYSIS
        # -------------------------

        if payment_method_col:

            st.markdown("#### Anomalies by Payment Method")

            payment_anomalies = (
                anomaly_results[payment_method_col]
                .astype(str)
                .value_counts()
            )

            if not payment_anomalies.empty:

                st.bar_chart(payment_anomalies)


        # -------------------------
        # BANK ANALYSIS
        # -------------------------

        if bank_col:

            st.markdown("#### Anomalies by Bank")

            bank_anomalies = (
                anomaly_results[bank_col]
                .astype(str)
                .value_counts()
            )

            if not bank_anomalies.empty:

                st.bar_chart(bank_anomalies)

        # -------------------------
        # ANOMALY TREND OVER TIME
        # -------------------------

        timestamp_col = find_column(
            anomaly_results,
            [
                "timestamp",
                "date",
                "transaction_date",
                "datetime",
            ],
        )

        if timestamp_col and not anomaly_results.empty:

            st.markdown("#### Anomaly Trend Over Time")

            st.caption(
                "Changes in detected anomalous payment activity over time."
            )

            trend_data = anomaly_results.copy()

            trend_data[timestamp_col] = pd.to_datetime(
                trend_data[timestamp_col],
                errors="coerce",
            )

            trend_data = trend_data.dropna(
                subset=[timestamp_col]
            )

            if not trend_data.empty:

                daily_anomalies = (
                    trend_data
                    .groupby(
                        trend_data[timestamp_col].dt.date
                    )
                    .size()
                )

                st.line_chart(daily_anomalies)

            else:

                st.info("No valid timestamp data available.")

        else:

            st.info(
                "No timestamp data available for anomaly trend analysis."
            )


        st.divider()


        # ============================================================
        # RISK ANALYSIS
        # ============================================================

        st.subheader("🚨 Risk Analysis")

        if (
            not anomaly_results.empty
            and "Risk Level" in anomaly_results.columns
        ):

            high_risk_count = (
                anomaly_results["Risk Level"]
                .astype(str)
                .str.contains("High")
                .sum()
            )

            medium_risk_count = (
                anomaly_results["Risk Level"]
                .astype(str)
                .str.contains("Medium")
                .sum()
            )

            low_risk_count = (
                anomaly_results["Risk Level"]
                .astype(str)
                .str.contains("Low")
                .sum()
            )

            risk_c1, risk_c2, risk_c3 = st.columns(3)

            with risk_c1:

                st.metric(
                    "🔴 High Risk",
                    f"{high_risk_count:,}",
                )

            with risk_c2:

                st.metric(
                    "🟠 Medium Risk",
                    f"{medium_risk_count:,}",
                )

            with risk_c3:

                st.metric(
                    "🟡 Low Risk",
                    f"{low_risk_count:,}",
                )


        st.divider()


        # ============================================================
        # HIGH-RISK TRANSACTIONS
        # ============================================================

        st.subheader("🚨 High-Risk Transactions")

        st.caption(
            "Transactions ranked by anomaly score, with the most unusual "
            "activity displayed first."
        )

        if not anomaly_results.empty:

            st.dataframe(
                anomaly_results.head(100),
                width="stretch",
                hide_index=True,
            )

        else:

            st.success("No anomalous records detected.")


# ============================================================
# Footer
# ============================================================

st.divider()

footer_left, footer_right = st.columns(2)

with footer_left:
    st.caption(
        "💳 PayPulse — Payment Reliability & Incident Intelligence"
    )

with footer_right:
    st.caption(
        "Powered by Data Analytics & Machine Learning"
    )
