from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BaseCrawler:

    def __init__(self, browser="chrome_headless"):
        self.main_wrapper_locator = ""
        if browser == "chrome_headless":
            driver_dir = './drivers/chromedriver_3'
            chrome_options = self.__set_chrome_options()
            self.driver = webdriver.Chrome(options=chrome_options)# ,
                                           #executable_path=driver_dir)

    def __set_chrome_options(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage') ##heroku
        chrome_options.add_argument('--verbose')
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": "",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
        })
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')

        return chrome_options

    def close_connection(self): 
        self.driver.close()

    def access_url(self, articleUrl):
        self.driver.get(articleUrl)

    def wait_and_set_main_wrapper(self, main_wrapper_locator):
        self.main_wrapper_locator = main_wrapper_locator
        self.currentWrapper = WebDriverWait(self.driver, 6).until(EC.visibility_of_element_located(self.main_wrapper_locator))