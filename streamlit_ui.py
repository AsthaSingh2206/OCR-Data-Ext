# streamlit_ui.py
import streamlit as st
import requests
import json

API_URL = st.text_input('Enter your Flask API URL', 'http://127.0.0.1:5000')

st.title('OCR JSON Query Platform')

# Upload PDF and process with OCR
st.markdown('---')
st.header('Upload and Process PDF')

uploaded_file = st.file_uploader('Upload a PDF document', type=['pdf'])
ocr_backends = ['easy', 'rapid', 'paddle']
ocr_backend = st.selectbox('Select OCR Engine', ocr_backends)
accelerator_devices = ['CPU', 'CUDA']
accelerator_device = st.selectbox('Select Accelerator Device', accelerator_devices)

if uploaded_file and st.button('Process and Save to DB'):
    files = {'file': (uploaded_file.name, uploaded_file, 'application/pdf')}
    params = {'ocr_backend': ocr_backend, 'accelerator_device': accelerator_device}
    try:
        resp = requests.post(f'{API_URL}/upload', files=files, data=params)
        if resp.status_code == 200:
            st.success('File processed and saved to database!')
            st.json(resp.json())
        else:
            st.error(f'Error: {resp.json().get("error") or resp.text}')
    except Exception as e:
        st.error(f'Upload failed: {e}')

st.markdown('---')
st.header('Query OCR Results')

# List docs
try:
    docs = requests.get(f'{API_URL}/docs').json()
except Exception as e:
    st.error(f'Could not connect to backend: {e}')
    docs = []

doc_options = {doc['filename']: doc['id'] for doc in docs}
selected_doc = st.selectbox('Select a document', list(doc_options.keys())) if docs else None

if selected_doc:
    doc_id = doc_options[selected_doc]
    st.write(f'Selected document: {selected_doc}')
    # Show JSON preview
    if st.button('Show JSON Preview'):
        doc_json = requests.get(f'{API_URL}/doc/{doc_id}').json()
        st.json(doc_json)

st.markdown('---')
st.header('Run SQL-like Query on JSON')
default_sql = "SELECT filename, json_extract(data, '$.metadata.page_count') as page_count FROM docs;"
user_sql = st.text_area('Enter SQL query (use json_extract for JSON fields):', value=default_sql, height=100)

if st.button('Run Query'):
    if not user_sql.strip():
        st.warning('Please enter a SQL query.')
    else:
        resp = requests.post(f'{API_URL}/query', json={'sql': user_sql})
        if resp.status_code == 200:
            data = resp.json()
            st.write('Query Results:')
            st.dataframe(data)
        else:
            st.error(f'Error: {resp.json().get("error")}')

st.markdown('---')
