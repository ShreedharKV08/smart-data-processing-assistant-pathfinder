"""File handling utilities for various formats."""

import pandas as pd
import json
import io
from typing import Optional, Tuple
import PyPDF2
import re


class FileHandler:
    """Handles loading and exporting data in various formats."""

    @staticmethod
    def load_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
        """Load file based on extension and return DataFrame and detected type."""
        name = uploaded_file.name.lower()
        file_type = "unknown"

        try:
            if name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                file_type = "csv"
            elif name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(uploaded_file)
                file_type = "excel"
            elif name.endswith(".json"):
                df = pd.read_json(uploaded_file)
                file_type = "json"
            elif name.endswith(".txt"):
                content = uploaded_file.read().decode('utf-8')
                df = FileHandler._parse_text_file(content)
                file_type = "text"
            elif name.endswith(".pdf"):
                content = FileHandler._extract_pdf_text(uploaded_file)
                df = FileHandler._parse_text_file(content)
                file_type = "pdf"
            else:
                return None, "unsupported"

            return df, file_type

        except Exception as e:
            return None, f"error: {str(e)}"

    @staticmethod
    def _parse_text_file(content: str) -> pd.DataFrame:
        """Parse text content into DataFrame, trying different formats."""
        lines = content.strip().split('\n')

        # Try CSV-like format
        if ',' in lines[0]:
            return pd.read_csv(io.StringIO(content))

        # Try tab-separated
        if '\t' in lines[0]:
            return pd.read_csv(io.StringIO(content), sep='\t')

        # Try key-value pairs
        data = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                if key not in data:
                    data[key] = []
                data[key].append(value.strip())

        if data:
            max_len = max(len(v) for v in data.values())
            for key in data:
                while len(data[key]) < max_len:
                    data[key].append('')
            return pd.DataFrame(data)

        # Fallback: single column
        return pd.DataFrame({'content': lines})

    @staticmethod
    def _extract_pdf_text(uploaded_file) -> str:
        """Extract text from PDF file."""
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

    @staticmethod
    def export_data(df: pd.DataFrame, format_type: str) -> Tuple[bytes, str]:
        """Export DataFrame to specified format and return bytes and filename."""
        buffer = io.BytesIO()

        if format_type == "csv":
            df.to_csv(buffer, index=False)
            filename = "processed_data.csv"
        elif format_type == "excel":
            df.to_excel(buffer, index=False, engine='openpyxl')
            filename = "processed_data.xlsx"
        elif format_type == "json":
            df.to_json(buffer, orient='records', indent=2)
            filename = "processed_data.json"
        elif format_type == "txt":
            df.to_csv(buffer, index=False, sep='\t')
            filename = "processed_data.txt"
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        buffer.seek(0)
        return buffer.getvalue(), filename