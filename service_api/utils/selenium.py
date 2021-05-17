"""
Module of grabbing service contains driver for selenium
"""
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DRIVER = None


def init_driver(link):
    """
    A function to initialize Chrome WebDriver
    """
    global DRIVER

    if DRIVER is None:
        options = Options()
        options.headless = True
        DRIVER = webdriver.Chrome(os.environ.get("SELENIUM_PATH"), options=options)
        DRIVER.get(link)

    return DRIVER
