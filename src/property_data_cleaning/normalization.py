"""Address and parcel normalization utilities."""

import pandas as pd
import re


class AddressNormalizer:
    """Standardizes address fields for downstream processing."""

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "address" in df.columns:
            df["address"] = df["address"].astype(str).str.strip().str.title()
        return df


class ParcelNormalizer:
    """Normalizes parcel IDs and related identifiers."""

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "parcel_id" in df.columns:
            df["parcel_id"] = df["parcel_id"].astype(str).str.replace(r"[^0-9A-Za-z]", "", regex=True).str.upper()
        return df


class DataNormalizer:
    """General data normalization utilities."""

    @staticmethod
    def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Convert column names to snake_case."""
        df = df.copy()
        df.columns = [re.sub(r'[^0-9a-zA-Z]+', '_', col.lower()).strip('_') for col in df.columns]
        return df

    @staticmethod
    def clean_text_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean text data: remove extra spaces, special chars, normalize casing."""
        df = df.copy()
        for col in df.select_dtypes(include=['object']).columns:
            # Convert to string but preserve None/NaN
            df[col] = df[col].astype(str).where(df[col].notna(), pd.NA)
            # Only clean non-null values
            mask = df[col].notna()
            df.loc[mask, col] = df.loc[mask, col].str.strip()
            df.loc[mask, col] = df.loc[mask, col].str.replace(r'\s+', ' ', regex=True)  # Multiple spaces to single
            df.loc[mask, col] = df.loc[mask, col].str.replace(r'[^\w\s-]', '', regex=True)  # Remove special chars except - and space
        return df

    @staticmethod
    def standardize_data_types(df: pd.DataFrame) -> pd.DataFrame:
        """Ensure consistent data types."""
        df = df.copy()

        # Convert None/null values to proper NaN
        df = df.replace({None: pd.NA})

        # Try to convert obvious numeric columns
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column name suggests it should be numeric
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in ['id', 'number', 'count', 'value', 'amount', 'price', 'tax', 'zip', 'code']):
                    # Try numeric conversion
                    try:
                        numeric_series = pd.to_numeric(df[col], errors='coerce')
                        # Only convert if at least 50% of values are numeric
                        if numeric_series.notna().mean() > 0.5:
                            df[col] = numeric_series
                    except:
                        pass
                # Try date conversion for date-like columns
                elif any(keyword in col_lower for keyword in ['date', 'time']):
                    try:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                    except:
                        pass

        return df
