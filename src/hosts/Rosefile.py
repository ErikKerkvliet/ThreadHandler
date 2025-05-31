import sys
from src.hosts.Host import Host
from src.hosts.Host import MAX_WAIT_TIMES


class Rosefile:
    def __init__(self, glv, user):
        self.glv = glv
        self.user = user
        self.home_page = "https://rosefile.net"
        self.host = Host(self)

    def login(self, account=None):
        user = account if account else self.user

        self.glv.driver.get(self.home_page)

        if 'login' not in self.glv.driver.page_source.lower():
            return

        login_page = f'{self.home_page}/account.php?action=login'

        self.glv.driver.get(login_page)

        # login_field = self.glv.get_elements('name', 'username', 1, 0, True)
        #
        # login_field.send_keys(user['username'])
        #
        # password_field = self.glv.get_elements('name', 'password', 1, 0, True)
        #
        # password_field.send_keys(user['password'])
        #
        # submit_form = self.glv.get_elements('tag', 'form', 1, 0, True)
        #
        # if submit_form:
        #     submit_form.submit()

        self.glv.sleep(20)

        self.glv.log('Login successful')

    def upload(self, files):
        self.login(self.user)

        self.glv.log(f'Start uploading on {self.home_page}')

        self.glv.driver.get(f'{self.home_page}/mydisk.php?item=profile&menu=upload&action=upload')

        self.glv.sleep(1)

        iframe = self.glv.get_elements('class', 'embed-responsive-item', 1, 0, True)

        upload_page = iframe.get_attribute('src')

        self.glv.driver.get(upload_page)

        inputs = self.glv.get_elements('tag', 'input')
        file_input = None
        for element in inputs:
            if element.get_attribute('type') == 'file' and element.get_attribute('multiple') == 'true':
                file_input = element
                break

        if file_input:
            file_str = '\n'.join(files)
            file_input.send_keys(file_str)
            self.glv.sleep(2)

        upload_button = self.glv.get_elements('class', 'uploader-btn-start', 1, 0, True)

        upload_button.click()

        self.glv.sleep(3)

        times = 0
        max_times = len(files) * MAX_WAIT_TIMES
        source = self.glv.driver.page_source.lower()
        while ('queue' in source or 'append' in source or 'kb/' in source or 'mb/' in source or 'gb/' in source) and times < max_times:
            if times > 0:
                sys.stdout.write("\r")
                sys.stdout.write("Downloading for {:2d} seconds\n".format(times * 6))
                sys.stdout.flush()
            self.glv.sleep(6)

            source = self.glv.driver.page_source.lower()
            times += 1

        if times == max_times:
            self.glv.log('File not downloaded, took too long', 'error')
            self.glv.quit()

        return self.get_urls(files)

    def get_urls(self, paths):
        file_names = []
        for path in paths:
            file_names.append(self.get_key(path))

        file_page = f'{self.home_page}/mydisk.php?item=profile&menu=file&action=files'

        self.glv.sleep(5)

        self.glv.driver.get(file_page)

        self.glv.sleep(2)

        links_divs = self.glv.get_elements('class', 'file_url')

        urls = {}
        for element in links_divs:
            url_element = self.glv.get_element_in_element(element, 'tag', 'a', True)

            href = url_element.get_attribute('href')
            urls[self.get_key(href)] = href

        file_urls = []
        for key in urls.keys():
            for file_name in file_names:
                if file_name in key:
                    file_urls.append(urls[key])

        return file_urls

    @staticmethod
    def get_key(string):
        split = string.split('/')[-1].split('.')
        return split[0].replace(' ', '_') + split[1]

    def check_links(self, link_sets):
        return self.host.check_links(link_sets)
