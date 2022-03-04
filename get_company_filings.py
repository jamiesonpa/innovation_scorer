from turtle import down
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os
import time
from datetime import date
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import numpy as np
from matplotlib import pyplot as plt
import pyautogui
import config

#to run this script you're going to need to have chromedriver.exe in your local path. https://sites.google.com/chromium.org/driver/downloads
#you also need a list of companies to search that are in a .txt file where the format is 
#example:
    #company1,country
    #company2,country
    #company3,country
    #....
#and you have to make sure that the company names in this file have no commas in them because the comma is used as the delimiter here.

#create a local directory called "filings" that specifies where you will download the filings to

#last things you need are the png files that are the icons for the excel and pdf files you need to click on for the last step.

#first get a list of companies and get them into a dict where they key:value pairings is company name:country

with open("international_companies.txt") as readfile:
    companies = readfile.read().split("/n")

company_dict = {}
for company in companies:
    company_name = company.split(",")[0]
    company_location = company.split(",")[1]
    company_dict[company_name] = company_location

#now log into capiq


#use these headers and driver options to make your requests look like they're not from a bot.
hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36","X-Requested-With": "XMLHttpRequest"}
driverPath = os.getcwd() +"/chromedriver.exe"
options = webdriver.ChromeOptions()

options.add_argument('--no-sandbox')
options.add_argument('--disable-setuid-sandbox')
options.add_argument("--proxy-server='direct://")
options.add_argument('--proxy-bypass-list=*')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-accelerated-2d-canvas')
options.add_argument("--log-level=3")
options.add_argument('--disable-gpu')
options.add_argument("start-maximized")
options.add_argument("-incognito")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

#set the max number of seconds to wait for pages to load
delay = 10

#use this to determin"e where you're going to download the company filings and reports
downloads_directory = "filings"
cwd = os.getcwd()
try:
    default_download_path = os.path.join(cwd, downloads_directory)
except:
    print("ERROR: NO FILINGS DIRECTORY TO SERVE AS DOWNLOAD LOCATION IN YOUR LOCAL PATH")
    default_download_path = os.getcwd()

prefs = {"download.default_directory" : default_download_path}
options.add_experimental_option("prefs",prefs)

#instantiate the webdriver
driver = webdriver.Chrome(options=options, executable_path=os.getcwd()+"/chromedriver.exe")

#change these to your capiq login info
email = config.capiq_email
password = config.capiq_password
url = 'https://www.capitaliq.com/'

#open capiq with the webdriver
driver.get(url)


#now log into capiq
username_input = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div[1]/form/table/tbody/tr[1]/td/ol/li[1]/input'))).send_keys(email)
driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/form/table/tbody/tr[1]/td/ol/li[2]/input').send_keys(password)
time.sleep(1)
driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/form/table/tbody/tr[1]/td/ol/li[5]/input').click()

#now that we're logged in, we can search a company.
search_bar_input = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/table/tbody/tr/td[2]/div/form[2]/table/tbody/tr/td[1]/div[1]/div/input')))

