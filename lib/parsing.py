import argparse
import lxml
import os
import re
import sys
import time
import logging
from bs4 import BeautifulSoup
from collections import defaultdict
from io import StringIO
from lxml import etree, html
from json import loads, dumps
from ast import literal_eval
import pickle
from lib.utils import serialize_dictionary
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def print_elements(element, indent=0):
    # Print the current element's tag name and attributes
    print(' ' * indent + element.tag + " " + str(element.attrib))
    
    # Recursively print child elements
    for child in element:
        print_elements(child, indent + 2)

def load_html(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        html_content = file.read()
    return html_content

def is_same_pattern(xpath1, xpath2):
    #check if two xpathes are the same pattern, like following example 
    #xpath1 = '/card-check-box-list/div[1]/div/input'
    #xpath2 = '/card-check-box-list/div[2]/div/input'
    #perfect match retunr 1, non perfect match return 0
    fieldAs = xpath1.split('/')
    fieldBs = xpath2.split('/')
    pattern = r"(\w+)\[(\d+)\]"

    if len(fieldAs) != len(fieldBs):
        return False
    count = 0
    for item1, item2 in zip(fieldAs[:-1], fieldBs[:-1]):
        if item1 == item2:
            continue
        #check if they match pattern \w+\[\d+\]
        match, word_a, digit_a = match_pattern(pattern, str(item1))
        if not match:
            return False
        match, word_b, digit_b = match_pattern(pattern, str(item2))
        if not match:
            return False
        if word_b == word_a and digit_b == digit_a + 1:
            count = count + 1
        else:
            return False
    if count <=1:
        return True
    return False

def match_pattern(pattern, item):
    #print(pattern)
    match = re.match(pattern, item)
    word_part = ''
    digit_part = -1
    if match:
        word_part = match.group(1)
        digit_part = int(match.group(2))
    return match, word_part, digit_part

def check_input_leafs(common_path, input_xpathes):
    count = 0
    leafs_pathes = []
    for xpath in input_xpathes:
        if xpath.startswith(common_path):
            count = count + 1
            leafs_pathes.append(xpath)
    if count == 0:
        #warning this shouldn't happen if all text elements grouping correctly
        logging.warning('This means some text elements are not groped correctly')
        return False
    if count == 1:
        return True
    #print(common_path)
    #print(input_xpathes)
    first_path = leafs_pathes[0]
    is_one_cluster = True
    for path in leafs_pathes:
        if not is_same_pattern(first_path, path):
            is_one_cluster = False
            break
    return is_one_cluster

def id_tranformation(item_id):
    return f"#{item_id}"

def process_checkbox_elements(checkbox_inputs, tree):
    # Create a dictionary to store checkbox group values
    # return key value dictionary, where key is the xpath of the first element in one group
    checkbox_groups = defaultdict(list)
    # Iterate over the checkbox input elements
    isFirst = True
    preXpath = ''
    for input_elem in checkbox_inputs:
        #value = input_elem.label.text_content()
        xpath_expression = tree.getpath(input_elem)
        if isFirst:
            preXpath = xpath_expression
            group_name = xpath_expression
            checkbox_groups[group_name].append(input_elem)
            isFirst = False
        else:
            samePattern = is_same_pattern(preXpath, xpath_expression)
            if samePattern:
                checkbox_groups[group_name].append(input_elem)
                preXpath = xpath_expression
            else:
                group_name = xpath_expression
                preXpath = xpath_expression
                checkbox_groups[group_name].append(input_elem)
    return checkbox_groups


def process_radio_elements(radio_inputs, tree):
    # Create a dictionary to store radio group values
    radio_groups = defaultdict(list)
    # Iterate over the radio input elements
    isFirst = True
    preName = ''
    for input_elem in radio_inputs:
        name = input_elem.get('name')
        #value = input_elem.label.text_content()
        xpath_expression = tree.getpath(input_elem)
        if isFirst:
            preName = name
            group_name = xpath_expression
            radio_groups[group_name].append(input_elem)
            isFirst = False
        else:
            if name == preName:
                radio_groups[group_name].append(input_elem)
            else:
                preName = name
                group_name = xpath_expression
                radio_groups[group_name].append(input_elem)
    return radio_groups


def process_select_elements(select_inputs, tree):
    select_groups = defaultdict(list)
    for node in select_inputs:
        xpath_expression = tree.getpath(node)
        select_groups[xpath_expression].append(node)
    return select_groups


def process_input_elements(inputs, tree):
    input_groups = defaultdict(list)
    for node in inputs:
        xpath_expression = tree.getpath(node)
        name = ''
        if node.label is not None:
            name = node.label.text_content() 
        value = node.value
        input_groups[xpath_expression].append(node)
    return input_groups

def process_text_elements(text_elements, tree):
    #group sibling text elements into one group, group key is the first xpath of the group
    text_groups = defaultdict(list)
    isFirst = True
    preXpath = ''
    for input_elem in text_elements:
        #print(etree.tostring(input_elem, pretty_print=True).decode('utf-8'))
        xpath_expression = tree.getpath(input_elem)
        if isFirst:
            preXpath = xpath_expression
            group_name = xpath_expression
            isFirst = False
        else:
            areSiblings = is_same_pattern(preXpath, xpath_expression) | xpath_expression.startswith(preXpath)
            if areSiblings:
                text_groups[group_name].append(input_elem)
            else:
                group_name = xpath_expression
                text_groups[group_name].append(input_elem)
                preXpath = xpath_expression
    return text_groups

def match_text_inputs(index_cat, index_xpath, input_xpathes):
    sorted_keys = sorted(index_cat)
    associated_text_node = defaultdict()
    
    for i in range(0,len(sorted_keys)):
        cur_key = sorted_keys[i]
        pre_key = -1
        if i > 0:
            pre_key = sorted_keys[i-1]
        next_key = -1
        if i < len(sorted_keys) - 1:
            next_key = sorted_keys[i+1]
        if (index_cat[cur_key] == 'text'):
            #need to associate the text element to right structural element
            xpath_cur = index_xpath[cur_key]
            
            xpath_pre = ''
            if pre_key > 0:
                xpath_pre = index_xpath[pre_key]
            xpath_next = ''
            if next_key > 0:
                xpath_next = index_xpath[next_key]
            paths = [xpath_pre, xpath_cur]
            common_path_pre = os.path.commonprefix(paths)
            paths = [xpath_next, xpath_cur]
            common_path_next = os.path.commonprefix(paths)
            
            if len(common_path_pre) >= len(common_path_next):
                #check if common_path_pre has too many input leafs
                if check_input_leafs(common_path_pre, input_xpathes):
                    associated_text_node[xpath_pre] = xpath_cur
            else:
                #check if common_path_next has too many input leafs
                if check_input_leafs(common_path_next, input_xpathes):
                    associated_text_node[xpath_next] = xpath_cur
    return associated_text_node

def grap_context_text(xpath, associated_text_path, text_group):
    context = ''
    if xpath in associated_text_path:
        text_xpath = associated_text_path[xpath]
        text_nodes = text_group[text_xpath]
        context_text = []
        for node in text_nodes:
            context_text.append(node.text_content())
        context = ' '.join(context_text)
        context = context.replace('\n', '').replace('\r', '')
    return context

def pack_raido_group(radio_group, associated_text_path, text_group, result):
    for xpath, radio_nodes in radio_group.items():
        name = ('radio group', grap_context_text(xpath, associated_text_path, text_group).strip())
        values = []
        for node in radio_nodes:
            #print(node.type)
            if node and node.label and node.label.text_content():
                label_text = node.label.text_content().strip()
            else:
                label_text = ''
            label_text = label_text.replace('\n', '').replace('\r', '')
            values.append((id_tranformation(node.get('id')), xpath, label_text, node.type))
        result[name] = values
    return result

def pack_checkbox_group(checkbox_group, associated_text_path, text_group, result):
    for xpath, checkbox_nodes in checkbox_group.items():
        name = ('checkbox group',  grap_context_text(xpath, associated_text_path, text_group).strip())
        values = []
        for node in checkbox_nodes:
            #print(node.type)
            label_text = ""
            if node.label:
                label_text = node.label.text_content().replace('\n', '').replace('\r', '')
            values.append((id_tranformation(node.get('id')), xpath, label_text, node.type))
        result[name] = values
    return result

def pack_select_group(select_group, associated_text_path, text_group, result):
    for xpath, select_nodes in select_group.items():
        name_prefix = 'select group'
        for node in select_nodes:
            option_elements = node.xpath(".//option")
            # Extract option values
            values = [option.get("value") for option in option_elements]
            if node and node.label and node.label.text_content():
                label_text = node.label.text_content().strip()
            else:
                label_text = ''
            label_text = label_text.replace('\n', '').replace('\r', '')
            name = (name_prefix, label_text)
            node_name = ""
            if node.get('name'):
                node_name = node.get('name')
            result[name] = [(id_tranformation(node.get('id')), xpath, values, 'select:'+ node_name)]
    return result

def pack_input_group(input_group, associated_text_path, text_group, result):
    for xpath, input_nodes in input_group.items():
        name_prefix = 'input group'
        for node in input_nodes:
            if node.label is not None \
                and node.label.text_content() is not None \
                and len(node.label.text_content()) >= 1:
                name = (name_prefix, node.label.text_content().strip())
            elif node.name is not None:
                name = (name_prefix, node.name)
            elif node.get('id') is not None:
                name = (name_prefix, id_tranformation(node.get('id')))
            else:
                name = (name_prefix, node.get('aria-labelledby'))
            #print(etree.tostring(node))
            values = [(id_tranformation(node.get('id')), xpath, node.value, node.type)]
            result[name] = values

    return result

def preprocess_parent_labels(labels):
    #//label[input or select]
    for label in labels:
        # Find the first input or select element inside the label
        child_elements = label.findall('./input')
        select_elements = label.findall('./select')
        if len(select_elements) > 0:
            child_elements = child_elements + select_elements
        # If the element is found and doesn't have an id, generate one
        for child_element in child_elements:
            if child_element.get('type') == 'hidden':
                continue
            if child_element.get('id') is None:
                # Generate a unique ID for the element
                element_id = f"element_{id(child_element)}"
                child_element.set('id', element_id) 
            # Set the 'for' attribute of the label to match the element's id
            element_id = child_element.get('id')   
            label.set('for', element_id)


def parsing_page(page):
    #checkbox elements
    tree = etree.ElementTree(page)

    #Find all normal input elements
    labels = tree.xpath("//label[input or select]")
    preprocess_parent_labels(labels)

    # Find all checkbox input elements
    checkbox_inputs = tree.xpath("//input[@type='checkbox']")
    checkbox_group = process_checkbox_elements(checkbox_inputs, tree)
    
    # Find all radio input elements
    radio_inputs = tree.xpath("//input[@type='radio']")
    radio_group = process_radio_elements(radio_inputs, tree)
    
    # Find all select elements
    select_inputs = tree.xpath("//select")
    select_group = process_select_elements(select_inputs, tree)
    
    #Find all normal input elements
    inputs = tree.xpath("//input[not(@type='radio' or @type='checkbox' or @type='hidden')]")
    input_group = process_input_elements(inputs, tree)

    #Find all text elements (excluding label subtree)
    text_elements = tree.xpath(
    "//h1[not(ancestor::label)] | //h2[not(ancestor::label)] | //span[not(ancestor::label)] | //strong[not(ancestor::label)] | //legend[not(ancestor::label)]")
    text_group = process_text_elements(text_elements, tree)
    
    index_cat = defaultdict()
    index_xpath = defaultdict()
    index = 0
    for node in tree.iter():
        xpath = tree.getpath(node)
        index_xpath[index] = xpath
        if xpath in text_group:
            index_cat[index] = 'text'
        if xpath in checkbox_group:
            index_cat[index] = 'input'
        if xpath in radio_group:
            index_cat[index] = 'input'
        if xpath in input_group:
            index_cat[index] = 'input'
        index = index + 1
    
    #Associate text elements to input elements
    input_xpathes = []
    for index, category in index_cat.items():
        if category == 'input':
            input_xpathes.append(index_xpath[index])
    associated_text_path = match_text_inputs(index_cat, index_xpath, input_xpathes)
    result = defaultdict(list)
    
    #for raido group, key = potential associated text, value = list of radio nodes' label text
    pack_raido_group(radio_group, associated_text_path, text_group, result)
    #for checkbox group, key = potential associated text, value = list of checkboxs' label text
    pack_checkbox_group(checkbox_group, associated_text_path, text_group, result)
    #for select group, key = the select label text, value = list of option values
    pack_select_group(select_group, associated_text_path, text_group, result)
    #for normal input group, key = label text, value = default value / none
    pack_input_group(input_group, associated_text_path, text_group, result)

    return result
    
def print_input_with_context_soup(soup):
    all_texts = list(soup.stripped_strings)
    print(all_texts)
    exit(1)
    non_hidden_inputs = soup.find_all(lambda tag: (isinstance(tag, type(soup.new_tag("test"))) and 
                                              tag.name == 'input' and 
                                              tag.get('type') != 'hidden'))
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


def print_input_with_context(parsed_html):
    # Find all <input> elements
    input_elements = parsed_html.xpath("//input[not(@type='hidden')]")
    tree = etree.ElementTree(parsed_html)
    data = []
    for input_elem in input_elements:
        context = ""
        label_text = ""
        # Try to find an associated <label> using the 'for' attribute
        if 'id' in input_elem.attrib:
            input_id = input_elem.attrib['id']
            label_elem = parsed_html.xpath(f'//label[@for="{input_id}"]')
            if label_elem:
                label_text = label_elem[0].text_content().strip()
        
        # If the <input> is a direct child of a <label>
        parent = input_elem.getparent()
        if parent.tag == 'label':
            # Use the text content of the <label> as context, but exclude the <input> itself
            label_text = parent.text_content().replace(html.tostring(input_elem, encoding="unicode").strip(), "").strip()
        
        # If no label or context was found, gather surrounding text and inline elements
        if not context:
            # Gather preceding inline elements and text
            sibling = input_elem.getprevious()
            while sibling is not None and sibling.tag not in ('input', 'div', 'label', 'form', 'table', 'ul', 'ol'):
                context = sibling.text_content() + context
                sibling = sibling.getprevious()
            
            # Gather following inline elements and text
            sibling = input_elem.getnext()
            while sibling is not None and sibling.tag not in ('input', 'div', 'label', 'form', 'table', 'ul', 'ol'):
                context += sibling.text_content()
                sibling = sibling.getnext()
        data_item = dict(input_elem.attrib)
        data_item["context"] = context
        data_item["label"] = label_text
        data_item["xpath"] = tree.getpath(input_elem)
        data.append(data_item)
        print("Context:", context)
        print("Input:", html.tostring(input_elem, encoding="unicode").strip())
        print('---')
    return data


def html_parsing(html_content):

    # Attempt to parse the content using lxml
    try:
        #page = etree.fromstring(html_content, etree.HTMLParser())
        page = lxml.html.fromstring(html_content)
        print(page)
        parsing_success = True
        print(page)
        result = parsing_page(page)
        return result
    except etree.ParserError as e:
        error_message = str(e)
        print(error_message)
        parsing_success = False
        return None

def html_parsing_simple(html_content):
    page = BeautifulSoup(html_content, 'html.parser')
    
    data = print_input_with_context_soup(page)
    json_data = dumps(data)
    return json_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parsing html page to extract form fields.")
    parser.add_argument("--html", type=str, help="The input html file.")
    parser.add_argument("--method", type=str, default="simple", help="The pii data json file.")
    parser.add_argument("--output", type=str, help="The output file.")
    

    args = parser.parse_args()
    
    if args.method == 'simple':
        html_content = load_html(args.html)
        json_data = html_parsing_simple(html_content)
        with open(args.output, 'w') as file:
            file.write(json_data)
    else:
        html_content = load_html(args.html)
        
        result = html_parsing(html_content)
        
        serialize_dictionary(result, args.output)

    


    
    
