# Data-gene
Data-gene is a repository of python code contains the base setup of an UI testing project, using Python, Selenium Webdriver and Page Object Model pattern for helping user to manage their PII data for automation purpose (like application automation, form prefill, etc.)    

The prefill.py leverage python selenium tool to automate the form prefill for user with user content.  

# Requirements
Python 3.11.X  
pip and setuptools  
venv (recommended)  

# Instalation
Download or clone the repository.  
Open a terminal.  
Go to the project root directory "/data-gene/".  
Create a virtual environment.  
Activate the virtual environment.  
Execute the following command to download the necessary libraries: pip install -r requirements.txt.  
Download right version of chromedriver from [here](https://chromedriver.chromium.org/downloads)

# Selenium Demo
Open a terminal  
From the project root directory run: python prefill.py https://www.capitalone.com/credit-cards/preapprove/?landingPage=cchp

# Parsing Demo
Open a terminal  
From the project root directory run: python parsing.py --html ./test.html --output ./test.pickle

# Matching Demo
Open a terminal  
From the project root directory run: python matching.py --formfields test.pickle --output form.json

# Configuration
By default, demo will be executed in Chrome (normal mode). 

# Links
[Selenium - Python Documentation](https://selenium-python.readthedocs.io/)  
[Webdriver Manager for Python](https://pypi.org/project/webdriver-manager/)  
[lxml parser](https://lxml.de/parsing.html)  
[Form filling with Selenium](https://iqss.github.io/dss-webscrape/filling-in-web-forms.html)
