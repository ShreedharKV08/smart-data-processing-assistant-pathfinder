import streamlit as st
import pandas as pd
import numpy as np
import re
import faiss
from sentence_transformers import SentenceTransformer
import io
import base64

from property_data_cleaning.processor import PropertyDataCleaner
from property_data_cleaning.file_handler import FileHandler
from property_data_cleaning.email_sender import EmailSender

# -----------------------------
# LOAD MODEL
# -----------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')

# -----------------------------
# INITIALIZE COMPONENTS
# -----------------------------
cleaner = PropertyDataCleaner()
file_handler = FileHandler()
email_sender = EmailSender()

# -----------------------------
# FILE LOAD + CLEAN
# -----------------------------
def load_and_clean_file(uploaded_file):
    """Load file, detect type, and clean data."""
    df, file_type = file_handler.load_file(uploaded_file)

    if df is None:
        if file_type.startswith("error"):
            st.error(f"Error loading file: {file_type[6:]}")
        else:
            st.error(f"Unsupported file type: {file_type}")
        return None, None

    st.success(f"✅ File loaded successfully! Detected type: {file_type.upper()}")

    # Clean the data using our pipeline
    try:
        df_cleaned = cleaner.run(df)
        st.success("✅ Data cleaned and standardized!")
        return df_cleaned, file_type
    except Exception as e:
        st.error(f"Error during cleaning: {e}")
        return df, file_type

# -----------------------------
# AUTO DETECT COLUMNS
# -----------------------------
def detect_columns(df):
    """Detect key columns for property data."""
    mapping = {}

    for col in df.columns:
        data = df[col].astype(str)

        if data.str.match(r'^R\d+', na=False).any():
            mapping["PropertyID"] = col

        elif data.str.match(r'^\d{6,}$', na=False).mean() > 0.5:
            mapping["AccountNumber"] = col

        elif data.str.match(r'^\d{5}$', na=False).any():
            mapping["ZipCode"] = col

        elif data.str.contains("TX|CA|NY", na=False).any():
            mapping["State"] = col

        elif data.str.contains("Loop|Street|Ave|Road", na=False).any():
            mapping["Address"] = col

        elif data.str.contains("Driftwood|Dallas|Austin", na=False).any():
            mapping["City"] = col

        elif data.str.contains("Andrew|John|Smith", na=False).any():
            mapping["Owner"] = col

    return mapping

# -----------------------------
# EXACT MATCH (RETURN ACCOUNT ONLY)
# -----------------------------
def dynamic_exact_match(df, query):
    """Find exact matches for property IDs or account numbers."""
    query = str(query).strip().upper()

    match = re.findall(r'[A-Za-z]*\d+', query)
    if not match:
        return "⚠️ Invalid input - please enter a valid ID or account number"

    value = match[0]

    col_map = detect_columns(df)

    prop_col = col_map.get("PropertyID")
    acct_col = col_map.get("AccountNumber")

    if not prop_col and not acct_col:
        return "❌ No PropertyID or AccountNumber columns detected"

    # Try PropertyID first
    if prop_col:
        df[prop_col] = df[prop_col].astype(str).str.upper()
        result = df[df[prop_col] == value]
        if not result.empty:
            return result

    # Try AccountNumber
    if acct_col:
        df[acct_col] = df[acct_col].astype(str).str.upper()
        result = df[df[acct_col] == value]
        if not result.empty:
            return result

    return None  # No exact match found

# -----------------------------
# RAG TEXT FORMAT (CLEAN)
# -----------------------------
def df_to_text(df):
    """Convert DataFrame to text format for RAG."""
    texts = []
    col_map = detect_columns(df)

    for _, row in df.iterrows():
        formatted = []

        for key, col in col_map.items():
            val = row[col]
            if pd.notna(val) and str(val).strip() != "":
                formatted.append(f"{key}: {val}")

        texts.append("\n".join(formatted))

    return texts

# -----------------------------
# VECTOR STORE
# -----------------------------
def create_vector_store(texts):
    """Create FAISS vector store for semantic search."""
    embeddings = model.encode(texts)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    return index

def semantic_search(query, index, texts, k=5):
    """Perform semantic search using RAG."""
    query_vec = model.encode([query])

    D, I = index.search(np.array(query_vec), k)

    return [texts[i] for i in I[0]]

# -----------------------------
# CONVERT RAG → TABLE
# -----------------------------
def rag_to_dataframe(results):
    """Convert RAG results back to DataFrame."""
    rows = []

    for r in results:
        row = {}
        for line in r.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                row[k.strip()] = v.strip()
        rows.append(row)

    return pd.DataFrame(rows)

