from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import math

from config import USERNAME_3

# Constants for URLs
AS_URL = 'http://www.anime-sharing.com/forum/'
AS_GAME_TYPE_URL = 'hentai-games.38'
AS_OVA_TYPE_URL = 'hentai-ovas.36'
AS_LOGIN_URL = 'http://www.anime-sharing.com/forum/'
AS_THREAD_URL_TEMPLATE = 'https://www.anime-sharing.com/forums/{type_post}/post-thread'

# Constants for script elements and attributes
SELECTOR_P_ACCOUNT = '.p-account'
PARTIAL_LINK_TEXT_LOGIN = 'login/logout'
CLASS_NAVGROUP_LINK_USER = 'p-navgroup-link--user'
CLASS_NAVGROUP_LINK_LOGIN = 'p-navgroup-link--logIn'
NAME_LOGIN = 'login'
NAME_PASSWORD = 'password'
CLASS_BUTTON_ICON_LOGIN = 'button--icon--login'
NAME_PREFIX_ID = 'prefix_id'
NAME_TITLE = 'title'
CLASS_FR_VIEW = 'fr-view'
TAG_TEXTAREA = 'textArea'
NAME_MESSAGE = 'message'
CLASS_SELECT2_SEARCH_FIELD = 'select2-search__field'
CLASS_ACTIONBAR_ACTION_EDIT = 'actionBar-action--edit'
CLASS_BUTTON_ICON_WRITE = 'button--icon--write'
SPAN_BUTTON_TEXT_SAVE = '<span class="button-text">Save</span>'


