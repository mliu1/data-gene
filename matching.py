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

input_string = """First name: Min
MIDDLE INITIAL: NA
Last name: Lu
Residential address: 15481 Bristol Ridge Ter
Address line 2: #54
State: CA
City: San Diego
Zipcode: 92127
Email address: minlu19@gmail.com
Primary phone number: 2176399259
Employment status: employed
Education degree: PhD
Income (annual): 250000
Monthly rent/mortgage: 2500
Date of birth (MM/DD/YYYY): 12/15/1989
Social Security number: 326-02-2932"""

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
    parser.add_argument("--output", type=str, help="The filled information for #id/#xapth of input elements, in json format.")


    args = parser.parse_args()
    
    #pii = deserialize_dictionary(args.pii)
    
    formfields = deserialize_dictionary(args.formfields)
    json_output = args.output
    openai.api_key = os.environ["OPENAI_API_KEY"]

    model = "gpt-3.5-turbo"
    
    form_key_values = []
    form_key_texts = defaultdict(dict)
    for key, values in formfields.items():
        form_key_values.append(key[1])
        text_to_value = dict()
        for v in values:
            # key[1] is the actual name / context of the input group
            # v[0], v[1] is the id and xpath of input element, 
            # v[2] is the value of the input element
            text_to_value[(key[1], str(v[2]))] = (v[0],v[1])

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
    description_string = """Based on the semantic of list elements, build a map between of two input lists."""
    args = [str(pii_key_values), str(form_key_values)]
    result_string = ai_function(function_string, args, description_string, model)
    result = ast.literal_eval(result_string)
    print(result)

    form_name_values = []

    for pii_name, form_name in result.items():
        
        if len(form_name) == 0:
            continue

        form_value = []
        for (k,v) in form_key_texts[form_name]:
            form_value.append(v)

        print(form_value)
        pii_value = pii_dict[pii_name]

        if len(form_value) > 1:
            function_string = "def value_select(values: list, query: str) -> str:"
            args = [str(form_value), pii_value]
            description_string = """Based on the query string to select the best value in the list."""
            mapped_value = ai_function(function_string, args, description_string, model)
            form_name_values[form_name] = mapped_value
            xid, xpath = form_key_texts[form_name][(form_name, mapped_value)]
            form_name_values.append((xid, xpath, mapped_value))
        if len(form_value) == 1:
            #check if there is format string availale 
            default_value = form_value[0]
            xid, xpath = form_key_texts[form_name][(form_name, default_value)]
            mapped_value = ''
            if len(default_value) > 1:
                function_string = "def value_norm(format: str, value: str) -> str:"
                args = [default_value, pii_value]
                print(default_value)
                description_string = """Based on the format string, normalized the value string."""
                mapped_value = ai_function(function_string, args, description_string, model)
            else:
                mapped_value = pii_value
            form_name_values.append((xid, xpath, mapped_value))

    #print(form_name_values)
    with open(json_output, 'w') as json_file:
        json.dump(form_name_values, json_file)
    


    
    