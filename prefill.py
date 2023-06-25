from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.common.keys import Keys
import time 
 
options = webdriver.ChromeOptions() 
options.headless = False 
service = ChromeService('/path-to-chromedriver/chromedriver')
driver = webdriver.Chrome(service=service, options=options)

# load target website 
url =  'http://www.capitalone.com'
 
# get website content 
driver.get(url) 

time.sleep(15)
