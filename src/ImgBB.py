class ImgBB:

    def __init__(self, glv):
        self.glv = glv

    def upload(self, images):
        self.glv.log('Upload images')

        self.glv.driver.get('https://nl.imgbb.com/')

        self.glv.get_element('xpath', '//*[@id="top-bar"]/div/ul[2]/li[1]/span/span[1]').click()

        self.glv.sleep(3)

        for image in images:
            image_input = self.glv.get_element('id', 'anywhere-upload-input')
            image_input.send_keys(image)

        # uploading on site need another check here!!
        self.glv.sleep(5)

        times = 0
        while times < 5:
            js = "return $('button[data-action=\"upload\"]')"
            if len(self.glv.run_js(js)) > 0:
                js = "return $('button[data-action=\"upload\"]').click()"
                self.glv.run_js(js)
                break
            else:
                self.glv.sleep(5)
                times += 1
        else:
            self.glv.log('Upload button is never found', 'error')
            self.glv.quit()

        times = 0
        self.glv.sleep(2)
        embedded_images = ''
        thumbnails = ''
        while times < 5:
            js = "return $('#uploaded-embed-code-4').val()"
            if self.glv.run_js(js) != '':
                js = "return $('#uploaded-embed-code-3').val()"
                embedded_images = self.glv.run_js(js)

                js = "return $('#uploaded-embed-code-4').val()"
                thumbnails = self.glv.run_js(js)
                break
            else:
                self.glv.sleep(5)
                times += 1
        else:
            self.glv.log('Value of "uploaded-embed-code-4" is always empty', 'error')
            self.glv.quit()

        images1 = embedded_images.split('\n')

        images2 = thumbnails.split(' ')

        for image in images2:
            if 'cover' in image:
                images2.remove(image)
                break

        images = images2

        for image in images1:
            if 'cover' in image:
                images.insert(0, image)
                break

        return images
