
import sys

from src.hosts.Host import Host
from src.hosts.Host import MAX_WAIT_TIMES


class Mexashare:

    def __init__(self, glv, user):
        self.glv = glv
        self.user = user
        self.home_page = "https://mexa.sh"

        self.host = Host(self)

    def start(self):
        self.login(self.user)

    def login(self, account=None):
        user = account if account else self.user
        self.host.login(user)

    def upload(self, files):
        self.login()
        self.glv.driver.get(self.home_page)

        self.glv.log(f'Start uploading on {self.home_page}')

        file_str = '\n'.join(files)

        self.glv.get_element('id', 'file_0').send_keys(file_str)
        self.glv.sleep(3)

        js = "$('input[value=\"Start upload\"]').last().click()"
        self.glv.run_js(js)

        source = self.glv.driver.page_source
        times = 0
        max_times = len(files) * MAX_WAIT_TIMES
        while 'The Uploaded Files' not in source and times < max_times:
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

        textarea = self.glv.get_element('id', 'ic0-')

        text = textarea.get_attribute("value").strip()

        urls = text.split('\n')

        self.glv.log('Successfully uploaded {} files'.format(len(files)))

        return urls

    def check_links(self, link_sets):
        files = []

        self.glv.log(f'Checking links on {self.home_page}')

        for key in link_sets.keys():
            for link in link_sets[key]:
                files.append(link)

        if len(files) == 0:
            self.glv.log('No links are given')
            return False

        self.glv.driver.get('https://mexa.sh/?op=checkfiles')

        urls = '\\n'.join(files)

        js = f"$('textarea[name=\"list\"').html('{urls}')"
        self.glv.run_js(js)

        js = f"$('input[name=\"process\"').click()"
        self.glv.run_js(js)

        if 'Not found' in self.glv.driver.page_source:
            self.glv.log('Not all files are found')
            return False

        self.glv.log(f'Files all found')
        return True
