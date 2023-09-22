import streamlit as st
import os
import json
import openai
import pickle
import requests
from lib.upload import upload_json
from lib.download import fetch_html_content,fetch_hashes
from lib.utils import get_new_hashes, get_all_hashes
from lib.matching import cosine_similarity_matrix,load_html_files_from_directory,get_embedding,get_inverted_index,get_all_inputs,get_label_for_inputs
import time

params = st.experimental_get_query_params()
if 'update' in params:
    url = 'https://form-fill-mongodb.vercel.app/api/html/hash'
    hashes = get_new_hashes()
    label_dict = {}
    with open(label_file, "rb") as f:
        label_dict = pickle.load(f)
    for hash_string in hashes:
        html_content = fetch_html_content(url, hash_string)
        if (len(html_content) > 0):
            html_content = fetch_html_content(url_base, hash_string)
            soup, inputs = get_all_inputs(html_content)
            data = get_label_for_inputs(inputs, soup, label_dict)
            json_string = json.dumps(data)
            print(json_string)
            upload_json(hash_string, json_string)

if 'batch' in params:
    url_base = 'https://form-fill-mongodb.vercel.app/api/html/find?hash='
    hashes = get_all_hashes()
    label_dict = {}
    with open(label_file, "rb") as f:
        label_dict = pickle.load(f)
    for hash_string in hashes:
        html_content = fetch_html_content(url, hash_string)
        if (len(html_content) > 0):
            html_content = fetch_html_content(url_base, hash_string)
            soup, inputs = get_all_inputs(html_content)
            data = get_label_for_inputs(inputs, soup, label_dict)
            json_string = json.dumps(data)
            print(json_string)
            upload_json(hash_string, json_string)

if 'hash' in params:
    hash_string = params['hash'][0]
    print(hash_string)
    url_base = 'https://form-fill-mongodb.vercel.app/api/html/find?hash='
    html_content = fetch_html_content(url_base, hash_string)
    if (len(html_content) > 0):
        with open("label.pkl", "rb") as f:
            label_dict = pickle.load(f)
            html_content = fetch_html_content(url_base, hash_string)
            soup, inputs = get_all_inputs(html_content)
            data = get_label_for_inputs(inputs, soup, label_dict)
            json_string = json.dumps(data)
            print(json_string)
            upload_json(hash_string, json_string)

