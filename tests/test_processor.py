import pandas as pd

from property_data_cleaning.processor import PropertyDataCleaner


def test_property_data_cleaner_runs():
    cleaner = PropertyDataCleaner()
    raw = pd.DataFrame([
        {"address": "123 main st", "parcel_id": "A-1", "owner_name": "Acme", "tax_value": None}
    ])

    cleaned = cleaner.run(raw)

    assert "validation_issues" in cleaned.columns
    assert cleaned.iloc[0]["parcel_id"] == "A1"
    assert cleaned.iloc[0]["tax_value"] == 0
