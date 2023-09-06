import argparse
import os
import re
import sys
import time
import json
import logging
from collections import defaultdict
#from langchain.llms import OpenAI
#import tiktoken
import openai
import numpy as np
from .utils import deserialize_dictionary  #TODO: fix the module import from parsing.py
from .utils import load_json_from_file
import ast


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# json_string = '{"First Name": "firstName", "Middle Name": "middleName", "Middle Initial": "middleName-initial", "Last Name": "lastName", "Individual Taxpayer Identification Number (itin)": "itin",\
#                "Mailing Addressline1": "mailingAddressLine1", "Mailing Addressline2 (optional)": "mailingAddressLine2", "Zipcode/Postcode": "zip/postalCode",\
#                "State/Province/Region": "state/province/region", "City": "city", "Country": "country", "Primary Phone Number": "primaryPhoneNumber", \
#                "Phone Type": "primaryPhoneType", "Employment Status":"employmentStatus", "Income(annual)": "income-annual-usd", "Housing Status": "housingStatus",\
#                "Monthly Rent/Mortgage": "monthlyRent/Mortgage", "Education Degree": "educationDegree", "Working Industry": "workingIndustry", \
#                "Professional Title": "professionalTitle", "Professional Tenure":"professionalTenure", "Social Security Number (ssn)": "ssn", \
#                "Date of Birth": "dob", "Email Address": "email"}'


json_string = '''{
  "First Name": "firstName",
  "Middle Name": "middleName",
  "Middle Initial": "middleName-initial",
  "Last Name": "lastName",
  "Suffix": "suffix",
  "Tax ID Type": "taxIDType",
  "Individual Taxpayer Identification Number (itin)": "itin",
  "Social Security Number (ssn)": "ssn",
  "Date of Birth (mm/dd/yyyy)": "dob-mm/dd/yyyy",
  "Mother Maiden Name": "motherMaidenName",
  "Address Type": "addressType",
  "Mailing Addressline1": "mailingAddressLine1",
  "Mailing Addressline2 (optional)": "mailingAddressLine2",
  "Zipcode/Postcode": "zip/postalCode",
  "State/Province/Region": "state/province/region",
  "City": "city",
  "Country": "country",
  "Primary Phone Type": "primaryPhoneType",
  "Primary Phone Number": "primaryPhoneNumber",
  "Email Address": "email",
  "Employment Status": "employmentStatus",
  "Income(annual)": "income-annual-usd",
  "Type of residence/Housing Status": "housingStatus",
  "Monthly Rent/Mortgage": "monthlyRent/Mortgage",
  "Education Degree": "educationDegree",
  "Working Industry": "workingIndustry",
  "Professional Title": "professionalTitle",
  "Professional Tenure": "professionalTenure",
  "Linkedin Profile": "linkedinProfile",
  "Personal Website": "personalWebsite",
  "Visa Sponsorship": "visaSponsorship"
}'''

# Convert the JSON string to a Python dictionary
name_maps = json.loads(json_string)


input_string = """First Name: Min
Middle Initial: NA
Last Name: Lu
Mailing Addressline1: 15481 Bristol Ridge Ter
Mailing Addressline2 (optional): #54
State/Province/Region: CA
City: San Diego
Zipcode/Postcode: 92127
Email Address: minlu19@gmail.com
Primary Phone Number: 2176399259
Employment Status: employed
Education Degree: Doctoral Degree (Ph.D, Ed.D, M.D.)
Income(annual): 250000
Monthly Rent/Mortgage: 2500
Date of Birth (mm/dd/yyyy): 12/15/1989
Social Security Number (ssn): 316-14-4952
Middle Name: NA
Suffix: None
Tax ID Type: SOCIAL_SECURITY_NUMBER
Individual Taxpayer Identification Number (itin): 316-88-8888
Country: USA
Primary Phone Type: CELL
Type of residence/Housing Status: OWN
Working Industry: Tech
Professional Title: Engineer
Professional Tenure: 10 Years
Address Type: DOMESTIC
Mother Maiden Name: A
Linkedin Profile: https://www.linkedin.com/in/abc/
Personal Website: https://www.abc.com
Visa Sponsorship: NO"""


