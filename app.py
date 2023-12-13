import streamlit as st
import pdfplumber
import pytesseract
import io
import pandas as pd
from PIL import Image

# Function to parse page numbers
def parse_page_numbers(input_str):
    pages = set()
    for part in input_str.split(','):
        if '-' in part:
            a, b = part.split('-')
            pages.update(range(int(a), int(b) + 1))
        else:
            pages.add(int(part))
    return sorted(pages)

# Function to highlight text
def highlight_text(text, search_query):
    if search_query:
        highlighted = text.replace(search_query, f"**{search_query}**")
        return f'<span style="background-color:yellow;">{highlighted}</span>'
    return text

# Streamlit UI
st.title('PDF Extractor App')
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
page_input = st.text_input("Enter page numbers to extract (e.g., 1, 3-5):")
search_query = st.text_input("Enter text to search:")
data_type = st.selectbox("Select data to extract", ["Text", "Tables", "Images", "OCR Text"])

if uploaded_file is not None and page_input:
    # Parse the page numbers
    page_numbers = parse_page_numbers(page_input)

    # Process the PDF
    with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
        for page_num in page_numbers:
            if page_num <= len(pdf.pages):
                page = pdf.pages[page_num - 1]

                if data_type == "Text" or data_type == "OCR Text":
                    text = page.extract_text() if data_type == "Text" else pytesseract.image_to_string(page.to_image().original)
                    if text:
                        highlighted_text = highlight_text(text, search_query)
                        st.markdown(highlighted_text, unsafe_allow_html=True)
                    else:
                        st.write(f"No text found on Page {page_num}")

                elif data_type == "Tables":
                    tables = page.extract_tables()
                    for i, table in enumerate(tables):
                        df = pd.DataFrame(table[1:], columns=table[0])
                        st.write(f"Table {i + 1} on Page {page_num}")
                        st.dataframe(df)

                elif data_type == "Images":
                    st.write(f"Images on Page {page_num}")
                    images = page.images
                    for image in images:
                        image_bytes = page.extract_image(image)['image']
                        st.image(image_bytes, use_column_width=True)
