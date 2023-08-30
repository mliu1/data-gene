import streamlit as st
import os
import json
import openai
import requests
from lib.download import fetch_html_content
from lib.parsing  import html_parsing
from lib.matching import matching
from lib.upload import upload_json

params = st.experimental_get_query_params()
if 'hash' in params:
    hash_string = params['hash'][0]
    print(hash_string)
    url = 'https://form-fill-mongodb.vercel.app/api/html/find?hash='
    html_content = fetch_html_content(url, hash_string)
    if (len(html_content) > 0):
        print(html_content)
        result = html_parsing(html_content)
        print(result)
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        form_name_to_pii_name = matching(result, openai_api_key)
        print(form_name_to_pii_name)
        json_string = json.dumps(form_name_to_pii_name)
        upload_json(hash_string, json_string)