# input_string = """First Name: Xin
# Middle Name: X
# Last Name: Xu
# Suffix: None
# Tax ID Type: SSN
# Individual Taxpayer Identification Number (itin): 316-14-8882
# Social Security Number (ssn): 316-14-8882
# Date of Birth (mm/dd/yyyy): 12/15/1989
# Mother's Maiden Name: A
# Address Type: DOMESTIC
# Mailing Addressline1: 15469 Bristol Ridge Ter
# Mailing Addressline2: #58
# Zipcode/Postcode: 92122
# State/Province/Region: CA
# City: San Diego
# Country: USA
# Primary Phone Type: CELL
# Primary Phone Number: 2176399999
# Email Address: minlu8@gmail.com
# Employment Status: Employed
# Income(annual): 250000
# Type of residence/Housing Status: OWN
# Monthly Rent/Mortgage: 2500
# Education Degree: Doctoral Degree (Ph.D, Ed.D, M.D.)
# Working Industry: Tech
# Professional Title: Engineer
# Professional Tenure: 10 Years
# """


# Split the string into lines
lines = input_string.splitlines()

# Initialize an empty dictionary
pii_dict = {}

# Iterate through the lines and add them to the dictionary
for line in lines:
    key, value = line.split(": ", 1)  # split at the first occurrence of ': '
    pii_dict[key] = value
piikeys = pii_dict.keys()
piistr = str(pii_dict)

print(piistr)


def classifier_function(item, targets, model = "gpt-4"):
    messages = [{"role": "user", "content": f"You are now acting like classifier from a object specified by ```{item}``` on to one of predefined list specified in: ```{targets}```, meaning the response should be one of the element in ```{targets}```.\n\n Only respond with your `return` value. Do not include any other explanatory text in your response."}]

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )

    return response.choices[0].message["content"]

def ai_function(function, args, description, model = "gpt-4"):
    # parse args to comma separated string
    args = ", ".join(args)
    messages = [{"role": "system", "content": f"You are now the following python function: ```# {description}\n{function}```\n\nOnly respond with your `return` value. Do not include any other explanatory text in your response."},{"role": "user", "content": args}]

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )

    return response.choices[0].message["content"]

def cosine_similarity_matrix(embeddings1, embeddings2):
    # Normalize the embeddings
    embeddings1_normalized = embeddings1 / np.linalg.norm(embeddings1, axis=1, keepdims=True)
    embeddings2_normalized = embeddings2 / np.linalg.norm(embeddings2, axis=1, keepdims=True)
    
    # Compute the similarity matrix
    similarity = np.dot(embeddings1_normalized, embeddings2_normalized.T)
    
    return similarity

