# Data-gene
Data-gene is a repository of python code contains the base setup of an UI testing project, using Python, Selenium Webdriver and Page Object Model pattern for helping user to manage their PII data for automation purpose (like application automation, form prefill, etc.) 

The prefill.py leverage python selenium tool to automate the form prefill for user with user content. 
This repository .

# Requirements
Python 3.11.X
pip and setuptools
venv (recommended)

# Instalation
Download or clone the repository
Open a terminal
Go to the project root directory "/data-gene/".
Create a virtual environment: py -m venv venv
Activate the virtual environment executing the following script: .\venv\Scripts\activate
Execute the following command to download the necessary libraries: pip install -r requirements.txt

# Test Execution
Open a terminal
From the project root directory run: pytest -v --html=results/report.html

# Configuration
By default, tests will be executed in Chrome (normal mode). Preferences can be changed in "/data/config.yaml" file

# Results
To check the report, open the '/results/report.html' file once the execution has finished.

# Links
Selenium - Python Documentation

Webdriver Manager for Python
