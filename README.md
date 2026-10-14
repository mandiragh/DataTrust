# DataTrust — Data Quality Monitoring

DataTrust is a Python and PostgreSQL project that checks transaction data for common quality problems and tracks the results in a Streamlit dashboard.

## What I Built

- Loaded customer and transaction datasets into **PostgreSQL**.
- Created **SQL and Python checks** for duplicate transaction IDs, missing or unknown customer IDs, negative amounts, and invalid statuses.
- Saved each validation run and its pass/fail results in PostgreSQL.
- Created a separate reporting table that excludes negative-amount transactions while preserving the original data.
- Built a **Streamlit dashboard** to compare datasets, review detected issues, and see validation history.
- Added **pytest tests** for the basic validation rules.

## Results

The original dataset has **1,000 transactions** and the filtered reporting dataset has **995**. The negative-amount check passes for the filtered dataset, while other checks still highlight issues that need attention.

The dashboard shows the number of checks passed or failed, issues found by each check, and how results differ between validation runs and datasets.

## Tools

**Python · SQL · PostgreSQL · Pandas · Psycopg · Streamlit · pytest**

## How to Run Locally

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

With a local PostgreSQL database named `datatrust_db` and the project tables populated, run the validation script:

```bash
python scripts/check_data_quality.py
```

Start the dashboard:

```bash
python -m streamlit run dashboard/app.py
```

Run the sample validation tests:

```bash
python -m pytest tests/ -v
```

*This portfolio project uses sample customer and transaction data. The current dashboard reads results from a local PostgreSQL database.*
