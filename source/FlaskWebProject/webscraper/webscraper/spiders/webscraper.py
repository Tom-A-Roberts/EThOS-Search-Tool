
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
import time

#from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager


account_user = "thomas12roberts@gmail.com"
account_pass = "plaintext"

search_text = "python"
max_pages = 1

already_downloaded_ids = []

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.login_driver = webdriver.Chrome()

    def start_requests(self):

        sel = self.driver
        sel_logged = self.login_driver

        sel.implicitly_wait(10)
        sel_logged.implicitly_wait(10)

        sel_logged.get("https://ethos.bl.uk/Logon.do")
        inputElement1 = sel_logged.find_element_by_name("username")
        inputElement1.send_keys(account_user)
        inputElement2 = sel_logged.find_element_by_name("password")
        inputElement2.send_keys(account_pass)
        inputElement2.submit()

        time.sleep(0.3)
        sel.get("https://ethos.bl.uk/Home.do?new=1")
        checkbox = sel.find_element_by_id("chk1")
        checkbox.click()
        searchElement = sel.find_element_by_name("query")
        searchElement.send_keys(search_text)
        searchElement.submit()

        current_page = 1

        while current_page <= max_pages:
            urls = []
            elements = sel.find_elements_by_xpath("//a[@class='title ui-button-text']")
            for el in elements:
                thesis_url = el.get_attribute("href")
                urls.append(thesis_url)
            for url in urls:
                print("Starting parser for: " + str(url))
                self.sync_parse(url)
                #yield scrapy.Request(url=url, callback=self.parse)
        
            end_elements = sel.find_elements_by_xpath("//span[@class='ui-icon ui-icon-seek-end ']")
            if len(end_elements) == 0:
                # No results found
                break
            link_to_end = end_elements[0].find_element_by_xpath('..').get_attribute("href")
            if len(link_to_end) <= 1:
                # End is found
                break
            current_page += 1
            sel.get("https://ethos.bl.uk/ProcessSearchUpdate.do?page=" + str(current_page))
            time.sleep(0.5)


        sel.close()
        sel_logged.close()
        print("Finished scraping.")

    def sync_parse(self, url):
        ethos_id = url.split(".")[-1]
        print("ETHOS ID: " + str(ethos_id))
        sel = self.login_driver
        new_url = "https://ethos.bl.uk/OrderDetails.do?uin=uk.bl.ethos." + str(ethos_id)
        sel.get(new_url)

        sel.implicitly_wait(1)
        access_button = sel.find_elements_by_class_name("access-btn")
        sel.implicitly_wait(5)
        if len(access_button) == 0:
            return None
        access_button[0].click()
        terms_check = sel.find_element_by_id("termsCheck")
        terms_check.click()
        download_selectors = sel.find_elements_by_name("selectedItems")
        for el in download_selectors:
            el.click()
        download_button = sel.find_element_by_class_name("download-button")
        download_button.click()

