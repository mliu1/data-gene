import os
import re
import time
import json
import nltk
import pickle
import openai
import argparse
import numpy as np
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
    
data = {
    "firstName": ["first name", "legal first name", "firstName"],
    "middleName": ["Middle Name", "Middle Initial", "middle initial (optional)", "middleName"],
    "lastName": ["Last Name", "Legal Last Name", "lastName"],
    "suffix": ["Suffix", "suffix (optional)"],
    "suffixValue": ["jr", "sr", "ii", "iii", "iv"],
    "taxIDType": ["Tax ID Type"],
    "itin": ["Individual Taxpayer Identification Number", "individual tax id", "itin"],
    "ssn": ["Social Security Number", "Social Security", "ssn", "ssn or individual tax id", "social security number or individual taxpayer identification"],
    "ssnFormat": ["xxx-xx-xxxx"],
    "dob": ["Date of Birth", "dateOfBirth" "dob", "date of birth (mm/dd/yyyy)"],
    "dateFormat": ["mm/dd/yyyy"],
    "mother MaidenName": ["Mother Maiden Name", "mother's maiden name"],
    "addressType": ["Address Type"],
    "mailingAddressLine1": ["Mailing Address","Residence Address", "street address", "residential address", "Residential Address (P.O. Box is not valid)", "mailing address", "billing address"],
    "mailingAddressLine2": ["Apt/suite number", "Apt no", "suite no", "apt/suite (if applicable)", "suite/apt/other", "address line 2 (optional)"],
    "zip/postalCode": ["zipcode", "zip code", "zip", "postal Code", "postalCode"],
    "state/province/region": ["state", "province"],
    "interest rates": ["interest rates", "apr", "prime rate"],
    "us_state_name": [ "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",\
                        "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",\
                        "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "ohio",\
                        "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",\
                        "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",\
                        "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",\
                        "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",\
                        "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming", \
                        "puerto rico", "district of columbia", "guam","virgin islands"],
    "country_name": ["Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda",\
                    "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain",\
                    "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan",\
                    "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria",\
                    "Burkina Faso", "Burundi", "Côte d'Ivoire", "Cabo Verde", "Cambodia", "Cameroon",\
                    "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros",\
                    "Congo (Congo-Brazzaville)", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czechia",\
                    "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic",\
                    "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini",\
                    "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany",\
                    "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana",\
                    "Haiti", "Holy See", "Honduras", "Hungary", "Iceland", "India", "Indonesia",\
                    "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan",\
                    "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan", "Laos", "Latvia",\
                    "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",\
                    "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",\
                    "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia",\
                    "Montenegro", "Morocco", "Mozambique", "Myanmar (formerly Burma)", "Namibia", "Nauru",\
                    "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea",\
                    "North Macedonia (formerly Macedonia)", "Norway", "Oman", "Pakistan", "Palau", "Palestine State",\
                    "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal",\
                    "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia",\
                    "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia",\
                    "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia",\
                    "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain",\
                    "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Tajikistan",\
                    "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago",\
                    "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates",\
                    "United Kingdom", "United States of America", "Uruguay", "Uzbekistan", "Vanuatu",\
                    "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"],
    "city": ["City"],
    "country": ["Country"],
    "primaryPhoneType": ["Primary Phone Type", "phone type", "phonetype"],
    "primaryPhoneNumber": ["Primary Phone Number", "mobile number", "phone number", "mobile phone number", "Primary Phone Number & Type"] ,
    "email": ["Email Address", "email"],
    "employmentStatus": ["Employment Status"],
    "employmentStatusValue": ["unemployed", "self-employed", "employed"],
    "income-annual-usd":["Income(annual)", "total gross annual income", "total annual income"],
    "housingStatus":["Type of residence", "Housing Status"],
    "housingStatusValue":["own", "rent"],
    "monthlyRent/Mortgage": ["Monthly Rent/Mortgage", "monthly housing payment"],
    "educationDegree":  ["Education Degree", "the highest level of education"],
    "workingIndustry":  ["Working Industry"],
    "professionalTitle":["Professional Title"],
    "professionalTenure": ["Professional Tenure"],
    "linkedinProfile": ["Linkedin Profile"],
    "personalWebsite": ["Personal Website", "personal info", "personal information"],
    "visaSponsorship": ["Visa Sponsorship"],
    #"yes/no": ["Yes", "No"],
    "terms & conditions": ["terms & conditions", "terms", "terms of service"],
    "annual membership fee": ["annual membership fee"],
    "authorized user": ["authorized user"],
    "monthly fee": ["monthly fee"],
    "annual fee": ["annual fee"],
    "transaction fees": ["transaction fees"],
    "penalty fees": ["penalty fees"],
    "password": ["password"],
    "username": ["username"],
    "contact information": ["contact information", "personal information"],
    "residency status": ["US citizen", "Green card (Permanent Resident)", "Foreign (Non-resident)"],
}

def cosine_similarity_matrix(embeddings1, embeddings2):
    # Normalize the embeddings
    embeddings1_normalized = embeddings1 / np.linalg.norm(embeddings1, axis=1, keepdims=True)
    embeddings2_normalized = embeddings2 / np.linalg.norm(embeddings2, axis=1, keepdims=True)
    
    # Compute the similarity matrix
    similarity = np.dot(embeddings1_normalized, embeddings2_normalized.T)
    
    return similarity

def load_html_files_from_directory(directory_path):
    # List all files in the directory
    all_files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    
    # Filter for .html files
    html_files = [f for f in all_files if f.endswith('.html')]
    
    # Load each HTML file into memory
    html_contents = {}
    for html_file in html_files:
        with open(os.path.join(directory_path, html_file), 'r', encoding='utf-8') as file:
            html_contents[html_file] = file.read()
    
    return html_contents

def nltk_tokenize(input_string):
    tokens_nltk = word_tokenize(input_string.lower())
    tokens_nltk = [token for token in tokens_nltk if not no_alphanumeric_string(token)]
    return ' '.join(tokens_nltk)

def no_alphanumeric_string(s):
    return bool(re.match(r'^[^\w]', s))

def remove_trailing_non_alnum_regex(s):
    return re.sub(r'[^a-zA-Z0-9]*$', '', s)

def generate_xpath(element):
    path_parts = []
    current = element
    while current is not None and current.name is not None and current.parent is not None:
        siblings = list(current.parent.children)
        tag_siblings = [sibling for sibling in siblings if sibling.name == current.name]
        if len(tag_siblings) > 1:
            index = tag_siblings.index(current) + 1  # XPath is 1-indexed
            path_parts.append(f"{current.name}[{index}]")
        else:
            path_parts.append(current.name)
        current = current.parent
    return '/' + '/'.join(reversed(path_parts))

def get_inverted_index(html_data):
    inverted = dict()
    for filename, content in html_data.items():
        print(f"Contents of {filename}:")
        #print(content)
        page = BeautifulSoup(content, 'html.parser')
        vocab = set()
        # Extracting text strings for all elements in the soup
        for s in page.stripped_strings:
            vocab.add(s.lower())
        
        # Extracting the 'name' attributes for all elements in the soup
        element_name_attributes = [tag['name'] for tag in page.find_all() if tag.has_attr('name')]
        for s in element_name_attributes:
            vocab.add(s.lower())

        #print(vocab)
        for v in vocab:
            if v not in inverted:
                inverted[v] = [filename]
            else:
                inverted[v].append(filename)
    return inverted

def scan_for_inputs(html_data, label_dict, output_folder):
    for filename, content in html_data.items():
        print(f"Contents of {filename}:")
        #print(content)
        soup, inputs = get_all_inputs(content)
        data = get_label_for_inputs(inputs, soup, label_dict)
        json_output = output_folder + '/' + filename[:-5] + ".json"
        with open(json_output, 'w') as json_file:
            json.dump(data, json_file)


def get_all_inputs(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    inputs  = soup.find_all('input')
    selects = soup.find_all('select')
    textareas = soup.find_all('textarea')
    radios = soup.find_all(attrs={'role': 'radio'})
    checkboxes = soup.find_all(attrs={'role': 'checkbox'})
    submit_buttons = soup.find_all(attrs={'role': 'submit'})
    radiogroups = soup.find_all(attrs={'role': 'radiogroup'})
    input_elements = inputs + selects + textareas + radiogroups + radios + checkboxes + submit_buttons
    return soup, input_elements

def get_label_for_inputs(non_hidden_inputs, soup, label_dict):
    
    data = []
    for input_elem in non_hidden_inputs:
        
        elem_id = ""
        elem_type = ""
        label_text = ""
        label_conf = 0.0

        #if we can find a good match using name, skip
        foundLabel = False
        if input_elem.get('name'):
            s =  input_elem.get('name').lower()
            s = nltk_tokenize(s)
            if s in label_dict:
                label_text = label_dict[s][0] #label category
                label_conf = label_dict[s][1] #confidence score
                foundLabel = True
            #print(f"name is {s}, found label {foundLabel}")
            
        if not foundLabel:
            # Find associated label using 'for' attribute
            associated_label = soup.find('label', {'for': input_elem.get('id')})
            
            # If input is a child of label, the parent is the associated label
            if not associated_label and input_elem.find_parent('label'):
                associated_label = input_elem.find_parent('label')
            
            if associated_label:
                #print(associated_label)
                
                for s in associated_label.stripped_strings:
                    token = nltk_tokenize(s)
                    #print(f'normalized to {token}')
                    if token in label_dict:
                        print(f'{token} is matched to {label_dict[token]}')
                        label_text = label_dict[token][0] #label category
                        label_conf = round(label_dict[token][1], 2)#confidence score
                        foundLabel = True
                        break
                    #print(f"label is {s}, found label {foundLabel}")
    
        #print(f'label is {label_text}') 
        #if 'id' in input_elem:
        if input_elem.get('id'):
            elem_id = input_elem.get('id')
        
        if input_elem.get('type'):
            elem_type = input_elem.get('type')

        xpath = generate_xpath(input_elem)
        data_item = (elem_id, xpath, label_text, label_conf, elem_type)
        data.append(data_item)

    return data

def chunk_list(input_list, chunk_size):
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]

def get_embedding(input_tokens):
    print(input_tokens)
    token_embedding = dict()
    sub_tokens_list = chunk_list(input_tokens, 20)
    for sub_tokens in sub_tokens_list:
        print(sub_tokens)
        resp = openai.Embedding.create(
                input=sub_tokens,
                engine="text-embedding-ada-002")
        for i in range(len(sub_tokens)):
            token_embedding[sub_tokens[i]] = resp['data'][i]['embedding']
        print(sub_tokens)
    return token_embedding


def process_htmls_for_inputs(html_data, token_label, label_category):
    
    for filename, content in html_data.items():
        print(f"Contents of {filename}:")
        get_input_with_context_soup(html_content, token_label, label_category)

        is_desired_input = lambda tag: (tag.name == 'input' and 
                                tag.get('type') not in ['checkbox', 'radio', 'submit', 'hidden'])

        #print(content)
        soup = BeautifulSoup(content, 'html.parser')
        desired_inputs = soup.find_all(is_desired_input)
        selects = soup.find_all('select')
        checkboxes = soup.find_all('input', type='checkbox')
        radio_buttons = soup.find_all('input', type='radio')
        submit_buttons = soup.find_all('input', type='submit')
        textareas = soup.find_all('textarea')


    data = []
    for input_elem in non_hidden_inputs:
        
        label_text = ""
        # Find associated label using 'for' attribute
        associated_label = soup.find('label', {'for': input_elem.get('id')})
        
        # If input is a child of label, the parent is the associated label
        if not associated_label and input_elem.find_parent('label'):
            associated_label = input_elem.find_parent('label')
        
        if associated_label:
            label_text = associated_label.get_text(separator=' ', strip=True)

        context = ""
        # Gather preceding inline elements and text
        sibling = input_elem.find_previous_sibling()
        while sibling is not None and sibling.name not in ('input', 'div', 'label', 'form', 'table', 'ul', 'ol'):
            context = sibling.get_text(separator=' ', strip=True) + context
            sibling = sibling.find_previous_sibling()

        # Gather following inline elements and text
        sibling = input_elem.find_next_sibling()
        while sibling is not None and sibling.name not in ('input', 'div', 'label', 'form', 'table', 'ul', 'ol'):
            context += sibling.get_text(separator=' ', strip=True)
            sibling = sibling.find_next_sibling()

        data_item = dict(input_elem.attrs)
        data_item["context"] = context
        data_item["label"] = label_text
        data_item["xpath"] = ""
        data.append(data_item)

    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parsing html page to extract form fields.")
    parser.add_argument("--input", type=str, help="The input folder.")
    parser.add_argument("--output", type=str, help="The output file name.")
    parser.add_argument("--label", type=str, help="The output file name.")
    parser.add_argument("--mode", type=str, default = 'matching', help="The input folder.")

    args = parser.parse_args()
    # Example usage
    mode = args.mode
    if mode == 'processdata':
        output_file = args.output
        value_tokens = []
        token_label = dict()
        
        for key, value in data.items():
            #"firstName": ["first name", "legal first name"]
            for v in value:
                print(v.lower())
                token_label[v.lower()] = key
                value_tokens.append(v.lower())
        
        openai_api_key = os.environ["OPENAI_API_KEY"]
        resp = openai.Embedding.create(
                input=value_tokens,
                engine="text-embedding-ada-002")
        value_token_embedding = dict()
        for i in range(len(value_tokens)):
            #"first name", embeddding vector
            value_token_embedding[value_tokens[i]] = resp['data'][i]['embedding']

        with open(output_file, 'wb') as f:
            pickle.dump((value_token_embedding, token_label), f)

    if mode == 'labeling':
        input_file = args.input
        output_file = args.output

        label_example_embedding = dict()
        example_label = []
        with open("data.pkl", "rb") as f:
            (label_example_embedding, example_label) = pickle.load(f)
        
        label_example_embedding_array_2d = []
        labels = []
        for k, v in label_example_embedding.items():
            label_example_embedding_array_2d.append(v)
            labels.append(example_label[k])
        label_example_embedding_array_2d = np.vstack(label_example_embedding_array_2d)

        token_embedding = dict()
        with open(input_file, 'rb') as file:
            token_embedding = pickle.load(file)

        token_embedding_array_2d = []
        for k, v in token_embedding.items():
            token_embedding_array_2d.append(v)
        token_embedding_array_2d = np.vstack(token_embedding_array_2d)

        simmatrix = cosine_similarity_matrix(token_embedding_array_2d, label_example_embedding_array_2d)

        #print(simmatrix)
        label_dict = dict()
        for ind, (key, value) in enumerate(token_embedding.items()):
            dot_products = simmatrix[ind,:]
            max_index = np.argmax(dot_products)
            max_similarity = dot_products[max_index]
            print(f'{key} is mapped to {labels[max_index]} with score: {max_similarity}')
            if max_similarity > .95: 
                label_dict[key] = (labels[max_index], max_similarity)
        with open(output_file, 'wb') as f:
            pickle.dump(label_dict, f)

    if mode == "matching":
        directory_path = args.input
        output_path = args.output
        label_file = args.label
        with open(label_file, "rb") as f:
            label_dict = pickle.load(f)
            html_data = load_html_files_from_directory(directory_path)
            scan_for_inputs(html_data, label_dict, output_path)

    if mode == 'parsing':
        input_file = args.input
        output_file = args.output
        openai_api_key = os.environ["OPENAI_API_KEY"]
        inverted = {}
        with open(input_file, 'rb') as file:
            inverted = pickle.load(file)

        # Sort dictionary by the length of its values
        input_tokens = []
        sorted_items = sorted(inverted.items(), key=lambda item: len(item[1]), reverse=True)
        for item in sorted_items:
            key = item[0]
            value = item[1]
            key = nltk_tokenize(key)
            if len(key) >= 90 or len(key) <= 1:
                continue
            input_tokens.append(key)
        
        token_embedding = get_embedding(input_tokens)
        with open(output_file, 'wb') as f:
            pickle.dump(token_embedding, f)

    if mode == "indexing":
        directory_path = args.input
        output_file = args.output
        html_data = load_html_files_from_directory(directory_path)
        inverted = get_inverted_index(html_data)
        with open(output_file, 'wb') as f:
            pickle.dump(inverted, f)
    
