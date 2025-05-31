import os
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import chromedriver_autoinstaller

load_dotenv()

class DriverProxy:
    def __init__(self):
        self._thread_local = threading.local()

    def __getattr__(self, name):
        driver = getattr(self._thread_local, 'driver', None)
        if driver is None:
            raise AttributeError("Driver not initialized for this thread")
        return getattr(driver, name)

    def initialize(self, headless, home, download_path):
        if 'root' in home or os.getenv('REMOTE_USERNAME') in home:
            fp = webdriver.FirefoxProfile()
            fp.set_preference("browser.download.folderList", 2)
            fp.set_preference("browser.download.manager.showWhenStarting", False)
            fp.set_preference("browser.download.dir", download_path)
            fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                              "application/x-rar-compressed, application/octet-stream, application/zip,\
                               application/octet-stream, application/x-zip-compressed")

            self._thread_local.driver = webdriver.Firefox(executable_path=home + '/bin/geckodriver', firefox_profile=fp)
            self._thread_local.driver.set_window_size(800, 600)
        else:
            options = Options()
            options.add_experimental_option("prefs", {
                "download.default_directory": download_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            })

            if headless:
                options.add_argument('--headless')

            options.add_argument('--safebrowsing-disable-download-protection')

            chromedriver_autoinstaller.install()
            self._thread_local.driver = webdriver.Chrome(options=options)

    def quit(self):
        driver = getattr(self._thread_local, 'driver', None)
        if driver:
            driver.quit()
            del self._thread_local.driver
