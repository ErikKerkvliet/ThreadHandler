import time

from src.hosts.Host import Host


class SaberCat:
    def __init__(self, glv, user):
        self.glv = glv
        self.user = user
        self.home_page = 'https://sabercathost.com/'
        self.upload_page = 'https://sabercathost.com/?aff=f83bab64873bc0b2'
        self.login_page = 'https://sabercathost.com/login'

        self.host = Host(self)

    def login(self, account=None):
        user = account if account else self.user

        self.glv.driver.get(self.home_page)

        if 'https://sabercathost.com/account_home.html' in self.glv.driver.page_source.lower():
            return

        self.glv.driver.get(self.login_page)

        login_field = self.glv.get_elements('name', 'username', 1, 0, True)
        login_field.send_keys(user['username'])

        password_field = self.glv.get_elements('name', 'password', 1, 0, True)
        password_field.send_keys(user['password'])

        login_button = self.glv.get_elements('class', 'btn-login', 1, 0, True)
        login_button.click()

        source = self.glv.driver.page_source
        times = 0
        while 'filemanagerwrapper' not in source.lower() and times < 20:
            times += 1
            time.sleep(2)

        self.glv.log('Login successful')

    def upload(self, files):
        self.login(self.user)

        self.glv.log(f'Start uploading on {self.home_page}')

        self.glv.driver.get(self.upload_page)

        file_str = '\n'.join(files)

        self.glv.get_element('id', 'add_files_btn').send_keys(file_str)
        self.glv.sleep(2)

        js = 'document.getElementById("start_upload_btn").click()'

        self.glv.run_js(js)

        pass

    def check_links(self, link_sets) -> bool:
        return self.host.check_links(link_sets)
