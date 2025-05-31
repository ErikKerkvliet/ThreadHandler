import sys


class Rapidgator:

    def __init__(self, glv):
        self.glv = glv
        self.home_page = "https://rapidgator.net"
        self.user = self.glv.get_account('rapidgator', 0)

    # login on to rapidgator.net
    def login(self, account=None):
        user = account if account else self.user
        self.glv.log('Log into https://rapidgator.net')

        url = 'https://rapidgator.net'
        self.glv.driver.get(url)

        self.glv.sleep(2)
        # get all links on the page
        elements = self.glv.get_elements('tag', 'a')

        # check if a profile related link exists. If so: The logging in can be stopped
        for element in elements:
            text = element.get_attribute('innerHTML')
            if text == 'Login':
                element.click()
                break
            if element.get_attribute('innerHTML').strip(' ') == 'My account':
                print('Already logged in on to rapidgator.net')

                return

        self.glv.sleep(1, 2)

        inputs = self.glv.get_elements('tag', 'input')

        for input_field in inputs:
            if input_field.get_attribute('id') == 'LoginForm_email':
                input_field.clear()
                input_field.send_keys(user['username'])
            if input_field.get_attribute('id') == 'LoginForm_password':
                input_field.clear()
                input_field.send_keys(user['password'])

        self.glv.sleep(2, 3)

        self.glv.run_js("document.forms.registration.submit();")

        self.glv.sleep(1, 2)

        self.glv.log('Login successful')

    def download(self, links_set, comment):
        self.login()
        path = self.glv.downloadPath.split('source/')[-1]
        self.glv.log(f'Downloading file(s) to: ./{path}')

        files = []
        for link in links_set[comment]:
            self.glv.sleep(1, 2)
            files.append(self.download_link(link, comment))

            self.glv.downloads[comment] = files
        self.glv.log('Downloads successful')

    def download_link(self, link, comment):
        self.glv.log(link)

        self.glv.driver.get(link)
        current_files = self.glv.get_folder_content(self.glv.downloadPath)

        times = 0
        downloaded_finished = False
        files = []
        while not downloaded_finished and times < 100:
            if times > 0:
                sys.stdout.write("\r")
                sys.stdout.write("Downloading for {:2d} seconds\n".format(times * 6))
                sys.stdout.flush()
            self.glv.sleep(6)
            times += 1

            files = self.glv.get_folder_content(self.glv.downloadPath)

            finished = 0
            for file in files:
                if 'unconfirmed' not in file.lower():
                    finished += 1

            if len(files) == finished and len(files) > 0:
                downloaded_finished = True

        if times == 50:
            self.glv.log('File not downloaded after 10 minutes', 'error')
            self.glv.quit()
        else:
            for file in files:
                if file not in current_files:
                    return f'{self.glv.downloadPath}/{file}'

    def check_links(self, link_sets):
        account = self.glv.get_account('rapidgator', 2)
        file_ids = []

        self.glv.log(f'Checking links on {self.home_page}')

        for key in link_sets.keys():
            for link in link_sets[key]:
                if link == '':
                    continue
                file_ids.append(link.split('/')[4])

        ids = ",".join(file_ids)

        url = f'{self.glv.get_root()}?v=2'
        url += '&action=fileInfo'
        url += f'&user={account["username"]}'
        url += f'&password={account["password"]}'
        url += f'&fileIds={ids}'

        self.glv.driver.get(url)

        if 'fail' in self.glv.driver.page_source:
            self.glv.log(f'Error: {url}')
            return False

        self.glv.log(f'Files all found')
        return True
