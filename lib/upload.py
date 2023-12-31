import json
import argparse
import requests
from lib.utils import load_json_from_file


def upload_json(hash_string, json_string):
    r = requests.post('https://form-fill-mongodb.vercel.app/api/html/selection', json={
      "hash": hash_string,
      "selection": json_string
    })
    print(f"Status Code: {r.status_code}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download HTML content by hash.")
    parser.add_argument("--hash", type=str, help="The hash string used in the URL.")
    parser.add_argument("--input", type=str, help="The json file for upload.")
    args = parser.parse_args()
    file_path = args.input
    hash_string = args.hash
    # hash_string = "https://applynow.capitalone.com/?16260eddbb866e0859c13d220667b9df97807af9dab0382529fadd8d10a4ed52457f77c1dab697776e37f05874fc0717f5e8ada7a96b455fa2bd9cb2fa8d8317"
    selection_string = load_json_from_file(file_path)
    upload_json(hash_string, selection_string)
    # print(f"Status Code: {r.status_code}, Response: {r.json()}")

