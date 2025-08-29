# streamlit_ui.py
import streamlit as st
import requests
import json

# --- Custom CSS for accent color and improved style ---
st.markdown('''
    <style>
    .main {background-color: #f7f8fa;}
    .stButton>button {background: linear-gradient(90deg, #7B68EE 60%, #8f94fb 100%); color: white; border-radius: 6px;}
    .stTextInput>div>div>input {border: 2px solid #7B68EE;}
    .stSelectbox>div>div {border: 2px solid #7B68EE;}
    .stTextArea textarea {border: 2px solid #7B68EE;}
    .stDataFrame {background: #fff; border-radius: 6px;}
    .block-container {padding-top: 2rem;}
    </style>
''', unsafe_allow_html=True)

st.markdown('<h1 style="color:#7B68EE;font-weight:700;">📄 OCR Data Extraction Portal</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#555;font-size:1.1rem;">Upload PDFs, extract structured data using OCR, and run powerful queries on your results.</p>', unsafe_allow_html=True)

# --- Upload Section ---
st.markdown('---')
st.markdown('#### <span style="color:#7B68EE;">1. Upload and Process PDF</span>', unsafe_allow_html=True)

with st.expander('How it works', expanded=False):
    st.info('Upload a PDF, select OCR engine and device, and process it. The extracted data will be stored in the backend database.')

col1, col2 = st.columns([2, 1])
with col1:
    uploaded_file = st.file_uploader('Upload a PDF document', type=['pdf'])
with col2:
    ocr_backend = st.selectbox('OCR Engine', ['easy', 'rapid', 'paddle'], help='Choose the OCR backend')
    accelerator_device = st.selectbox('Accelerator Device', ['CPU', 'CUDA'], help='Choose device for processing')

if uploaded_file and st.button('Process & Save to DB'):
    files = {'file': (uploaded_file.name, uploaded_file, 'application/pdf')}
    params = {'ocr_backend': ocr_backend, 'accelerator_device': accelerator_device}
    try:
        resp = requests.post(f'{st.secrets.get("API_URL", "https://ocr-json-docling-backend.onrender.com")}/upload', files=files, data=params)
        if resp.status_code == 200:
            st.success('✅ File processed and saved!')
            with st.expander('View OCR JSON Output'):
                st.json(resp.json())
        else:
            st.error(f'❌ Error: {resp.json().get("error") or resp.text}')
    except Exception as e:
        st.error(f'❌ Upload failed: {e}')

# --- Document List & Preview ---
st.markdown('---')
st.markdown('#### <span style="color:#7B68EE;">2. Explore Uploaded Documents</span>', unsafe_allow_html=True)

docs = []
try:
    docs = requests.get(f'{st.secrets.get("API_URL", "https://ocr-json-docling-backend.onrender.com")}/docs').json()
except Exception as e:
    st.error(f'Could not connect to backend: {e}')

if docs:
    doc_options = {doc['filename']: doc['id'] for doc in docs}
    selected_doc = st.selectbox('Select a document', list(doc_options.keys()))
    if selected_doc:
        doc_id = doc_options[selected_doc]
        doc_meta = next((d for d in docs if d['id']==doc_id), {})
        with st.expander('Show Metadata & Preview', expanded=False):
            st.write('**Filename:**', doc_meta.get('filename'))
            st.write('**ID:**', doc_meta.get('id'))
            st.write('**Upload Time:**', doc_meta.get('uploaded_at', 'N/A'))
            if st.button('Show JSON Preview'):
                doc_json = requests.get(f'{st.secrets.get("API_URL", "https://ocr-json-docling-backend.onrender.com")}/doc/{doc_id}').json()
                st.json(doc_json)
else:
    st.info('No documents uploaded yet.')

# --- Query Section ---
st.markdown('---')
st.markdown('#### <span style="color:#7B68EE;">3. Run SQL Query on OCR Data</span>', unsafe_allow_html=True)

st.markdown('''<small style="color:#888;">Example queries:<br>
- <code>SELECT * FROM docs;</code><br>
- <code>SELECT filename, json_extract(data, '$.metadata.page_count') as page_count FROM docs;</code><br>
- <code>SELECT filename FROM docs WHERE json_extract(data, '$.metadata.ocr_backend') = 'easy';</code>
</small>''', unsafe_allow_html=True)

default_sql = "SELECT filename, json_extract(data, '$.metadata.page_count') as page_count FROM docs;"
user_sql = st.text_area('Enter SQL query (use json_extract for JSON fields):', value=default_sql, height=100)

if st.button('Run Query'):
    if not user_sql.strip():
        st.warning('Please enter a SQL query.')
    else:
        resp = requests.post(f'{st.secrets.get("API_URL", "https://ocr-json-docling-backend.onrender.com")}/query', json={'sql': user_sql})
        if resp.status_code == 200:
            data = resp.json()
            st.write('Query Results:')
            st.dataframe(data)
        else:
            st.error(f'Error: {resp.json().get("error")}')

st.markdown('---')
