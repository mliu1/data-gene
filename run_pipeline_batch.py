import json
import time
import hashlib
import argparse
import requests
import subprocess
from lib.utils import load_json_from_file

def get_hashes():
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

def run_command(command: str):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return process.communicate()[0].decode()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Parsing html page to extract form fields.")
    parser.add_argument("--mode", type=str, default = 'matching', help="The input folder.")

    args = parser.parse_args()
    mode = args.mode

    if mode == "download":
        hashes = get_hashes()
        for hash_string in hashes:
            # 1. Run download.py with the hash
            subprocess.run(["python3", "lib/download.py", "--hash", hash_string, "--output", "ouput_"+string_to_8char_hex(hash_string)+".html"], check=True)

    if mode == "upload":
        hashes = get_hashes()
        for hash_string in hashes:
            # 4. Run upload.py with the current hash
            subprocess.run(["python3.11", "lib/upload.py", "--hash", hash_string, "--input", "template/ouput_"+string_to_8char_hex(hash_string)+".json"], check=True)  
            time.sleep(2)
            
    if mode == "matching":
        try:
            # 1. Scan all html generate unique tokens
            subprocess.run(["python3.11", "run.py", "--mode", "indexing", "--input", "data/", "--output", "inverted_index.pkl"], check=True)

            # 2. Filter html tokens and generate token embedding vectors
            subprocess.run(["python3.11", "run.py", "--mode", "parsing", "--input",  "inverted_index.pkl", "--output", "embedding.pkl"], check=True)

            # 3. Process knowledge data to generate label embedding vectors
            subprocess.run(["python3.11", "run.py", "--mode", "processdata", "--output", "data.pkl"], check=True)

            # 4. Generate label for all input tokens from htmls
            subprocess.run(["python3.11", "run.py", "--mode", "labeling", "--input",  "embedding.pkl", "--output", "label.pkl"], check=True)
        
            # 5. Process htmls and generate the form templates
            subprocess.run(["python3.11", "run.py", "--mode", "matching", "--input",  "data/", "--label", "label.pkl", "--output", "template/"], check=True)
        
            print(f"Pipeline successfully executed for debug/")

        except subprocess.CalledProcessError as e:
            print(f"Pipeline failed for hash with error: {str(e)}")

    
