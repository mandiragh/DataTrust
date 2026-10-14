
import os
import pandas as pd
import psycopg
import streamlit as st

st.set_page_config(
    page_title="DataTrust Monitor",
    page_icon="🛡️",
    layout="wide",
)

st.title("DataTrust Monitor")
st.caption("Data Quality & Reliability Monitoring")


from pathlib import Path

# Load data from PostgreSQL locally or CSV on Streamlit Cloud
csv_path = Path(__file__).parent / "data" / "data_quality_results.csv"

try:
    if os.getenv("DATATRUST_DATA_SOURCE") == "csv":
        # Streamlit Cloud: use exported validation results
        df = pd.read_csv(csv_path)

        df["checked_at"] = pd.to_datetime(
            df["checked_at"], utc=True
        )

    else:
        # Local development: connect to PostgreSQL
        with psycopg.connect(
            host="localhost",
            port=5432,
            dbname="datatrust_db",
            user=os.getenv("PGUSER", os.getenv("USER")),
            connect_timeout=5,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        result_id, run_id, dataset_name,
                        check_name, issue_count, status, checked_at
                    FROM data_quality_results
                    ORDER BY result_id DESC
                """)

                records = cursor.fetchall()
                columns = [col.name for col in cursor.description]

        df = pd.DataFrame(records, columns=columns)

except Exception as error:
    st.error("Unable to load DataTrust validation results.")
    st.exception(error)
    st.stop()

# Ensure consistent ordering regardless of data source
df = df.sort_values("result_id", ascending=False)

# Dataset selector
datasets = df["dataset_name"].dropna().unique().tolist()

selected_dataset = st.selectbox(
    "Select Dataset",
    datasets,
)

dataset_df = df[df["dataset_name"] == selected_dataset].copy()

# Latest validation run
latest_run_id = dataset_df.iloc[0]["run_id"]
latest = dataset_df[
    dataset_df["run_id"] == latest_run_id
].copy()

# Calculate metrics
total = len(latest)
passed = int((latest["status"] == "PASS").sum())
failed = int((latest["status"] == "FAIL").sum())
pass_rate = (passed / total * 100) if total else 0

st.subheader("Latest Validation Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Checks", total)
col2.metric("Passed Checks", passed)
col3.metric("Failed Checks", failed)
col4.metric("Pass Rate", f"{pass_rate:.1f}%")

st.divider()

# Quality issues chart
st.subheader("Data Quality Issues")

chart_data = latest.set_index("check_name")["issue_count"]
st.bar_chart(chart_data)

# Details
st.subheader("Validation Details")

st.dataframe(
    latest[["check_name", "issue_count", "status", "checked_at"]],
    hide_index=True,
    use_container_width=True,
)

# Historical results for selected dataset
st.divider()
st.subheader("Validation History")

history = (
    dataset_df.groupby("run_id", as_index=False)
    .agg(
        checked_at=("checked_at", "max"),
        total_checks=("status", "size"),
        passed_checks=("status", lambda x: (x == "PASS").sum()),
    )
    .sort_values("checked_at")
)

history["pass_rate"] = (
    history["passed_checks"] / history["total_checks"] * 100
)

st.line_chart(
    history.set_index("checked_at")["pass_rate"]
)

st.subheader("Previous Validation Runs")

st.dataframe(
    history[
        ["checked_at", "total_checks", "passed_checks", "pass_rate"]
    ].sort_values("checked_at", ascending=False),
    hide_index=True,
    use_container_width=True,
)

st.caption(
    "Pass rate measures the percentage of checks that passed, "
    "not the percentage of valid transaction records."
)
