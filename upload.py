from lxml import html
import requests
import json
import argparse

def load_json_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    return json_data

parser = argparse.ArgumentParser(description="Download HTML content by hash.")
parser.add_argument("--hash", type=str, help="The hash string used in the URL.")
args = parser.parse_args()

hash_string = args.hash
# hash_string = "https://applynow.capitalone.com/?16260eddbb866e0859c13d220667b9df97807af9dab0382529fadd8d10a4ed52457f77c1dab697776e37f05874fc0717f5e8ada7a96b455fa2bd9cb2fa8d8317"
file_path = 'form.json'
selection_string = load_json_from_file(file_path)

r = requests.post('https://form-fill-mongodb.vercel.app/api/html/selection', json={
  "hash": hash_string,
  "selection": selection_string
})
print(f"Status Code: {r.status_code}")
# print(f"Status Code: {r.status_code}, Response: {r.json()}")

