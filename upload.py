from lxml import html
import requests
import json

def load_json_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    return json_data

hash_string = "https://secure05ea.chase.com/web/oao/application/card?8226a1d4232c94f307cafda8faa2f7dbb40402c341ad19d08c8444d15eb42b6f7a1aebedca809fd6de75d518d8490ccd598ef6bd42a15af1ab0f83f02202fae3"
file_path = 'form.json'
selection_string = load_json_from_file(file_path)

r = requests.post('https://form-fill-mongodb.vercel.app/api/html/selection', json={
  "hash": hash_string,
  "selection": selection_string
})
print(f"Status Code: {r.status_code}, Response: {r.json()}")

