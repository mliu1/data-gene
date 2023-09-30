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
from lib.upload import upload_json
from lib.download import fetch_html_content,fetch_hashes,fetch_lists,fetch_pageDetails
from lib.matching import cosine_similarity_matrix,load_html_files_from_directory,get_embedding,get_inverted_index,get_all_inputs,get_label_for_inputs,check_ground_truth,get_label_for_fields
    
data = {
    "firstName": ["first name", "legal first name", "firstName"],
    "middleName": ["Middle Name", "Middle Initial", "middle initial (optional)", "middleName"],
    "lastName": ["Last Name", "Legal Last Name", "lastName"],
    "veteranStatus":["Veteran Status"],
    "disabilityStatus":["Disability Status"],
    "visaSponsorship":["Visa Sponsorship"],
    "isHispanicLatino":["is Hispanic/Latino"],
    "gender": ["Gender"],
    "race": ["Race"],
    "fullName":["fullName", "full name"],
    "suffix": ["Suffix", "suffix (optional)"],
    "suffixValue": ["jr", "sr", "ii", "iii", "iv"],
    "taxIDType": ["Tax ID Type"],
    "itin": ["Individual Taxpayer Identification Number", "individual tax id", "itin"],
    "ssn": ["SSN/ITIN", "Social Security Number", "Social Security", "ssn", "ssn or individual tax id", "social security number or individual taxpayer identification"],
    "ssnFormat": ["xxx-xx-xxxx"],
    "dob": ["Date of Birth", "dateOfBirth" "dob", "date of birth (mm/dd/yyyy)"],
    "dateFormat": ["mm/dd/yyyy"],
    "mother MaidenName": ["Mother Maiden Name", "mother's maiden name"],
    "addressType": ["Address Type"],
    "mailingAddressLine1": ["Home or permanent address", "Mailing Address","Residence Address", "street address", "residential address", "Residential Address (P.O. Box is not valid)", "mailing address", "billing address"],
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

    if mode == "verify":
        url_base = 'https://form-fill-mongodb.vercel.app/api/html/find?hash='
        hash_string = args.input
        targets = fetch_lists(url_base, hash_string, "prodSelection")
        preds = fetch_lists(url_base, hash_string, "selection")
        preds = json.loads(preds) #the raw output is a string object, convert it to list
        true_det, false_det, missing_det, match_cat = check_ground_truth(targets, preds)
        print(f"True detection: {true_det}, false detection: {false_det}, missing detection: {missing_det} ")
        print(match_cat)

    if mode == "online":
        url_base = 'https://form-fill-mongodb.vercel.app/api/html/find?hash='
        hash_string = args.input
        label_file = args.label
        with open(label_file, "rb") as f:
            label_dict = pickle.load(f)
            #html_content = fetch_html_content(url_base, hash_string)
            #soup, inputs = get_all_inputs(html_content)
            #data = get_label_for_inputs(inputs, soup, label_dict)
            fields = fetch_pageDetails(url_base, hash_string)
            data = get_label_for_fields(fields, label_dict)
            json_string = json.dumps(data)
            print(json_string)
            upload_json(hash_string, json_string)
