from Hcapital import Hcapital
from AnimeSharing import AnimeSharing
from FillTemplate import FillTemplate
from ImageExtractor import ImageExtractor
from ImgBB import ImgBB
from TurboImage import TurboImage


class Update:

    def __init__(self, glv):
        self.glv = glv
        self.hcapital = Hcapital(self.glv)
        self.imgbb = ImgBB(self.glv)
        self.turbo_image = TurboImage(self.glv)
        self.sharing = AnimeSharing(self.glv)
        self.fillTemplate = FillTemplate(self.glv)
        self.extractor = ImageExtractor(self.glv)

    def update(self):
        if self.hcapital.start() == 'not possible':
            return quit()

        self.glv.log(f'Entry: {self.glv.id}')

        data = self.hcapital.get_data()

        self.glv.fix_links(data)

        has_thread = False
        for i, user in enumerate(self.glv.get_sharing_account()):
            self.sharing.account = user
            self.glv.user = user

            if len(data['anime-sharing-urls'][user['username']]) == 0:
                continue

            has_thread = True

            self.sharing.login()

            urls = data['anime-sharing-urls'][user['username']]
            for url in urls:
                self.update_thread(url, data)

        if not has_thread:
            return data

        self.hcapital.links = None
        self.glv.previous_error = False
        self.glv.reset()

        return False

    def update_thread(self, url, data):
        self.glv.log(f'Updating: {url}')
        self.glv.driver.get(url)

        self.glv.sleep(3)

        js = 'localStorage.setItem(\'xf_editorDisabled\', 1);'

        js += "document.getElementsByClassName('actionBar-action--edit')[0].click();"
        self.glv.run_js(js)
        self.glv.sleep(3)

        message_input = self.glv.get_elements('name', 'message', 1, 0, True)
        message = message_input.get_attribute('value')

        if 'image_urls' not in data.keys():
            if 'i.**' in message or 'i.want.tf' in message:
                # data['image_urls'] = self.imgbb.upload(data['temp_images'])
                try:
                    data['image_urls'] = self.turbo_image.upload(data['temp_images'])
                except Exception as e:
                    print(f"Error uploading images to TurboImage: {e}")
                    data['image_urls'] = self.imgbb.upload(data['temp_images'])

                self.glv.driver.get(url)

                self.glv.sleep(5)

                js = "document.getElementsByClassName('actionBar-action--edit')[0].click();"
                self.glv.run_js(js)

                self.glv.sleep(5)
            else:
                data['image_urls'] = self.extractor.extract(message)

        thread = self.fillTemplate.create_thread(data)

        replacements = {
            '\n': '\\n',
            '[td] [/td]': '',
            '[/td] [td]': '',
            '[/td][td]': '',
            '[td][/td]': ''
        }

        body = thread['body']
        for old, new in replacements.items():
            body = body.replace(old, new)

        js = f'document.getElementsByName("message")[0].value = "{body}";'
        self.glv.run_js(js)

        self.save()

        while '<span class="button-text">Save</span>' in self.glv.driver.page_source:
            self.glv.sleep(5)
        self.glv.sleep(2)

    def save(self):
        self.glv.log('Saving changes')

        js = 'document.getElementsByClassName("button--icon--save")[0].click();'

        self.glv.run_js(js)
