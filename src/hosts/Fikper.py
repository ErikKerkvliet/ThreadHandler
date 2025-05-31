import sys

from src.hosts.Host import Host
from src.hosts.Host import MAX_WAIT_TIMES


class Fikper:
    def __init__(self, glv, user):
        self.glv = glv
        self.user = user
        self.file_urls = None
        self.home_page = "https://fikper.com"
        self.host = Host(self)

    def login(self, account=None):
        user = account if account else self.user

        self.glv.driver.get(self.home_page)

        if 'login' not in self.glv.driver.page_source.lower():
            return

        self.glv.driver.get(f'{self.home_page}/login')

        login_field = self.glv.get_elements('name', 'email', 1, 0, True)

        login_field.send_keys(user['email'])

        password_field = self.glv.get_elements('name', 'password', 1, 0, True)

        password_field.send_keys(user['password'])

        times = 0
        max_times = 300
        while 'used space' not in self.glv.driver.page_source.lower() or times > max_times:
            times += 1
            self.glv.sleep(6)

        self.glv.sleep(1)

        if times > max_times:
            self.glv.log('Login failed')

        self.glv.log('Login successful')

    def upload(self, files):
        self.file_urls = []
        to_upload = files.copy()
        self.login(self.user)

        self.glv.log(f'Start uploading on {self.home_page}')

        self.glv.driver.get(f'{self.home_page}/files')

        file_input = self.glv.get_element('id', 'contained-button-file')

        for file in files:
            self.upload_file(file_input, file)
            try:
                to_upload.remove(file)
            except:
                pass

        self.glv.sleep(5)

        return self.get_urls(files, to_upload)

    def upload_file(self, file_input, file):
        file_input.send_keys(file)
        times = 0
        self.glv.sleep(5)

        while len(self.glv.get_elements('class', 'css-gh7u6a')) >= 1 and times < MAX_WAIT_TIMES:
            if 'there was an error' in self.glv.get_source().lower():
                self.glv.log('An error occurred', 'error')
                self.upload_file(file_input, file)

            if times > 0:
                sys.stdout.write("\r")
                sys.stdout.write("Uploading for {:2d} seconds\n".format(times))
                sys.stdout.flush()

            times += 1
            self.glv.sleep(2)

        if times >= MAX_WAIT_TIMES:
            self.glv.log('File not downloaded, took too long', 'error')
            self.glv.quit()

    def get_urls(self, paths, to_upload):
        file_names = []
        for path in paths:
            file_names.append(self.get_key(path))

        file_page = f'{self.home_page}/files'

        self.glv.driver.get(file_page)

        self.glv.sleep(4)

        links_element = self.glv.get_elements('class', 'inovua-react-virtual-list__view-container', 1, 0, True)

        url_elements = self.glv.get_element_in_element(links_element, 'tag', 'a')
        urls = {}
        for element in url_elements:
            href = element.get_attribute('href')
            urls[self.get_key(href)] = href

        for key in urls.keys():
            for file_name in file_names:
                if file_name in key:
                    self.file_urls.append(urls[key])

        return self.upload(to_upload) if to_upload != [] else self.file_urls

    def get_key(self, string):
        split = string.split('/')[-1].split('.')
        return split[0].replace(' ', '_') + split[1]

    def check_links(self, link_sets):
        return self.host.check_links(link_sets)