# -----------------------------
# EXPORT FUNCTIONALITY
# -----------------------------
def create_download_link(data_bytes, filename):
    """Create a download link for the exported data."""
    b64 = base64.b64encode(data_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
    return href

# -----------------------------
# EMAIL FUNCTIONALITY
# -----------------------------
def send_email_with_attachment(email, data_bytes, filename):
    """Send email with processed data attachment."""
    subject = "Processed Data File"
    body = f"""Hello,

Please find attached your processed data file: {filename}

This file has been cleaned and standardized according to your requirements.

Best regards,
Data Processing Assistant
"""

    success = email_sender.send_email(
        to_email=email,
        subject=subject,
        body=body,
        attachment_data=data_bytes,
        attachment_filename=filename
    )

    return success

# -----------------------------
# STREAMLIT UI
# -----------------------------
def main():
    st.set_page_config(layout="wide", page_title="Data Processing Assistant")
    st.title("🤖 Smart Data Processing Assistant")
    st.markdown("Upload any file (CSV, Excel, JSON, TXT, PDF) and get clean, searchable data with export options!")

    # File upload
    uploaded_file = st.file_uploader("📁 Upload your data file", type=['csv', 'xlsx', 'xls', 'json', 'txt', 'pdf'])

    if uploaded_file:
        df, file_type = load_and_clean_file(uploaded_file)

        if df is not None:
            # Store in session state
            st.session_state["df"] = df
            st.session_state["file_type"] = file_type

            # Data Preview
            st.write("### 📊 Cleaned Data Preview")
            st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")

            # Column info
            st.write("**Column Information:**")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Data Type': df.dtypes.astype(str),
                'Non-Null Count': df.notna().sum(),
                'Null Count': df.isna().sum()
            })
            st.dataframe(col_info, use_container_width=True)

            # Data preview
            st.write("**Data Preview (first 20 rows):**")
            st.dataframe(df.head(20), use_container_width=True)

            # Build RAG index for search
            with st.spinner("Building search index..."):
                texts = df_to_text(df)
                index = create_vector_store(texts)
                st.session_state["index"] = index
                st.session_state["texts"] = texts

            st.success("✅ Data ready for search and export!")

            # Export Options
            st.write("### 📤 Export Options")
            col1, col2 = st.columns(2)

            with col1:
                export_format = st.selectbox(
                    "Choose export format:",
                    ["csv", "excel", "json", "txt"],
                    help="Select the format for your processed data"
                )

            with col2:
                if st.button("🚀 Generate Export File"):
                    try:
                        data_bytes, filename = file_handler.export_data(df, export_format)
                        st.session_state["export_data"] = data_bytes
                        st.session_state["export_filename"] = filename
                        st.success(f"✅ Export file generated: {filename}")

                        # Show download link
                        st.markdown(create_download_link(data_bytes, filename), unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Export failed: {e}")

            # Email option
            st.write("### 📧 Email Delivery (Optional)")
            email = st.text_input("Enter your email address (optional):", placeholder="user@example.com")

            if email and "export_data" in st.session_state:
                if st.button("📧 Send via Email"):
                    with st.spinner("Sending email..."):
                        success = send_email_with_attachment(
                            email,
                            st.session_state["export_data"],
                            st.session_state["export_filename"]
                        )
                        if success:
                            st.success("✅ Email sent successfully!")
                        else:
                            st.error("❌ Failed to send email. Please check your email configuration.")

    # Search functionality
    if "df" in st.session_state:
        st.write("---")
        st.write("### 🔍 Search & Filter")

        query = st.text_input(
            "🔍 Search by ID, Account Number, or describe what you're looking for:",
            placeholder="e.g., R12345, 123456789, or 'properties in Dallas'"
        )

        if query:
            df = st.session_state["df"]

            # Exact match first
            result = dynamic_exact_match(df, query)

            if isinstance(result, str):
                st.warning(result)
            elif result is not None:
                st.success("✅ Exact match found!")
                st.write(f"**Found {len(result)} matching record(s):**")
                st.dataframe(result, use_container_width=True)

                # Export filtered results
                if st.button("📤 Export Filtered Results"):
                    try:
                        data_bytes, filename = file_handler.export_data(result, "csv")
                        st.markdown(create_download_link(data_bytes, f"filtered_{filename}"), unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Export failed: {e}")

            else:
                # Fallback to semantic search
                st.info("🔍 No exact match found. Using AI-powered search...")

                results = semantic_search(
                    query,
                    st.session_state["index"],
                    st.session_state["texts"]
                )

                df_result = rag_to_dataframe(results)

                st.write("### 🎯 Top Matches")
                st.dataframe(df_result, use_container_width=True)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    main()