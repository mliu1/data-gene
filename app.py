import streamlit as st
import requests
from lib.download import fetch_html_content

params = st.experimental_get_query_params()
hash_string = params['hash']

url = 'https://form-fill-mongodb.vercel.app/api/html/find?hash='
html_content = fetch_html_content(url, hash_string)
if (len(html_content) > 0):
    print(html_content)
