import contextlib
import urllib.request
from urllib.parse import unquote

from src.hosts.Host import HOST_NAME_RAPIDGATOR
from src.hosts.Host import HOST_NAMES

from config import USERNAME_1, USERNAME_2


class Hcapital:

    def __init__(self, glv):
        self.glv = glv
        self.data = None
        self.links = None

    def start(self):
        self.data = {}

        if not self.glv.update and not self.glv.force and isinstance(self.glv.db.check_for_thread(self.glv.selected_username), int):
            return 'not possible'

        possible = False
        while not possible:
            url = self.glv.get_hcapital(True) + str(self.glv.id)
            self.glv.driver.get(url)
            possible = self.check_possible()
            if not possible:
                return 'not possible'

        if not self.initialize_data():
            return 'not possible'

    def check_possible(self):
        js = "return document.getElementsByTagName('textarea').length"
        length = self.glv.run_js(js)

        if '<body></body>' in self.glv.driver.page_source or 'fatal error' in self.glv.driver.page_source.lower():
            return False

        if self.links is None and self.glv.create_thread:
            self.links = self.get_links()

            # Check if any host has empty links for any comment
            empty_host_links = False
            comments = self.links[HOST_NAME_RAPIDGATOR].keys()
            for host in HOST_NAMES:
                for comment in comments:
                    if not self.links[host][comment]:
                        empty_host_links = True

            # If any host has empty links, return False
            if not self.glv.force and not empty_host_links:
                return False

        if (len(self.links[HOST_NAME_RAPIDGATOR]) == 0 or
                ('#' in self.links[HOST_NAME_RAPIDGATOR].keys()
                 and self.links[HOST_NAME_RAPIDGATOR]['#'] == [])):
            return False

        if length > 1 and len(self.links[HOST_NAME_RAPIDGATOR]) > 0 or self.glv.force:
            return True

        if not self.glv.update:
            self.glv.log('Problem with entry: {}'.format(self.glv.id), 'warning')
            self.glv.set_next_id()

    def initialize_data(self):
        self.glv.log('Get data from Hcapital')
        self.glv.sleep(2)

        self.glv.driver.get(self.glv.get_hcapital(True) + str(self.glv.id))

        self.data['temp_images'] = []
        self.data['type'] = self.get_type(self.glv.get_element('id', 'type').get_attribute('value'))
        self.data['title'] = self.glv.get_element('id', 'title').get_attribute('value')
        self.data['romanji'] = self.glv.get_element('id', 'romanji').get_attribute('value')
        self.glv.romanji_title = self.data['romanji']
        self.data['developers'] = self.get_developers()

        self.data['released'] = self.glv.get_element('id', 'released').get_attribute('value')
        self.data['size'] = self.glv.get_element('id', 'size').get_attribute('value')
        self.data['website'] = self.glv.get_element('id', 'website').get_attribute('value')
        self.data['information'] = self.glv.get_element('id', 'information').get_attribute('value')
        self.data['siteType'] = self.get_site_type()

        self.data['password'] = self.glv.get_element('id', 'password').get_attribute('value')

        self.data['cover'] = '{}/entry_images/entries/{}/cover/_cover_l.jpg'.format(self.glv.get_root(), self.glv.id)
        self.data['comments'] = self.get_comments()

        self.data['links'] = self.links

        self.glv.driver.get(self.glv.get_hcapital(False) + str(self.glv.id))

        self.data['images'] = self.get_images()
        self.data['anime-sharing-urls'] = self.get_anime_sharing_urls()

        if not self.glv.create_thread and not self.glv.update:
            for username in self.data['anime-sharing-urls'].keys():
                if len(self.data['anime-sharing-urls'][username]) > 0:
                    return False
        return True

    def get_developers(self):
        developers = []
        elements = self.glv.get_elements('class', 'developers')

        for element in elements:
            developer = element.get_attribute('value')
            developers.append(developer)

        return developers

    def get_site_type(self):
        if 'getchu' in self.data['information']:
            return 'Getchu'
        elif 'dlsoft' in self.data['information']:
            return 'Dlsite'
        else:
            return 'Information'

    def get_images(self):
        self.glv.driver.get(self.glv.get_hcapital(False) + str(self.glv.id))

        image_box = self.glv.get_element('id', 'single')

        elements = self.glv.get_element_in_element(image_box, 'class', 'info_images')

        path = self.glv.temp_images_path.split('source/')[-1]
        self.glv.log(f'Downloading images to: {path}')

        images = [self.data['cover']]
        self.download_image(self.data['cover'])
        for key, element in enumerate(elements):
            if key == 6:
                return images

            image_sub_src = element.get_attribute('src')

            image_url = image_sub_src
            images.append(image_url)

            self.download_image(image_url)

        return images

    def download_image(self, image):
        file_name = image.split('/')[-1]
        path = '{}/{}'.format(self.glv.temp_images_path, unquote(file_name))
        with open(path, 'wb') as out_file:
            with contextlib.closing(urllib.request.urlopen(image)) as fp:
                block_size = 1024 * 8
                while True:
                    block = fp.read(block_size)
                    if not block:
                        break
                    out_file.write(block)

        self.data['temp_images'].append(path)

    def get_comments(self):
        comments = []
        self.glv.sleep(4)
        comments_input = self.glv.get_elements('class', 'links-comment')
        if not isinstance(comments_input, int):
            for comment in comments_input:
                comments.append(comment.get_attribute('value'))
        return comments

    def get_anime_sharing_urls(self):
        forms = self.glv.get_elements('class', 'sharing-form')

        authors = {
            USERNAME_1: [],
            USERNAME_2: [],
        }
        for form in forms:
            author = self.glv.get_element_in_element(form, 'class', 'sharing-author', True)
            url_element = self.glv.get_element_in_element(form, 'class', 'sharing-url', True)

            auth = author.get_attribute('value')

            url = url_element.get_attribute('value')
            if url == '\n':
                continue
            authors[auth].append(url)

        return authors

    def get_data(self):
        return self.data

    def edit_links(self, host_links, web):
        self.glv.log(f'Edit links at {self.glv.get_root(web)}')

        self.glv.driver.get(self.glv.get_hcapital(True, web) + str(self.glv.id))

        self.glv.sleep(2)

        for j, host in enumerate(HOST_NAMES):
            for i, key in enumerate(host_links[host].keys()):
                urls = {}
                for link in host_links[host][key]:
                    file_name = link.split('/')[-1]
                    urls[f'{file_name}'] = link
                    continue
                urls = dict(sorted(urls.items()))
                host_links[host][key] = list(urls.values())

                host_link = '\\n'.join(host_links[host][key])

                element_nr = (i * 6) + HOST_NAMES.index(host)
                js = f"$('textarea[name=\"links-{element_nr}-links\"]').first().val('{host_link}')"

                self.glv.run_js(js)

        js = "$('#app-id').val('Thread-Handler')"
        self.glv.run_js(js)

        submit_button = self.glv.get_element('id', 'submit')
        submit_button.click()

        self.glv.sleep(2)

    def get_links(self):
        self.glv.driver.get(self.glv.get_hcapital(True, True) + str(self.glv.id))

        comments = self.get_comments()
        comments.insert(0, '#')

        links = {}
        for host in HOST_NAMES:
            links[host] = {}

            link_elements = self.glv.get_elements('class', f'{host}-links')
            for (key, element) in enumerate(link_elements):
                value = element.get_attribute('value')
                if value == '':
                    links[host][comments[key]] = []
                    continue
                links[host][comments[key]] = value.split('splitter')

            if len(links[host].keys()) > 0 and not getattr(getattr(self.glv, host), 'check_links')(links[host]):
                if host == HOST_NAME_RAPIDGATOR:
                    self.glv.log('Rapidgator link is not found')
                    self.glv.sleep(10)
                    self.glv.quit()
                else:
                    links[host]['#'] = []

            self.glv.driver.get(self.glv.get_hcapital(True, True) + str(self.glv.id))

        return links

    @staticmethod
    def get_type(entry_type):
        if entry_type == '3d' or entry_type == 'ova':
            return 'ova'
        return 'game'

    def get_thread_count(self):
        url = self.glv.get_hcapital(False, True) + str(self.glv.id)
        self.glv.driver.get(url)

        js = "$('#info-title').attr('data-thread-count')"
        return self.glv.run_js(js, True)
