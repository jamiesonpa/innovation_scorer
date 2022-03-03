from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
import time
from datetime import date
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import numpy as np
from matplotlib import pyplot as plt
import pyautogui




#first get a list of companies and get them into a dict where they key:value pairings is company name:company location
with open("international_companies.txt") as readfile:
    companies = readfile.read().split("/n")

company_dict = {}
for company in companies:
    company_name = company.split(",")[0]
    company_location = company.split(",")[1]
    company_dict[company_name] = company_location

#now log into capiq
driverPath = os.getcwd() +"/chromedriver.exe"
options = webdriver.ChromeOptions()


default_download_path = os.getcwd()

prefs = {"download.default_directory" : default_download_path}
options.add_experimental_option("prefs",prefs)
options.add_argument('--no-sandbox')
options.add_argument('--disable-setuid-sandbox')
options.add_argument("--proxy-server='direct://")
options.add_argument('--proxy-bypass-list=*')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-accelerated-2d-canvas')
options.add_argument('--disable-gpu')
options.add_argument("start-maximized")
options.add_argument("-incognito")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options, executable_path=os.getcwd()+"/chromedriver.exe")
url = 'https://www.capitaliq.com/'
email = "<input username here>"
password = "<input password here>"
driver.get(url)

hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36","X-Requested-With": "XMLHttpRequest"}

time.sleep(1)
driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/form/table/tbody/tr[1]/td/ol/li[1]/input').send_keys(email)
time.sleep(1)
driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/form/table/tbody/tr[1]/td/ol/li[2]/input').send_keys(password)
time.sleep(1)
driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/form/table/tbody/tr[1]/td/ol/li[5]/input').click()

time.sleep(5)

#now that we're logged in, we can search a company.

for company in company_dict.keys():
    driver.find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td[2]/div/form[2]/table/tbody/tr/td[1]/div[1]/div/input').send_keys(company)
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td[2]/div/form[2]/table/tbody/tr/td[2]/input').click()
    time.sleep(3)


    elems = driver.find_elements_by_xpath("//a[@href]")
    highest_fuzz = 0
    best_match_element = None
    best_match_text = ""
    for elem in elems:
        elemtext = elem.text.replace("/n","")
        elemtext = elemtext.replace("/t","")
        elemtext = elemtext.replace("  ","")
        elemtext = elemtext.replace("  ", "")
        try:
            elemtext = elemtext.split(" (")[0]
        except:
            pass

        if elemtext != "":
            if len(elemtext) >= len(company) - 3:
                ratio = fuzz.ratio(elemtext.lower(), company.lower())
                if ratio > highest_fuzz:
                    best_match_element = elem
                    best_match_text = elemtext
                    highest_fuzz = ratio

    print("best match to " + company + " was found to be " + best_match_text + " with a fuzz ratio of " + str(highest_fuzz))
    best_match_url = best_match_element.get_attribute("href")
    driver.get(best_match_url)
    time.sleep(2)
    reg20f = None
    annual_filing = None
    interim_report = None

    aeles = driver.find_elements(By.TAG_NAME, "a")
    for a in aeles:
        if a.get_attribute("title").find("20-F") != -1:
            print("found 20F filing")
            reg20f = a
        elif a.get_attribute("title").find("Annual") != -1:
            print("found latest annual report")
            annual_filing = a
        elif a.get_attribute("title").find("Interim") != -1:
            print("found latest interim report")
            interim_report = a
    
    if reg20f == None:
        if annual_filing == None:
            if interim_report == None:
                print("no reports found for " + company)

    base_doc_redirector_link = 'https://www.capitaliq.com/CIQDotNet/Filings/DocumentRedirector.axd?documentId='
    base_xls_redirector_link = 'https://www.capitaliq.com/CIQDotNet/Filings/DocumentRedirector.axd?versionId='
    if reg20f != None:
        docid = str(str(reg20f.get_attribute("href")).split("documentId=")[1].split("%")[0])
        driver.get(base_doc_redirector_link + docid)
        time.sleep(3)
        button_location = pyautogui.locateOnScreen('excel_icon.png')
        pyautogui.moveTo(button_location)
        time.sleep(2)
        pyautogui.click()
        time.sleep(.05)
        pyautogui.click()
        pathline_found = False
        while pathline_found == False:
            try:
                pl_location = pyautogui.locateOnScreen("pathline.png")
                pathline_found = True
            except:
                time.sleep(1)
                pyautogui.click()

        time.sleep(1)
        pyautogui.moveTo(pl_location)
        time.sleep(1)
        pyautogui.click()
        time.sleep(10)