def matching_simple(formfields, openai_api_key, model = "gpt-3.5-turbo"):
    openai.api_key = openai_api_key
    
    pii_names = []
    for readable_name, machine_name in name_maps.items():
        pii_names.append(readable_name)

    resp = openai.Embedding.create(
                input=pii_names,
                engine="text-embedding-ada-002")
      
    pii_name_embedding_array_2d = []
    for i in range(len(pii_names)):
        pii_name_embedding_array_2d.append(resp['data'][i]['embedding'])
    pii_name_embedding_array_2d = np.vstack(pii_name_embedding_array_2d)

    form_names = []
    for element in formfields:
        form_name = ""
        if 'name' in element:
            form_name = form_name + ' ' + element['name']
        elif 'label' in element:
            form_name = form_name + ' ' + element['label']
        elif 'context' in element:
            form_name = form_name + ' ' + element['context']
        if len(form_name) < 1:
            continue
        form_names.append(form_name)

    resp = openai.Embedding.create(
            input=form_names,
            engine="text-embedding-ada-002")

    form_name_embedding_array_2d = []
    for i in range(len(form_names)):
        form_name_embedding_array_2d.append(resp['data'][i]['embedding'])
    form_name_embedding_array_2d = np.vstack(form_name_embedding_array_2d)

    simmatrix = cosine_similarity_matrix(pii_name_embedding_array_2d, form_name_embedding_array_2d)
    
    form_name_candidates = {}
    for ind, form_name in enumerate(form_names):
        dot_products = simmatrix[:,ind]
        max_index = np.argmax(dot_products)
        max_similarity = dot_products[max_index]
        top_k_indices = np.argsort(dot_products)[-5:]
        candidates = []
        for index in top_k_indices:
            pii_name = pii_names[index]
            similarity = dot_products[index]
            if similarity > .6 and similarity > max_similarity - .05:
                candidates.append(pii_name)
        #verify the match with classification
        form_name_candidates[form_name] = candidates
    
    form_name_to_pii_name = []
    for element in formfields:
        form_name = ""
        machine_name = "no match"
        sub_dict = ""
        if 'name' in element:
            form_name = form_name + ' ' + element['name']
            sub_dict = element['name']
        elif 'label' in element:
            form_name = form_name + ' ' + element['label']
        elif 'context' in element:
            form_name = form_name + ' ' + element['context']
        if len(form_name) >= 1:
            #print('\n\n')
            #print(form_name)
            sub_dict = sub_dict + ' ' +element['label'] + ' ' + element['context']
            candidates = form_name_candidates[form_name]
            result = classifier_function(sub_dict, candidates,  "gpt-3.5-turbo")
            element['matched'] = result
            if result in name_maps:
                machine_name = name_maps[result]
            else:
                logging.warning(f"Key not found in name_maps: {result}")
            #print(candidates)
            #print(result)
        xid = ''
        if 'id' in element:
            xid = '#'+element['id']
        xpath = element['xpath']
        input_type = 'NA'
        if 'type' in element:
            input_type = element['type']
        pii_name = machine_name
        mapped_value = 'N/A'
        form_name_to_pii_name.append((xid, xpath, pii_name, mapped_value, input_type))
    return form_name_to_pii_name
    
