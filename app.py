import streamlit as st
from pii_detector import detect_all_pii
from redaction_engine import redact_text

st.set_page_config(page_title="PII Redaction Tool", page_icon="🕵️", layout="wide")

st.title("PII Redaction Engine 🕵️")
st.markdown("A tool to securely detect and redact Personally Identifiable Information (PII) from text. Built with spaCy and regex for Indian financial documents.")

st.markdown("### Try it out")
st.markdown("Enter some text containing PII below, or use the default test snippet.")

default_text = """Contact Person: Sarthak Malvadkar.
Email: cs.connect@kshinternational.com.
Telephone: +91 22 40094400.

KSH International Limited is the company.
Kushal Subbayya Hegde is a promoter.
Here is an IP address: 192.168.1.1.
DOB: 12/05/1990"""

text_input = st.text_area("Input Text", value=default_text, height=200)

if st.button("Detect and Redact PII"):
    if text_input.strip():
        with st.spinner("Analyzing text for PII..."):
            pii_results = detect_all_pii(text_input)
            redacted_text = redact_text(text_input, pii_results)
            
        st.success("Redaction Complete!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Text")
            st.text(text_input)
            
        with col2:
            st.subheader("Redacted Text")
            st.text(redacted_text)
            
        st.subheader("Detected Entities")
        
        # Format the dict output to hide empty arrays for a cleaner UI
        clean_results = {k: v for k, v in pii_results.items() if v}
        if clean_results:
            st.json(clean_results)
        else:
            st.info("No PII detected in this text.")
    else:
        st.warning("Please enter some text to redact.")
