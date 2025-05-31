
HOST_NAME_RAPIDGATOR = 'rapidgator'
HOST_NAME_MEXASHARE = 'mexashare'
HOST_NAME_KATFILE = 'katfile'
HOST_NAME_FIKPER = 'fikper'
HOST_NAME_DDOWNLOAD = 'ddownload'
HOST_NAME_ROSEFILE = 'rosefile'
HOST_NAME_SABERCAT = 'sabercat'
HOST_NAME_FICHIER = '1fichier'
HOST_NAME_LOCALHOST = 'localhost'
HOST_NAME_FILE = 'file'


HOST_NAMES = [
    HOST_NAME_RAPIDGATOR,
    HOST_NAME_MEXASHARE,
    HOST_NAME_KATFILE,
    # HOST_NAME_DDOWNLOAD,
    # HOST_NAME_FIKPER,
    # HOST_NAME_ROSEFILE,
    # HOST_NAME_SABERCAT,
]
MAX_WAIT_TIMES = 2000


class Host:
    def __init__(self, parent):
        self.parent = parent
        self.glv = parent.glv

    def login(self, user):

        self.glv.log(f'Log into {self.parent.home_page}')

        self.glv.driver.get(self.parent.home_page)

        source = self.glv.driver.page_source

        if 'Logout' in source:
            return

        url = f'{self.parent.home_page}/login.html'

        self.glv.driver.get(url)

        login_field = self.glv.get_elements('name', 'login', 1, 0, True)

        login_field.send_keys(user['username'])

        password_field = self.glv.get_elements('name', 'password', 1, 0, True)

        password_field.send_keys(user['password'])

        buttons = self.glv.get_elements('tag', 'button')

        submit_button = None
        for button in buttons:
            if button.text.lower() == 'login':
                submit_button = button
                break

        if submit_button:
            submit_button.click()
        else:
            submit_button = self.glv.get_elements('tag', 'form', 1, 0, True)

            if submit_button:
                submit_button.submit()

        self.glv.sleep(1, 2)

        self.glv.log('Login successful')

    def check_links(self, link_sets) -> bool:
        self.glv.log(f'Checking links on {self.parent.home_page}')

        if len(list(link_sets.keys())) == 1 and link_sets[list(link_sets.keys())[0]] == []:
            self.glv.log('No links are given')
            return False

        for key in link_sets.keys():
            for link in link_sets[key]:
                self.glv.driver.get(link)
                self.glv.sleep(0.5)
                source = self.glv.driver.page_source.lower()
                if 'not found' in source \
                        or 'can\'t be found' in source \
                        or 'file has been removed' in source \
                        or 'file does not exist' in source \
                        or 'the file has been deleted.' in source:
                    self.glv.log('Not all links exist or they are removed')
                    return False
        self.glv.log(f'Files all found')
        return True
