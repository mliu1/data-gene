from lxml import html
import json
import pickle
import requests

def get_new_hashes():
    response = requests.get("https://form-fill-mongodb.vercel.app/api/html/hash")
    response.raise_for_status()  # Ensure the request was successful
    return response.json()  # Assuming the endpoint returns a JSON list of hashes

def get_all_hashes():
    response = requests.get("https://form-fill-mongodb.vercel.app/api/html?hash=11")
    response.raise_for_status()  # Ensure the request was successful
    return response.json()  # Assuming the endpoint returns a JSON list of hashes

def string_to_8char_hex(input_string):
    # Hash the input string using SHA-256
    sha256 = hashlib.sha256()
    sha256.update(input_string.encode())
    hex_string = sha256.hexdigest()
    
    # Return the first 8 characters of the hex string
    return hex_string[:8]

def load_json_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    return json_data

def serialize_dictionary(dictionary, file_path):
    pickle.dump(dictionary, open(file_path,'wb'))
    #with open(file_path, 'w') as file:
    #    json.dump(dictionary, file)

def deserialize_dictionary(file_path):
    dictionary = pickle.load(open(file_path,'rb'))
    #with open(file_path, 'r') as file:
    #    dictionary = json.load(file)
    return dictionary


