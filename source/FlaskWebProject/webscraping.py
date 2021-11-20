
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import zipfile
import shutil

#from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager


account_user = "thomas12roberts@gmail.com"
# Fake/non personal password:
account_pass = "plaintext"

human_handling_mode = False

already_downloaded_ids = []

def unzip_files(download_folder):
    completed=[]
    for filename in os.listdir(download_folder):
        if filename.endswith(".zip"):
            ethos_id = filename.split('_')[0]
            if os.path.isfile(download_folder + "\\" + ethos_id + ".pdf"):
                print("Skipping unpack of: " + ethos_id)
                continue
            zipdata = zipfile.ZipFile(download_folder + "\\" + filename )
            zipinfos = zipdata.infolist()
            shutil.unpack_archive(download_folder + "\\" + filename, download_folder)
            largest_size = -1
            largest_sized_id = 0
            ## Choose largest file to unpack:
            for i, zipinfo in enumerate(zipinfos):
                if zipinfo.compress_size > largest_size and zipinfo.filename.endswith(".pdf"):
                    largest_size = zipinfo.compress_size
                    largest_sized_id = i
            if largest_size == -1:
                print("\n\n\nWARNING!! NO PDF FOUND\n\n\n")
                continue
            if len(zipinfos) > 1:
                for i, zipinfo in enumerate(zipinfos):
                    if i != largest_sized_id:
                        os.remove(download_folder + "\\" + zipinfo.filename)
            os.rename(download_folder + "\\" + zipinfos[largest_sized_id].filename, download_folder + "\\" + ethos_id + ".pdf")
            completed.append(download_folder + "\\" + filename)



def scrape(search_text, max_pages, download_folder):
    global already_downloaded_ids
    for filename in os.listdir(download_folder):
        if filename.endswith(".zip"):
            already_downloaded_ids.append(filename.split('_')[0])
        if filename.endswith(".pdf"):
            already_downloaded_ids.append(filename.split('.')[0])

    scraper = ScrapeSpider(download_folder)
    search_text_list = search_text.split(",")
    downloaded_ids, pdf_names = scraper.start_requests(search_text_list, max_pages)
    print("Waiting 3 seconds for downloads to complete...")
    time.sleep(3)
    unzip_files(download_folder)
    for i in range(len(downloaded_ids)):
        f= open(download_folder + "\\" + downloaded_ids[i] + ".txt","w", encoding="utf-8")
        f.write(pdf_names[i])

    for filename in os.listdir(download_folder):
        if filename.endswith(".zip"):
            try:
                os.remove(download_folder + "\\" + filename)
            except OSError:
                continue
    return downloaded_ids

class ScrapeSpider():

    def __init__(self, download_location):
        self.driver = webdriver.Chrome()
        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory' : download_location}
        chrome_options.add_experimental_option('prefs', prefs)
        self.login_driver = webdriver.Chrome(chrome_options=chrome_options)


    def start_requests(self, search_text_list, max_pages):

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

       
        sel.get("https://ethos.bl.uk/AdvancedSearch.do")
        add_button  = sel.find_element_by_id("newSearchRowId")
        add_button.click()
        time.sleep(0.2)
        add_button  = sel.find_element_by_id("newSearchRowId")
        add_button.click()
        time.sleep(0.2)
        add_button  = sel.find_element_by_id("newSearchRowId")
        add_button.click()
        time.sleep(0.2)
        checkbox = sel.find_element_by_id("chk1")
        checkbox.click()
        
        search_amount = len(search_text_list)
        if search_amount > 6:
            search_amount = 6
        for i in range(search_amount):
            box_id = "advancedQueryStringValue" + str(i+1)
            text_search = search_text_list[i]
            searchElement = sel.find_element_by_id(box_id)
            searchElement.send_keys(text_search)

        if human_handling_mode:
            time.sleep(15)
        go_button  = sel.find_element_by_id("processAdvancedSearchButton")
        go_button.click()

        current_page = 1
        id_list = []
        names_list = []

        while current_page <= max_pages:
            urls = []
            elements = sel.find_elements_by_xpath("//a[@class='title ui-button-text']")
            for el in elements:
                thesis_url = el.get_attribute("href")
                thesis_name = el.find_element_by_class_name("title").text
                urls.append((thesis_url,thesis_name))

            for url in urls:
                print("Starting parser for: " + str(url[0]))
                new_id = self.sync_parse(url[0])
                if new_id is not None:
                    id_list.append(new_id)
                    pdf_name = "test"
                    names_list.append(url[1])
                #yield scrapy.Request(url=url, callback=self.parse)
        
            end_elements = sel.find_elements_by_xpath("//span[@class='ui-icon ui-icon-seek-end ']")
            if len(end_elements) == 0:
                # No results found
                break
            link_to_end = end_elements[0].find_element_by_xpath('..').get_attribute("href")
            if link_to_end is None or len(link_to_end) <= 1:
                # End is found
                break
            current_page += 1
            sel.get("https://ethos.bl.uk/ProcessSearchUpdate.do?page=" + str(current_page))
            time.sleep(0.5)


        sel.close()
        sel_logged.close()
        print("Finished scraping.")
        return id_list, names_list

    def sync_parse(self, url):
        global already_downloaded_ids
        ethos_id = url.split(".")[-1]
        print("ETHOS ID: " + str(ethos_id))
        if ethos_id in already_downloaded_ids:
            print("SKIPPING: " + ethos_id)
            return ethos_id
        sel = self.login_driver
        new_url = "https://ethos.bl.uk/OrderDetails.do?uin=uk.bl.ethos." + str(ethos_id)
        sel.get(new_url)

        sel.implicitly_wait(1)
        access_button = sel.find_elements_by_class_name("access-btn")
        sel.implicitly_wait(5)
        if len(access_button) == 0:
            if human_handling_mode:
                print("NO ACCESS FOUND FOR "+ ethos_id +", URL: " + str(new_url))
                print()
                return ethos_id
            return None
        access_button[0].click()
        terms_check = sel.find_element_by_id("termsCheck")
        terms_check.click()
        download_selectors = sel.find_elements_by_name("selectedItems")
        for el in download_selectors:
            el.click()
        download_button = sel.find_element_by_class_name("download-button")
        download_button.click()
        return ethos_id
