import selenium import webdriver
import pandas as pd
import time

# settings
options = webdriver.ChromeOptions()
options.add_argument('--headeless')