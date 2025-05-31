import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from src.hosts.Host import Host
from src.hosts.Host import MAX_WAIT_TIMES



class Ddownload:
    def __init__(self, glv, user):
        self.glv = glv
        self.user = user
        self.home_page = "https://ddownload.com"
        self.upload_page = f'{self.home_page}/?op=upload_form'

        self.host = Host(self)

    def login(self, account=None):
        user = account if account else self.user
        self.host.login(user)

    def upload(self, files):
        self.glv.log(f'Start uploading on {self.home_page}')

        self.login(self.user)

        self.glv.driver.get(self.upload_page)

        file_str = '\n'.join(files)

        self.glv.get_element('id', 'file_0').send_keys(file_str)
        self.glv.sleep(3)

        js = "$('input[value=\"Upload\"]').last().click()"
        self.glv.run_js(js)

        source = self.glv.driver.page_source
        times = 0
        max_times = len(files) * MAX_WAIT_TIMES
        while 'Upload Results' not in source and times < max_times:
            try:
                WebDriverWait(self.glv.driver, 6).until(EC.alert_is_present())
                alert = self.glv.driver.switch_to.alert
                alert.accept()
                self.upload(files)
            except TimeoutException:
                pass

            if times > 0:
                sys.stdout.write("\r")
                sys.stdout.write("Uploading for {:2d} seconds\n".format(times * 6))
                sys.stdout.flush()

            times += 1

            source = self.glv.driver.page_source

            if times == max_times:
                self.glv.log('Not uploaded after {} min.'.format(max_times / 10), 'error')
                self.glv.quit()

        textarea = self.glv.get_element('id', 's-links')

        text = textarea.get_attribute("value").strip()

        urls = text.split('\n')

        self.glv.log('Successfully uploaded {} files'.format(len(files)))

        return urls

    def check_links(self, link_sets):
        return self.host.check_links(link_sets)
