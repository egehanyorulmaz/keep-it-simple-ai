import pandas as pd
import numpy as np

from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup

CHROME_DRIVER_PATH = "/usr/bin/chromedriver"

class PDFDriveCrawler:
    """A class to crawl PDFDrive and download books."""

    def __init__(self, url: str):
        """Initialize the PDFDriveCrawler with the base URL."""
        self.base_url = url
        self.driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
        self.wait = WebDriverWait(self.driver, 10) # 10 seconds timeout
        self.promotion_appear_counter = 0
        self.start_crawling()

    # Public methods
    def start_crawling(self) -> None:
        """Open the base URL and maximize the window."""
        self.driver.get(self.base_url)
        self.driver.maximize_window()
        time.sleep(10)

    def check_and_pass_promotion(self, wait_time = 5) -> None:
        """Close the promotion pop-up if it appears."""
        wait = WebDriverWait(self.driver, 5)
        try:
            # Wait for the element to be visible
            element = wait.until(
                EC.presence_of_element_located([By.XPATH, "/html/body/div[3]/div[2]/div/div/div/i"]))
            # Click on the element
            element.click()
            print("Promotion pop-up passed")
        except:
            print("No promotion pop-up found")
        self.promotion_appear_counter += 1

    def search_book(self, book_name) -> None:
        """Search for a book by its name."""
        if self.promotion_appear_counter >= 3:
            self.driver.refresh()

        self.check_and_pass_promotion()
        self.driver.find_element(By.ID, "q").send_keys(book_name)
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/form/button").click()
        print(f'Entering book name {book_name}')

    def click_book_details(self, book_index=1) -> None:
        """Click on a book's details by its index."""
        self.check_and_pass_promotion()
        url = self.__get_book_hyperlink_by_position(book_index)
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'title')))
        print("Clicked on the book details")

    def click_download_button(self) -> None:
        """Click the download button for the current book."""
        url = self.__get_download_button_hyperlink()
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'title')))
        print("Clicked to download button")

    def download_book(self) -> None:
        """Download the current book."""
        self.check_and_pass_promotion()
        wait = WebDriverWait(self.driver, 20) # 10 seconds timeout
        url = self.__get_download_link()
        print(url)
        self.driver.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'title')))

    def check_book_file_type(self) -> bool:
        # TODO: check if the book is in PDF format
        """Check if the current book is in EPUB format."""
        soup = self.__get_soup(_type='html.parser')
        text = soup.get_text().strip()
        is_pdf = 'Download ( PDF )' in text
        return is_pdf
    
    def get_books_after_search(self) -> pd.DataFrame:
        """Get a DataFrame of the books after searching."""
        data_collection = {"title": [], "year": []}
        for position in range(1, 21):
            try:
                # Find the element using the full XPath expression
                element = self.driver.find_element(by=By.XPATH,
                                            value=f"/html/body/div[3]/div[1]/div[1]/div[4]/ul/li[{str(position)}]/div/div/div[2]/a/h2")

                # Get the text content of the element
                book_title = element.text

                # Find the element using the XPath expression
                element = self.driver.find_element(by=By.XPATH,
                                            value=f"/html/body/div[3]/div[1]/div[1]/div[4]/ul/li[{str(position)}]/div/div/div[2]/div/span[3]")

                # Get the text content of the element
                year = element.text

                data_collection["title"].append(book_title)
                data_collection["year"].append(year)
            except:
                pass
        
        df = pd.DataFrame(data_collection)
        return df

    def get_most_similar_title(self, df, book_name, threshold=0.3) -> int:
        """Return the index of the most similar book title in the DataFrame."""

        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        import string

        # Lowercase the year column
        df['title'] = df['title'].str.lower()

        # Remove stopwords and special characters from the year column
        stop_words = set(stopwords.words('english'))
        df['title'] = df['title'].apply(lambda x: ' '.join([word for word in word_tokenize(x) if word not in stop_words]))
        df['title'] = df['title'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))

        # Tokenize the input text
        input_tokens = set(word_tokenize(book_name.lower()))

        # Calculate the Jaccard distance for each title
        df['similarity'] = df['title'].apply(lambda x: len(set(word_tokenize(x.lower())) & input_tokens) / len(set(word_tokenize(x.lower())) | input_tokens))

        # Return the index of the first row with a distance above the threshold
        try:
            result_index = df.index[df['similarity'] > threshold].tolist()[0]
            if result_index >= 3:
                # if the filtered book is after the 3rd place, then it is not available
                return -1
            return result_index
        except:
            return -1

    def check_if_book_is_available(self, book_name):
        """Check if a book is available on the website."""
        df = self.get_books_after_search()
        idx = self.get_most_similar_title(book_name)

        if idx == -1:
            # book is not available on the website
            return 999
        else:
            # book is available on the website
            return idx

    # Private methods
    def __get_soup(self, _type='lxml') -> BeautifulSoup:
        """Return the BeautifulSoup object for the current page source."""
        # Parse the HTML source with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, _type)
        return soup

    def __get_html_source(self) -> str:
        """Return the HTML source of the current page."""
        html_source = self.driver.page_source
        return html_source

    def __get_the_first_book_hyperlink(self) -> str:
        """
        OUTDATED
        Return the hyperlink of the first book.
        """
        soup = self.__get_soup()
            # Find the 'a' tag with the class 'ai-search'
        a_tag = soup.find('a', class_='ai-search')

        # Extract the hyperlink from the 'a' tag
        hyperlink = a_tag['href']

        print(hyperlink)
        url = self.base_url + hyperlink
        return url

    def __get_book_hyperlink_by_position(self, book_index) -> str:
        """Return the hyperlink of the book at a given index."""
        soup = self.__get_soup()
        # Find the 'a' tag using the provided CSS selector
        CSS_SELECTOR = f"""body > div.dialog > div.dialog-main > div.dialog-left > div.files-new > ul > 
        li:nth-child({book_index+1}) > div > div > div.file-right > a"""

        a_tag = soup.select_one(CSS_SELECTOR)
        # Extract the href attribute from the 'a' tag
        hyperlink = a_tag['href']
        print("Book hyperlink is as follows:", hyperlink)

        url = self.base_url + hyperlink
        return url

    def __get_download_link(self) -> str:
        wait = WebDriverWait(self.driver, 20) # 10 seconds timeout

        # Wait for the button to be visible and clickable
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="btn btn-primary btn-user"]')))

        # Extract the hyperlink from the button
        hyperlink = button.get_attribute('href')
        print(hyperlink)

        return hyperlink

    def __get_download_button_hyperlink(self) -> str:
        """Return the hyperlink of the download button."""
        soup = self.__get_soup()
        # Find the 'a' tag with the id 'download-button-link'
        a_tag = soup.find('a', id='download-button-link')
        # Extract the href attribute from the 'a' tag
        hyperlink = a_tag['href']
            
        url = self.base_url + hyperlink
        return url

if __name__ == '__main__':
    # Path: pdf_drive_crawler/crawler.ipynb
    book_level = pd.read_csv('book_levels.csv')

    crawler = PDFDriveCrawler("https://www.pdfdrive.com/")
    for book_name in list(book_level["title"]):
        crawler.search_book(book_name)
        books = crawler.get_books_after_search()
        idx = crawler.get_most_similar_title(df=books, book_name=book_name)
        if idx == -1:
            # book doesn't exist
            continue
        crawler.click_book_details(book_index=idx)
        crawler.click_download_button()
        crawler.check_book_file_type()
        crawler.download_book()
        time.sleep(10)