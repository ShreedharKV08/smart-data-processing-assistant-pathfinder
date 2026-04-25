"""Rule-based validation for property records."""

import pandas as pd
from typing import List


class RuleValidator:
    """Validates property data against business rules."""

    # def validate(self, df: pd.DataFrame) -> List[str]:
    #     issues = []
    #     if "parcel_id" in df.columns:
    #         invalid_ids = df["parcel_id"].astype(str).str.len() < 3
    #         if invalid_ids.any():
    #             issues.append("Invalid parcel IDs detected")
    #     if "owner_name" in df.columns:
    #         missing_owner = df["owner_name"].isna() | (df["owner_name"].astype(str).str.strip() == "")
    #         if missing_owner.any():
    #             issues.append("Missing owner name")
    #     return issues

    def validate(self, df: pd.DataFrame) -> pd.Series:
        issues = []

        for _, row in df.iterrows():
            row_issues = []

            if "parcel_id" in df.columns:
                if len(str(row.get("parcel_id", ""))) < 3:
                    row_issues.append("Invalid parcel ID")

            if "owner_name" in df.columns:
                if pd.isna(row.get("owner_name")) or str(row.get("owner_name")).strip() == "":
                    row_issues.append("Missing owner name")

            issues.append(", ".join(row_issues))

        return pd.Series(issues)