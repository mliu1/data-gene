import subprocess
import argparse
import json

def run_command(command: str):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return process.communicate()[0].decode()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the entire pipeline.")
    parser.add_argument("--hashes", type=str, help="The file has all the hashes for processing")
    
    args = parser.parse_args()
    file_name = args.hashes
    my_file = open(file_name, 'r')

    #read text file into list 
    hashes = my_file.read()

    # Step 0: START
    print('---START---')
    for hash_string in hashes:

        # Step 1: Run download.py
        print('---Download---' + hash_string)
        run_command(f"python3 download.py --hash {hash_string}")

        # Step 2: Run parsing.py
        print('---Parsing---')
        run_command("python3 parsing.py --html ./output.html --output output.pickle")

        # Step 3: Run matching.py
        print('---Matching---')
        run_command("python3 matching.py --formfields output.pickle --output form.json")

        # Step 4: Run upload.py
        print('---Upload---' + hash_string)
        run_command(f"python3 upload.py --hash {hash_string}")

    # Step 5: END
    print('---END---')

