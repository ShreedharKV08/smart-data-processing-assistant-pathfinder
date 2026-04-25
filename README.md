# Smart Data Processing Assistant

A comprehensive data processing assistant that accepts various file formats (CSV, Excel, JSON, TXT, PDF) and provides automated cleaning, standardization, search, and export capabilities.

## Features

### Data Cleaning & Standardization
- **Automatic file type detection** and schema inference
- **Text cleaning**: Remove extra spaces, line breaks, special characters
- **Data normalization**: Consistent casing, column name standardization (snake_case)
- **Data type standardization**: Automatic detection of dates, numbers, strings
- **Missing value handling**: Intelligent filling of null/empty values
- **Duplicate detection and removal**
- **PDF text extraction**: Extract structured data from PDF documents

### Data Preview
- Clean tabular display of processed data
- Column information with data types and statistics
- First 20 rows preview

### Smart Search & Filtering
- **Exact matching** for IDs, account numbers, and key fields
- **AI-powered semantic search** using sentence transformers and FAISS
- Filter and return only relevant records

### Flexible Export Options
- **Multiple formats**: CSV, Excel (.xlsx), JSON, TXT
- **Filtered exports**: Export only search results
- **Proper formatting** and readability

### Email Delivery
- **Automated sending** of processed files via email
- **Clear subject and body** with processing summary
- **Attachment support** for all export formats

### Error Handling
- **File validation** with clear error messages
- **Search result handling** for no matches found
- **Robust processing** for various data formats

## Project Structure
- `src/property_data_cleaning/` - Core cleaning and validation modules
- `app.py` - Streamlit web interface
- `tests/` - Unit tests and validation

## Installation

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. For email functionality, configure environment variables:
   ```bash
   export EMAIL_USER=your_email@gmail.com
   export EMAIL_PASS=your_app_password
   ```

## Usage

### Web Interface
Run the Streamlit app:
```bash
streamlit run app.py
```

### Programmatic Usage
```python
from property_data_cleaning.processor import PropertyDataCleaner
from property_data_cleaning.file_handler import FileHandler

# Load and clean data
cleaner = PropertyDataCleaner()
file_handler = FileHandler()

df, file_type = file_handler.load_file(uploaded_file)
cleaned_df = cleaner.run(df)

# Export data
data_bytes, filename = file_handler.export_data(cleaned_df, 'csv')
```

## Supported File Formats

- **CSV**: Comma-separated values
- **Excel**: .xlsx and .xls files
- **JSON**: JSON objects and arrays
- **TXT**: Plain text with automatic parsing
- **PDF**: Text extraction from PDF documents

## Search Capabilities

- **Exact search**: Find records by ID, account number, or exact values
- **Semantic search**: AI-powered search for descriptions and natural language queries
- **Filtered results**: Return only matching records with full context

## Export Formats

- **CSV**: Standard comma-separated format
- **Excel**: Native .xlsx format with proper formatting
- **JSON**: Structured JSON with records array
- **TXT**: Tab-separated text format

## Email Configuration

For Gmail:
1. Enable 2-factor authentication
2. Generate an App Password
3. Set environment variables:
   ```bash
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_app_password
   ```

## Development

Run tests:
```bash
python -m pytest tests/
```

## License

This project is open source and available under the MIT License.
