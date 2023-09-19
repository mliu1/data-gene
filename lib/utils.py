from lxml import html
import json
import pickle
import requests


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


