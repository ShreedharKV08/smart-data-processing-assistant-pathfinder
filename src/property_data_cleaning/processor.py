"""Core processing pipeline for property data cleaning."""

import pandas as pd

from .duplicate_detection import DuplicateDetector
from .missing_value import MissingValuePredictor
from .normalization import AddressNormalizer, ParcelNormalizer, DataNormalizer
from .validators import RuleValidator


class PropertyDataCleaner:
    """Orchestrates ingestion, cleaning, normalization, and validation."""

    def __init__(self) -> None:
        self.duplicate_detector = DuplicateDetector()
        self.address_normalizer = AddressNormalizer()
        self.parcel_normalizer = ParcelNormalizer()
        self.data_normalizer = DataNormalizer()
        self.missing_value_predictor = MissingValuePredictor()
        self.rule_validator = RuleValidator()

    def ingest(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Load raw property data into a cleaned DataFrame."""
        return raw_data.copy()

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run the cleaning workflow on the raw DataFrame."""
        df = self.data_normalizer.normalize_column_names(df)
        df = self.data_normalizer.clean_text_data(df)
        df = self.data_normalizer.standardize_data_types(df)
        df = self.address_normalizer.normalize(df)
        df = self.parcel_normalizer.normalize(df)
        df = self.missing_value_predictor.predict(df)
        df = self.duplicate_detector.merge_duplicates(df)
        return df

    # def validate(self, df: pd.DataFrame) -> pd.DataFrame:
    #     """Validate cleaned data against business rules."""
    #     validation = self.rule_validator.validate(df)
    #     df = df.copy()
    #     df["validation_issues"] = validation
    #     return df
    
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run the complete cleaning pipeline."""
        df = self.ingest(df)
        df = self.clean(df)
        df = self.validate(df)
        return df

        return df

    def run(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Execute a full data cleaning and validation workflow."""
        df = self.ingest(raw_data)
        df = self.clean(df)
        df = self.validate(df)
        return df

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate cleaned data against business rules."""
        validation = self.rule_validator.validate(df)

        df = df.copy()

        # Convert list to string
        # issues_str = ", ".join(validation) if validation else ""
        df["validation_issues"] = validation

        # Assign same value to all rows
        # df["validation_issues"] = issues_str
        return df


def main() -> None:
    print("Property Data Cleaning system is ready.")
