import pandas as pd
import numpy as np

from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from bs4 import BeautifulSoup

class PDFDriveCrawler:
    """Class to crawl PDFDrive and download books"""

    def __init__(self, url: str):
        self.base_url = url
        self.driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver' )
        self.wait = WebDriverWait(self.driver, 10) # 10 seconds timeout

    ### CONTROL FUNCTIONS ###
    def pass_promotion(self):
        element = self.driver.find_element(by=By.XPATH, value="/html/body/div[3]/div[2]/div/div/div/i")
        # Click on the element
        element.click()

    def check_and_pass_promotion(self):
        for i in range(5):
            try:
                # Wait for the element to be visible
                element = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, f"/html/body/div[3]/div[{i}]/div/div/div/i"))
                )
                # Click on the element
                element.click()
                
            except:
                pass

    def search_book(self, driver, book_name):
        self.check_and_pass_promotion()
        driver.find_element(By.ID, "q").send_keys(book_name)
        driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/form/button").click()
        print(f'Entering book name {book_name}')

    def click_book_details(self):
        self.check_and_pass_promotion()

        url = self.get_the_first_book_hyperlink()
        self.driver.get(url)

        # Wait for the page's title to be present
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'title')))

        print("Clicked on the book details")
    
    def get_the_first_book_hyperlink(self):
        soup = self.get_soup()
        
        # Find the 'a' tag with the class 'ai-search'
        a_tag = soup.find('a', class_='ai-search')

        # Extract the hyperlink from the 'a' tag
        hyperlink = a_tag['href']

        print(hyperlink)
        url = self.base_url + hyperlink
        return url
    
    def get_download_link(self):
        wait = WebDriverWait(self.driver, 20) # 10 seconds timeout

        # Wait for the button to be visible and clickable
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="btn btn-primary btn-user"]')))

        # Extract the hyperlink from the button
        hyperlink = button.get_attribute('href')
        print(hyperlink)

        return hyperlink

    def download_book(self):
        self.check_and_pass_promotion()
        wait = WebDriverWait(self.driver, 20) # 10 seconds timeout

        # Get the entire HTML source of the current page
        url = self.get_download_link()

        print(url)
        self.driver.get(url)

        # Wait for the page's title to be present
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'title')))

    def check_book_file_type(self):
        soup = self.get_soup(_type='html.parser')
        text = soup.get_text().strip()

        is_epub = 'EPUB' in text
        return is_epub
    
    def get_soup(self, _type='lxml'):
        """Get the soup of the page"""
        # Parse the HTML source with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, _type)
        return soup


    def get_html_source(self):
        """Get the html source of the page"""
        html_source = self.driver.page_source
        return html_source
