"""Predict missing values in property datasets."""

import pandas as pd


class MissingValuePredictor:
    """Predicts or fills missing values for key property fields."""

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "tax_value" in df.columns:
            df["tax_value"] = df["tax_value"].fillna(0)
        return df
