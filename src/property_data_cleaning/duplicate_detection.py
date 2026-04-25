"""Duplicate detection and merge logic."""

import pandas as pd
from typing import List


class DuplicateDetector:
    """Detects and merges duplicate property records."""

    def find_duplicates(self, df: pd.DataFrame) -> List[List[int]]:
        """Return groups of duplicate row indexes."""
        return []

    def merge_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Merge detected duplicates into a single canonical record."""
        return df.copy()
    
    def find_duplicates(self, df):
        if "parcel_id" in df.columns:
            return df[df.duplicated(subset=["parcel_id"], keep=False)].index.tolist()
        return []

    def merge_duplicates(self, df):
        if "parcel_id" in df.columns:
            return df.drop_duplicates(subset=["parcel_id"], keep="first")
        return df