class AnimeSharing:
    """Class to interact with the Anime-Sharing forum"""

    def __init__(self, glv):
        """
        Initialize with a global object that will provide access to various utilities

        :param glv: Global object providing methods for logging, element access, and account details
        """
        self.glv = glv
        self.account = {}
        self.entry_type = ''

    def start(self, username=USERNAME_3):
        """
        Start the process by fetching account details and logging in

        :param username: Username to fetch details for (default is 0)
        """
        self.account = self.glv.get_sharing_account(username)
        self.login()

    def login(self):
        """Log into the Anime-Sharing forum"""
        self.glv.log('Log into http://www.anime-sharing.com')
        self.glv.driver.get(AS_LOGIN_URL)

        WebDriverWait(self.glv.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_P_ACCOUNT))
        )
        self.glv.run_js('window.stop()')
        source = self.glv.driver.page_source

        if 'p-navgroup--member' in source:
            self.glv.log('Already logged in')
            if self.account['username'] in source:
                return
            else:
                self.glv.log('Switch user, return')
                self.logout()
                self.glv.sleep(1)
                self.login()
        else:
            self.glv.get_elements('class', CLASS_NAVGROUP_LINK_LOGIN, 1, 0, True).click()
            WebDriverWait(self.glv.driver, 10).until(
                EC.presence_of_element_located((By.NAME, NAME_LOGIN))
            )
            self.glv.run_js(f'document.getElementsByName("{NAME_LOGIN}")[0].value = "{self.account["username"]}"')
            self.glv.run_js(f'document.getElementsByName("{NAME_PASSWORD}")[0].value = "{self.account["password"]}"')

            try:
                self.glv.get_elements('class', CLASS_BUTTON_ICON_LOGIN, 0, 1, True).click()
            except Exception as e:
                print(f'Error clicking login button: {e}')
                pass

            self.glv.sleep(3)
            self.glv.log('Login successful')

    def logout(self):
        self.glv.get_elements('class', CLASS_NAVGROUP_LINK_USER, 1, 0, True).click()
        self.glv.sleep(1)
        self.glv.run_js(
            f'var elements = document.getElementsByClassName("menu-linkRow"); elements[elements.length - 1].click();')

    def create_thread(self, data, post):
        """
        Create a new thread on the Anime-Sharing forum

        :param data: Entry data to determine the type of thread
        :param post: Post content including subject, body, and tags
        """
        self.entry_type = data if isinstance(data, str) else data['type']
        self.glv.log(f'Create {self.entry_type} thread')

        subject = post['subject']
        body = post['body']
        tags = post['tags']

        type_post = AS_GAME_TYPE_URL if self.entry_type == 'game' else AS_OVA_TYPE_URL
        url = AS_THREAD_URL_TEMPLATE.format(type_post=type_post)
        self.glv.driver.get(url)

        source = self.glv.driver.page_source

        if 'Oops! We ran into some problems.' in source:
            if 'You have hit the limit on the number of threads you are allowed to create.' in source:
                self.glv.log('Thread limit reached.')
                self.glv.sleep(3600)
                self.create_thread(data, post)

        self.glv.sleep(3)
        self.glv.run_js(f'document.getElementsByName("{NAME_PREFIX_ID}").value = "37";')
        self.glv.sleep(2)

        combined_tags = tags if isinstance(tags, str) else ', '.join(tags[:30] if len(tags[-1]) > 30 else tags)

        self.glv.run_js(f'document.getElementsByName("{NAME_TITLE}")[0].value = "{subject}";')
        self.glv.sleep(2)
        body_tagged = body.replace('\\n', '<br>')
        self.glv.run_js(f'document.getElementsByClassName("{CLASS_FR_VIEW}")[0].innerHTML = "{body_tagged}"')
        self.glv.sleep(1)

        js = ('var textfields = document.getElementsByTagName("textArea");'
              'for (var i = 0; i < textfields.length; i++) {'
              'if (textfields[i].name === "' + NAME_MESSAGE + '") {'
                                                              'textfields[i].value = "' + body + '"; break; }}')
        self.glv.run_js(js)

        self.glv.run_js(
            f'return document.getElementsByClassName("{CLASS_SELECT2_SEARCH_FIELD}")[0].value = "{combined_tags}";')
        self.update()

    def update_thread(self, data, username=None):
        """
        Update an existing thread with new links

        :param data: Data containing new links to update
        :param username: Username responsible for the thread
        """
        self.glv.log('Updating thread')

        username = username if username is not None else self.account['username']
        for url in data['anime-sharing-urls'][username]:
            if url.strip():
                self.glv.log(f'Updating: {url}')
                self.glv.driver.get(url)
                self.glv.sleep(5)

                self.glv.run_js(f"document.getElementsByClassName('{CLASS_ACTIONBAR_ACTION_EDIT}')[0].click();")
                self.glv.sleep(10)
                source = self.glv.driver.page_source

                links = self.glv.regex_group(source, r"(https:\/\/rapidgator\.net.*.html\")")
                rapidgator_links = []

                for link in links:
                    if 'target' not in link and link not in rapidgator_links:
                        rapidgator_links.append(link)

                js = ''
                for i in range(len(rapidgator_links)):
                    link = rapidgator_links[i][:-1].replace('/', r'\/')
                    js += f"document.documentElement.innerHTML = document.documentElement.innerHTML.replace(/{link}/g, '{data['links']['rapidgator']['#'][i]}');"

                if data['links']['mexashare']['#']:
                    mexashare_links = self.glv.regex_group(source, r"(https:\/\/mexa\.sh.*.html\")")
                    if len(mexashare_links) >= 3:
                        for j in range(2):  # Update first two sets only
                            for i in range(int(math.floor(len(mexashare_links) / 3))):
                                link = mexashare_links[i][:-1].replace('/', r'\/')
                                js += f"document.documentElement.innerHTML = document.documentElement.innerHTML.replace(/{link}/g, '{data['links']['mexashare']['#'][i]}');"

                self.glv.run_js(js)
                self.glv.log('Saving changes')
                self.glv.sleep(5)
                self.update()

                while SPAN_BUTTON_TEXT_SAVE in self.glv.driver.page_source:
                    self.glv.sleep(5)

        self.glv.sleep(2)

    def submit(self, entry_id):
        """
        Submit a new thread

        :param entry_id: Entry ID associated with the thread
        """
        self.glv.run_js(f'document.getElementsByClassName("{CLASS_BUTTON_ICON_WRITE}")[0].click();')
        self.glv.sleep(10)

        thread_url = self.glv.driver.current_url.replace('/reply', '')
        self.glv.log('Successfully created thread')

        threads = self.glv.hcapital.get_thread_count()
        threads += 1

        thread_data = {
            'entry_id': entry_id,
            'number': threads,
            'url': thread_url,
            'author': self.account['username'],
        }
        self.glv.db.insert_row('threads', thread_data)

    def update(self):
        """Click the update button to save changes"""
        self.glv.run_js(f'document.getElementsByClassName("{CLASS_BUTTON_ICON_WRITE}")[0].click();')
