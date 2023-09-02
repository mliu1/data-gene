import streamlit as st
import os
import json
import openai
import requests
from lib.download import fetch_html_content,fetch_hashes
from lib.parsing  import html_parsing
from lib.matching import matching
from lib.upload import upload_json

#params = st.experimental_get_query_params()
#if 'batch' in params:
url = 'https://form-fill-mongodb.vercel.app/api/html/hash'
url_base = 'https://form-fill-mongodb.vercel.app/api/html/find?hash='
#black_list = set(["applynow.capitalone.com/?db8665cfffd6a5600126fbf0e3f6d0cd608f6e59dabf8309cb9cb3c8dbedb1568d1a26ee322f8a436c47118457a8c7d96e6e0bb1bf35ba3f463969800125b490",
#                  "docs.google.com/spreadsheets/d/10-_D16zy7ZyxfivszyrOc1SH1qSEZOwzd50aPq1rNRA/edit?e2915be954010f257a77460e7e9c2d88259fe14049fe708b3a9fe5de9d4fc4df6f125526975abf1889b7317de76af79f4fc52a42c89e7329aec01770ff8a3e07",
#                  "flowbite.com/docs/forms/select/?3b155c495104daf2122818969b1fcf4f3360a619b480046391ae03925789c9e179d65d72c578c2884ca5992023f58df1a5d8e45057d8563e9dc1a797b31de7d1"])
hashes = fetch_hashes(url)
for hash_string in hashes:
    print('hash::')
    print(hash_string)
    #if hash_string in black_list:
    #    continue
    html_content = fetch_html_content(url_base, hash_string)
    result = html_parsing(html_content)
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    form_name_to_pii_name = matching(result, openai_api_key)
    #print(form_name_to_pii_name)
    json_string = json.dumps(form_name_to_pii_name)
    upload_json(hash_string, json_string)
# elif 'hash' in params:
#     hash_string = params['hash'][0]
#     print(hash_string)
#     url = 'https://form-fill-mongodb.vercel.app/api/html/find?hash='
#     html_content = fetch_html_content(url, hash_string)
#     if (len(html_content) > 0):
#         print(html_content)
#         result = html_parsing(html_content)
#         print(result)
#         openai_api_key = os.environ.get('OPENAI_API_KEY')
#         form_name_to_pii_name = matching(result, openai_api_key)
#         print(form_name_to_pii_name)
#         json_string = json.dumps(form_name_to_pii_name)
#         upload_json(hash_string, json_string)

