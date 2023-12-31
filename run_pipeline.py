import subprocess
import argparse
import json

def run_command(command: str):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return process.communicate()[0].decode()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the entire pipeline.")
    parser.add_argument("--hash", type=str, help="The hash argument for download and upload")
    
    args = parser.parse_args()

    # Step 1: Run download.py
    print('---Download---')
    run_command(f"python3 lib/download.py --hash {args.hash}")

    # Step 2: Run parsing.py
    print('---Parsing---')
    run_command("python3 lib/parsing.py --html ./output.html --output output.json")

    # Step 3: Run matching.py
    print('---Matching---')
    run_command("python3 lib/matching.py --formfields output.json --output form.json")

    # Step 4: Run upload.py
    print('---Upload---')
    run_command(f"python3 lib/upload.py --hash {args.hash}")

    # Step 5: END
    print('---END---')

