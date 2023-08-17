import requests
import subprocess

def get_hashes():
    response = requests.get("https://form-fill-mongodb.vercel.app/api/html/hash")
    response.raise_for_status()  # Ensure the request was successful
    return response.json()  # Assuming the endpoint returns a JSON list of hashes

def run_pipeline_for_hash(hash_string):
    try:
        # 1. Run download.py with the hash
        subprocess.run(["python3", "download.py", "--hash", hash_string], check=True)

        # 2. Run parsing.py
        subprocess.run(["python3", "parsing.py", "--html", "./output.html", "--output", "output.pickle"], check=True)

        # 3. Run matching.py
        subprocess.run(["python3", "matching.py", "--formfields", "output.pickle", "--output", "form.json"], check=True)

        # 4. Run upload.py with the current hash
        subprocess.run(["python3", "upload.py", "--hash", hash_string], check=True)
        
        print(f"Pipeline successfully executed for hash: {hash_string}")

    except subprocess.CalledProcessError as e:
        print(f"Pipeline failed for hash {hash_string} with error: {str(e)}")

if __name__ == "__main__":
    hashes = get_hashes()
    for hash_string in hashes:
        run_pipeline_for_hash(hash_string)
