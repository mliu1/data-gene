from lxml import html
import argparse
import requests

def add_html_tag_if_missing(html_snippet):
    try:
        # Parse the HTML snippet with lxml
        tree = html.fromstring(html_snippet)

        # Check if the root element is <html>
        if tree.tag == 'html':
            return html_snippet  # Return the original HTML snippet if it already has an <html> tag

        # Add an <html> tag to the beginning of the HTML snippet
        new_html = f'<html>{html_snippet}</html>'
        return new_html
    except Exception as e:
        # Handle parsing errors
        return html_snippet

def save_html_to_file(html_content, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

def fetch_hashes(url):
    response = requests.get(url)
    content = ""
    if response.status_code == 200:
        data = response.json()
        content = data
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
    return content
    
def fetch_html_content(url_base, hash_string):
    url = url_base + hash_string
    response = requests.get(url)
    html_content = ""
    if response.status_code == 200:
        data = response.json()
        content = data['html']
        html_content = add_html_tag_if_missing(content)
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
    return html_content

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download HTML content by hash.")
    parser.add_argument("--hash", type=str, help="The hash string used in the URL.")
    args = parser.parse_args()
    hash_string = args.hash
    html_content = fetch_html_content('https://form-fill-mongodb.vercel.app/api/html/find?hash=', hash_string)
    if len(html_content) > 0:
        # File path where you want to save the HTML content
        file_path = 'output.html'
        # Save the HTML content to the file
        save_html_to_file(html_content, file_path)
    else:
        print("Failed to retrieve data.")


