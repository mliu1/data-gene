import argparse
import requests

def is_html_tag_missing(html_content):
    """
    Check if the given HTML content is missing the <html> or </html> tags.
    
    Args:
    - html_content (str): The HTML content to check.
    
    Returns:
    - bool: True if either tag is missing, False otherwise.
    """
    # Convert content to lowercase to make the check case-insensitive
    html_content = html_content.lower()
    
    # Check for the presence of the tags
    missing_opening = "<html>" not in html_content
    missing_closing = "</html>" not in html_content
    
    return missing_opening or missing_closing

def add_html_tag_if_missing(html_snippet):
    if is_html_tag_missing(html_snippet):
        new_html = f'<html>{html_snippet}</html>'
        return new_html
    else:
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
        if (not data) or (not 'html' in data):
            print("Failed to retrieve html data. Status code:", response.status_code)
        else:
            content = data['html']
            html_content = add_html_tag_if_missing(content)
            print(html_content)
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
    return html_content

def fetch_pageDetails(url_base, hash_string):
    url = url_base + hash_string
    response = requests.get(url)
    fields = ""
    if response.status_code == 200:
        data = response.json()
        content = data['pageDetails']
        if len(content) > 0:
            fields = content['fields']:
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
    return fields

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download HTML content by hash.")
    parser.add_argument("--hash", type=str, help="The hash string used in the URL.")
    parser.add_argument("--output", type=str, default='output.html', help="The hash string used in the URL.")
    args = parser.parse_args()
    hash_string = args.hash
    file_path = args.output
    html_content = fetch_html_content('https://form-fill-mongodb.vercel.app/api/html/find?hash=', hash_string)
    if len(html_content) > 0:
        # File path where you want to save the HTML content
        # Save the HTML content to the file
        save_html_to_file(html_content, file_path)
    else:
        print("Failed to retrieve data.")