def matching(formfields, openai_api_key, model = "gpt-3.5-turbo"):
    openai.api_key = openai_api_key
    form_key_values = []
    form_key_texts = defaultdict(dict)
    for key, values in formfields.items():
        if (key[1] is None) or (len(key[1]) < 1):
            continue
        form_key_values.append(key[1])
        text_to_value = dict()
        for v in values:
            print(v)
            # key[1] is the actual name / context of the input group
            # v[0], v[1] is the id and xpath of input element, 
            # v[2] is the value of the input element
            text_to_value[(key[1], str(v[2]))] = (v[0],v[1],v[3])

        form_key_texts[key[1]] = text_to_value

    unique_form_keys = set(form_key_values)
    if len(unique_form_keys) < len(form_key_values):
        logging.warning('This means some form field names have duplication')
        exit(1)

    #print(formfields['input group 5  Social Security number'])
    
    pii_key_values = []
    for key, values in pii_dict.items():
        pii_key_values.append(key)
    
    #print(form_key_values)
    #print(pii_key_values)
    
    function_string = "def map_names(form_key_values: list, pii_key_values: list) -> dict:"
    description_string = """Based on the semantic of list elements, build a map from the first list to the second list."""
    args = [str(pii_key_values), str(form_key_values)]
    result_string = ai_function(function_string, args, description_string, model)
    logging.info(result_string)
    result = ast.literal_eval(result_string)
    print(result)
    filtered_result = {}
    for pii_name_raw, form_name in result.items():
        if (form_name is None) or (len(form_name) == 0):
            continue
        print(pii_name_raw)
        print(form_name)
        # Compute the cosine similarity
        resp = openai.Embedding.create(
            input=[pii_name_raw, form_name],
            engine="text-similarity-davinci-001")

        embedding_a = resp['data'][0]['embedding']
        embedding_b = resp['data'][1]['embedding']

        similarity = np.dot(embedding_a, embedding_b)
        #similarity = nlp(pii_name_raw).similarity(nlp(form_name))
        print(similarity)
        if similarity >=.6:
            filtered_result[pii_name_raw] = form_name
    result = filtered_result

    form_name_to_pii_name = []
    
    matched_form_fields = set(result.values())
    for form_name in form_key_values:
        if len(form_name) < 1:
            continue
        if form_name not in matched_form_fields:
            form_value = []
            for (k,v) in form_key_texts[form_name]:
                form_value.append(v)
            if len(form_value) > 1:
                for k, v in form_key_texts[form_name]:
                    xid = v[0]
                    xpath = v[1]
                    input_type = v[2] if len(v) > 2 else 'unknown'
                    print(input_type)
                    form_name_to_pii_name.append((xid, xpath, 'unknown', 'na', input_type))
            if len(form_value) == 1:
                default_value = form_value[0]
                xid, xpath, input_type = form_key_texts[form_name][(form_name, default_value)]
                print(input_type)
                form_name_to_pii_name.append((xid, xpath, 'unknown', 'na', input_type))

    for pii_name_raw, form_name in result.items():
        
        if pii_name_raw in name_maps:
            pii_name = name_maps[pii_name_raw]
        else:
            logging.warning(f"Key not found in name_maps: {pii_name_raw}")
            continue

        form_value = []
        for (k,v) in form_key_texts[form_name]:
            form_value.append(v)
        print(pii_name_raw)
        print(pii_name)
        print(form_name)
        print(form_value)
        pii_value = pii_dict[pii_name_raw]

        if len(form_value) > 1:
            function_string = "def value_select(values: list, query: str) -> str:"
            args = [str(form_value), pii_value]
            description_string = """Based on the query string to select the best value in the list. Please output the whole result, no abbreviation"""
            mapped_value = ai_function(function_string, args, description_string, model)
            if (form_name, mapped_value) in form_key_texts[form_name]:
                xid, xpath, input_type = form_key_texts[form_name][(form_name, mapped_value)]
                # logging form_name_values
                logging.info((xid, xpath, mapped_value))
                form_name_to_pii_name.append((xid, xpath, pii_name, mapped_value))
            else:
                logging.warning(f"Key not found in form key texts map: {(form_name, mapped_value)}")
            for k, v in form_key_texts[form_name]:
                if (k[0] == form_name) and (k[1] == mapped_value):
                    continue
                xid = v[0]
                xpath = v[1]
                input_type = v[2]
                print(input_type)
                form_name_to_pii_name.append((xid, xpath, 'unselected', 'na', input_type))

        if len(form_value) == 1:
            #check if there is format string availale 
            default_value = form_value[0]
            xid, xpath, input_type = form_key_texts[form_name][(form_name, default_value)]
            mapped_value = ''
            if len(default_value) > 1:
                function_string = "def value_norm(format: str, value: str) -> str:"
                args = [default_value, pii_value]
                print(default_value)
                description_string = """Based on the format string, normalized the value string."""
                mapped_value = ai_function(function_string, args, description_string, model)
            else:
                mapped_value = pii_value
            # logging form_name_values
            logging.info((xid, xpath, mapped_value))
            form_name_to_pii_name.append((xid, xpath, pii_name, mapped_value, input_type))

        if len(form_value) == 0:
            mapped_value = pii_value
            # logging form_name_values
            logging.info((xid, xpath, mapped_value))
            form_name_to_pii_name.append((xid, xpath, pii_name, mapped_value, input_type))
    return form_name_to_pii_name

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matching pii data to extracted form fields.")
    parser.add_argument("--method", type=str, default="simple", help="The pii data json file.")
    parser.add_argument("--formfields", type=str, help="The extraced form fields pickle file.")
    parser.add_argument("--output", type=str, help="The filled information for #id/#xpath of input elements, in json format.")


    args = parser.parse_args()
    
    if args.method == 'simple':
        formfields = load_json_from_file(args.formfields)
        openai_api_key = os.environ["OPENAI_API_KEY"]
        json_output = args.output
        model = "gpt-3.5-turbo"
        form_name_to_pii_name = matching_simple(formfields, openai_api_key, model)
        with open(json_output, 'w') as json_file:
            json.dump(form_name_to_pii_name, json_file)
    
    else:
    
        formfields = deserialize_dictionary(args.formfields)
        openai_api_key = os.environ["OPENAI_API_KEY"]
        json_output = args.output
        
        model = "gpt-3.5-turbo"
        form_name_to_pii_name = matching(formfields, openai_api_key, model)
        
        with open(json_output, 'w') as json_file:
            json.dump(form_name_to_pii_name, json_file)
    