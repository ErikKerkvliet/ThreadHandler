from Links import Links
from Tabs import Tabs


class FillTemplate:

    def __init__(self, glv):
        self.glv = glv
        self.links = Links(glv)
        self.tabs = Tabs(glv)
        self.template = ''
        self.update = False

    def load_template(self):
        self.glv.log(f'Using template: ./templates/{self.glv.user["username"]}')

        file = open(f'{self.glv.path}/templates/{self.glv.user["username"]}', "r")
        return file.read()

    def create_thread(self, data):
        self.template = self.load_template()

        return {
            'type': data['type'],
            'subject': self.create_subject(data),
            'body': self.create_body(data),
            'tags': self.create_tags(data)
        }

    def create_body(self, data):

        self.glv.log('Fill template')

        cover = self.create_cover(self.get_cover(data['image_urls']))
        if cover == '':
            self.glv.quit()

        urls = []
        times = 0
        if isinstance(data['image_urls'], dict):
            urls = data['image_urls']['images']
        else:
            for url in data['image_urls']:
                if 'cover' in url or 'free images' in url:
                    continue
                times += 1
                if times == 6:
                    break
                urls.append(url)

        self.template = self.template.replace('#cover#', cover)
        self.template = self.template.replace('#title_kanji#', data['title'])
        self.template = self.template.replace('#title_romanji#', data['romanji'])
        self.template = self.template.replace('#images#', self.create_images(urls))

        link_template = self.tabs.create_links(data['links'])
        self.template = self.template.replace('#links#', link_template)

        self.template = self.template.replace('#release_date#', data['released'])
        self.template = self.template.replace('#developers#', ', '.join(data['developers']))
        self.template = self.template.replace('#site_type#', data['siteType'])
        self.template = self.template.replace('#website#', self.get_website(data, 'website'))
        self.template = self.template.replace('#website_short#', self.get_website(data, 'website', 55))
        self.template = self.template.replace('#information#', self.get_website(data, 'information'))
        self.template = self.template.replace('#information_short#', self.get_website(data, 'information', 55))
        self.template = self.template.replace('#size#', data['size'])

        return self.escape_chars(self.template)

    @staticmethod
    def get_cover(images):
        if isinstance(images, dict):
            return images['cover']
        for image in images:
            if 'cover' in image:
                return image
        return ''

    @staticmethod
    def create_cover(image):
        return image

    @staticmethod
    def get_website(data, site_type='', length=None):
        data[site_type] = data[site_type].replace('maniax/', '')
        if data[site_type] != '':
            if length is not None:
                return data[site_type][0:length]
            return data[site_type]
        return data['information'].replace('maniax/', '')

    @staticmethod
    def create_tag_released(released):
        return released.replace('/', '-')

    @staticmethod
    def create_images(images):
        return '　'.join(images)

    @staticmethod
    def create_comment(comment):
        return '\n[B][SIZE=2]{}[/SIZE][/B]\n'.format(comment)

    @staticmethod
    def create_link_set(links, host, size):
        text = ''
        if links:
            text += '[B][SIZE={}]{}: [/SIZE][/B]\n\n'.format(size, host.capitalize())
            for link in links:
                text += '[URL]{}[/URL]\n'.format(link)
        return text

    def escape_chars(self, text):
        text = text.replace('&nbsp;', ' ')
        if not self.glv.only_text:
            text = text.replace("\n", "\\n")
        return text

    def create_subject(self, data):
        self.glv.log('Create subject')

        tag_released = self.create_tag_released(data['released'])
        subject = '[{}][{}] {}'.format(tag_released, data['developers'][0], data['title'])
        return self.escape_chars(subject)

    def create_tags(self, data):
        self.glv.log('Create tags')

        tag_released = self.create_tag_released(data['released'])
        romanji = self.escape_chars(data['romanji'])
        developer = self.escape_chars(data['developers'][0])
        return [tag_released, romanji, developer, 'katfile', 'rapidgator', 'mexashare']

    def store_thread(self, post):
        self.glv.log('Create thread file')

        file = open(f'{self.glv.home}/Threads_{self.glv.user["username"]}/thread_{self.glv.id}.txt', "w+")

        post['tags'] = ', '.join(post['tags'])

        file.write('{}\n'.format(post['type']))
        file.write('|part|{}\n'.format(post['subject']))
        file.write('|part|{}\n'.format(post['body']))
        file.write('|part|{}'.format(post['tags']))
        file.close()

        self.glv.log('Created file')
        self.glv.log(f"Time: {self.glv.get_time()}")
