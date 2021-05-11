"""
Module of grabbing service contains driver for selenium
"""

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True

driver = webdriver.Chrome(os.environ.get("SELENIUM_PATH"), options=options)