#this searches the company in the searchbar
for company in company_dict.keys():
    driver.find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td[2]/div/form[2]/table/tbody/tr/td[1]/div[1]/div/input').send_keys(company)
    time.sleep(.3)
    driver.find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td[2]/div/form[2]/table/tbody/tr/td[2]/input').click()

    #now wait for the list of search results to populate
    company_table = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr[2]/td[4]/div/form/table')))

    #once it has loaded, find all of the links in the page and extract the text from them
    elems = driver.find_elements_by_xpath("//a[@href]")

    #search all of these elements and filter out the ones that aren't in the search results table
    filtered_elems = []
    for elem in elems:
        if str(elem.get_attribute("href")).find("CompanySearchResultRow") != -1:
            filtered_elems.append(elem)


    highest_fuzz = 0
    best_match_element = None
    best_match_text = ""

    #clean the first ten elements
    for elem in filtered_elems[0:10]:
        elemtext = elem.text.replace("/n","")
        elemtext = elemtext.replace("/t","")
        elemtext = elemtext.replace("  ","")
        elemtext = elemtext.replace("  ", "")
        try:
            elemtext = elemtext.split(" (")[0]
        except:
            pass

        #now use fuzzy text matching to see how close that link text is to the company name in question
        if elemtext != "":
            if len(elemtext) >= len(company) - 3:
                ratio = fuzz.ratio(elemtext.lower(), company.lower())
                if ratio > highest_fuzz:
                    best_match_element = elem
                    best_match_text = elemtext
                    highest_fuzz = ratio
                
    #print the best match for logging purposes
    print("best match to " + company + " was found to be " + best_match_text + " with a fuzz ratio of " + str(highest_fuzz))

    #get the url from that link
    best_match_url = best_match_element.get_attribute("href")

    #now go to that link
    driver.get(best_match_url)

    reg20f = None
    annual_filing = None
    interim_report = None

    #now wait for the company header to load
    company_header = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr[2]/td[4]/div/form/div[3]')))

    #once it is loaded, get all of the "a" tags from the page and find the ones that hold the 20-f, Annual, and Interim reports

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
    
    #check to see that we found at least one report
    no_reports_found = False
    if reg20f == None:
        if annual_filing == None:
            if interim_report == None:
                print("no reports found for " + company)
                no_reports_found = True
    
    #now, if we found at least one report, proceed

    if no_reports_found == False:
        base_doc_redirector_link = 'https://www.capitaliq.com/CIQDotNet/Filings/DocumentRedirector.axd?documentId='
        base_xls_redirector_link = 'https://www.capitaliq.com/CIQDotNet/Filings/DocumentRedirector.axd?versionId='

        #get the 20F if it's there
        if reg20f != None:
            docid = str(str(reg20f.get_attribute("href")).split("documentId=")[1].split("%")[0])
            driver.get(base_doc_redirector_link + docid)
            filing_header = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '/html/frameset')))
            button_location = pyautogui.locateOnScreen('excel_icon.png')
            pyautogui.moveTo(button_location)
            #check to see the number of files in your download directory
            current_downloads_directory = os.listdir(downloads_directory)
            print("files in download directory found to be "+ str(len(current_downloads_directory)))
            
            time.sleep(.2)
            pyautogui.click()
            time.sleep(.05)
            pyautogui.click()



            #wait for files to show up that are .tmp or .crdownload to exist in the filings directory
            downloading_files = False
            while downloading_files == False:
                files_downloading = 0
                for file in os.listdir(downloads_directory):
                    if str(file).find(".tmp") != -1:
                        files_downloading += 1
                    if str(file).find(".crdownload") != -1:
                        files_downloading += 1
                if files_downloading == 0:
                    downloading_files = True


            #now check to see that there is a new file there at all
            new_file_detected = False
            while new_file_detected == False:
                new_downloads_directory = os.listdir(downloads_directory)
                if current_downloads_directory != new_downloads_directory:                
                    print("newly downloaded file detected in the downloads directory")
                    new_file_detected = True
                else:
                    time.sleep(.1)

            #now wait for them to go away
            while downloading_files == True:
                files_downloading = 0
                for file in os.listdir(downloads_directory):
                    if str(file).find(".tmp") != -1:
                        files_downloading += 1
                    if str(file).find(".crdownload") != -1:
                        files_downloading += 1
                if files_downloading == 0:
                    downloading_files = False
                time.sleep(0.1)

            #now check to see the name of that file
            new_file = None
            for file in new_downloads_directory:
                if file not in current_downloads_directory:
                    new_file = file
            
            time.sleep(2)
            company_name_edited = company_name.replace(" ","_")
            os.rename(new_file.replace(".crdownload",""),company+"_20F.xls")
            time.sleep(2)


