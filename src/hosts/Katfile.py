import sys
import requests

from src.hosts.Host import Host
from src.hosts.Host import MAX_WAIT_TIMES


class Katfile:

    def __init__(self, glv, user):
        self.glv = glv
        self.home_page = "https://katfile.com"
        self.user = user
        self.api_key = self.user['api']

        self.host = Host(self)

    def login(self, account=None):
        user = account if account else self.user
        self.host.login(user)

    def upload(self, files):
        self.login()

        self.glv.log('Starting upload')

        self.glv.driver.get(f'{self.home_page}/?op=upload')

        file_str = '\n'.join(files)

        self.glv.get_element('id', 'file_0').send_keys(file_str)
        self.glv.sleep(3)

        js = "$('input[value=\"Start upload\"]').last().click()"
        self.glv.run_js(js)

        source = self.glv.driver.page_source
        times = 0
        max_times = len(files) * MAX_WAIT_TIMES
        while 'Files Uploaded' not in source and times < max_times:
            if times > 0:
                sys.stdout.write("\r")
                sys.stdout.write("Uploading for {:2d} seconds\n".format(times * 6))
                sys.stdout.flush()
            self.glv.sleep(6)

            times += 1

            source = self.glv.driver.page_source

        if times == max_times:
            self.glv.log('Not uploaded after {} min.'.format(max_times / 10), 'error')
            self.glv.quit()

        textarea = self.glv.get_element('xpath', '//*[@id="container"]/div/div[2]/div/div[1]/textarea')

        text = textarea.get_attribute("value").strip()

        urls = text.split('\n')

        self.glv.log('Successfully uploaded {} files'.format(len(files)))

        return urls

    #deprecated use upload instead
    def api_upload(self, files):
        urls = []

        for file in files:
            print(f"Starting next upload: {file}")

            # First HTTP request
            upload_context = requests.get(f"{self.home_page}/api/upload/server?key={self.api_key}").json()
            print(f"Got next available file server: {upload_context['result']}")

            postfields = {
                "sess_id": upload_context['sess_id'],
                "utype": "prem",
                "fld_path": "",
                "file_0": open(file, 'rb'),
            }

            # Second HTTP request
            print("Uploading...")
            response = requests.post(upload_context['result'], files=postfields)
            ret = response.text
            print(f"Got from upload.cgi: {ret}")

            return self.web_upload([file])

        return urls

    def check_links(self, link_sets):
        return self.host.check_links(link_sets)
