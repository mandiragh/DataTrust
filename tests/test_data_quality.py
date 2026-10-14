
import pandas as pd


# Create a small sample dataset with known errors
def sample_transactions():
    return pd.DataFrame({
        "transaction_id": [101, 102, 102, 104],
        "customer_id": [1, 2, None, 999],
        "amount": [100, 200, -50, 300],
        "status": ["completed", "pending", "failed", "unknown"]
    })


# Test 1: Detect duplicate transaction IDs
def test_duplicate_transaction_ids():
    df = sample_transactions()

    duplicates = df["transaction_id"].duplicated().sum()

    assert duplicates == 1


# Test 2: Detect missing customer IDs
def test_missing_customer_ids():
    df = sample_transactions()

    missing = df["customer_id"].isna().sum()

    assert missing == 1


# Test 3: Detect negative amounts
def test_negative_amounts():
    df = sample_transactions()

    negative = (df["amount"] < 0).sum()

    assert negative == 1


# Test 4: Detect invalid transaction statuses
def test_invalid_statuses():
    df = sample_transactions()

    valid_statuses = ["completed", "pending", "failed"]

    invalid = (~df["status"].isin(valid_statuses)).sum()

    assert invalid == 1


# Test 5: Detect customer IDs that do not exist
def test_unknown_customer_ids():
    df = sample_transactions()

    valid_customer_ids = [1, 2, 3]

    unknown = (
        df["customer_id"].notna()
        & ~df["customer_id"].isin(valid_customer_ids)
    ).sum()

    assert unknown == 1
