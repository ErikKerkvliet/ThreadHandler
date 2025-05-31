
class IwantTF:

    def __init__(self, glv):
        self.glv = glv

    def start(self):
        account = self.glv.get_account('iwanttf', 0)
        self.login(account)

    def login(self, account):
        self.glv.log('Log into https://i.want.tf')

        self.glv.driver.get('https://i.want.tf/to/login')

        login_field = self.glv.get_element('name', 'login-subject')
        login_field.send_keys(account['username'])

        password_field = self.glv.get_element('name', 'password')
        password_field.send_keys(account['password'])

        submit_button = self.glv.get_element('class', 'icon--input-submit')
        submit_button.submit()

        self.glv.log('Login successful')
        self.glv.sleep(1)

    def upload(self, images):
        self.glv.log('Upload images')

        self.glv.driver.get('https://i.want.tf/to/')

        self.glv.sleep(2)
        upload_button = self.glv.get_element('class', 'fa-cloud-upload-alt')

        upload_button.click()

        for image in images:
            image_input = self.glv.get_element('id', 'anywhere-upload-input')
            image_input.send_keys(image)

        self.glv.sleep(2)

        times = 0
        while times > 5:
            js = "return $('button[data-action=\"upload\"]').length"
            if self.glv.run_js(js) > 0:
                js = "$('button[data-action=\"upload\"]').click()"
                self.glv.run_js(js)
                break
            else:
                self.glv.sleep(5)

        self.glv.sleep(1)
        queue_div = self.glv.get_element('id', 'anywhere-upload-submit')

        button = self.glv.get_element_in_element(queue_div, 'tag', 'button', True)
        button.click()

        image_urls = []
        times = 0
        if len(images) == 1:
            while self.glv.driver.current_url == 'https://i.want.tf/to/' and times < 5:
                self.glv.sleep(3)
                times += 1
            image_urls.append(self.glv.driver.current_url)
        else:
            js = "return document.getElementById('uploaded-embed-code-9').value"

            text = ''
            while '[img]' not in text and times < 5:
                self.glv.sleep(3)
                text = self.glv.run_js(js)
                times += 1

            image_urls = text.split(' ')

        self.glv.log('Uploaded successfully')

        return image_urls
