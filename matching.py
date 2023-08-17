import argparse
import os
import re
import sys
import time
import json
import logging
from collections import defaultdict
from langchain.llms import OpenAI
import tiktoken
import openai
from langchain import PromptTemplate
from parsing import deserialize_dictionary
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
  "Professional Tenure": "professionalTenure"
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
Mother Maiden Name: A"""


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matching pii data to extracted form fields.")
    #parser.add_argument("--pii", type=str, help="The pii data json file.")
    parser.add_argument("--formfields", type=str, help="The extraced form fields pickle file.")
    parser.add_argument("--output", type=str, help="The filled information for #id/#xpath of input elements, in json format.")


    args = parser.parse_args()
    
    #pii = deserialize_dictionary(args.pii)
    
    formfields = deserialize_dictionary(args.formfields)
    json_output = args.output
    openai.api_key = os.environ["OPENAI_API_KEY"]

    model = "gpt-3.5-turbo"
    
    form_key_values = []
    form_key_texts = defaultdict(dict)
    for key, values in formfields.items():
        if len(key[1]) < 1:
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
    
    form_name_to_pii_name = []
    
    matched_form_fields = set(result.values())
    for form_name in form_key_values:
        if len(key[1]) < 1:
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

        if form_name is None or len(form_name) == 0:
            continue

        form_value = []
        for (k,v) in form_key_texts[form_name]:
            form_value.append(v)

        print(form_value)
        pii_value = pii_dict[pii_name_raw]

        if len(form_value) > 1:
            function_string = "def value_select(values: list, query: str) -> str:"
            args = [str(form_value), pii_value]
            description_string = """Based on the query string to select the best value in the list."""
            mapped_value = ai_function(function_string, args, description_string, model)
            xid, xpath, input_type = form_key_texts[form_name][(form_name, mapped_value)]
            # logging form_name_values
            logging.info((xid, xpath, mapped_value))
            form_name_to_pii_name.append((xid, xpath, pii_name, mapped_value))
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

    with open(json_output, 'w') as json_file:
        json.dump(form_name_to_pii_name, json_file)
    