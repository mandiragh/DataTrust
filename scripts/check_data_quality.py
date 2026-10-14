
import os
import uuid
import psycopg

# Connect to PostgreSQL
connection = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="datatrust_db",
    user=os.getenv("PGUSER", os.getenv("USER")),
)

# Only these approved tables can be checked
datasets = ["transactions", "transactions_clean"]

# Each check should return the number of issues
checks = {
    "Duplicate transaction IDs": """
        SELECT COUNT(*) - COUNT(DISTINCT transaction_id)
        FROM {table}
    """,
    "Missing customer IDs": """
        SELECT COUNT(*)
        FROM {table}
        WHERE customer_id IS NULL
    """,
    "Unknown customer IDs": """
        SELECT COUNT(*)
        FROM {table} t
        LEFT JOIN customers c
            ON t.customer_id = c.customer_id
        WHERE t.customer_id IS NOT NULL
          AND c.customer_id IS NULL
    """,
    "Negative amounts": """
        SELECT COUNT(*)
        FROM {table}
        WHERE amount < 0
    """,
    "Invalid statuses": """
        SELECT COUNT(*)
        FROM {table}
        WHERE status IS NULL
           OR LOWER(TRIM(status)) NOT IN
              ('completed', 'pending', 'failed')
    """
}

run_id = uuid.uuid4()

print("\n===== DATATRUST QUALITY REPORT =====")
print(f"Run ID: {run_id}")

with connection:
    with connection.cursor() as cursor:
        for dataset in datasets:
            print(f"\nDataset: {dataset}")

            for check_name, query_template in checks.items():
                # Safe: dataset names are from our fixed allowlist
                query = query_template.format(table=dataset)

                cursor.execute(query)
                issue_count = cursor.fetchone()[0]
                status = "PASS" if issue_count == 0 else "FAIL"

                print(f"{check_name}: {issue_count} issues — {status}")

                cursor.execute(
                    """
                    INSERT INTO data_quality_results
                        (run_id, dataset_name, check_name,
                         issue_count, status)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (run_id, dataset, check_name,
                     issue_count, status)
                )

print("\nValidation results saved successfully!")
