from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TurboImage:
    def __init__(self, glv):
        self.glv = glv

    def _upload(self, images, thumb_size):
        self.glv.log(f'Uploading images to TurboImageHost with thumb size {thumb_size}')

        self.glv.driver.get('https://www.turboimagehost.com/')

        # Wait for the page to load
        self.glv.sleep(3)

        # Select content type (ADULT content)
        content_select = self.glv.get_element('id', 'imcontent')
        Select(content_select).select_by_value('adult')

        # Set thumbnail size
        thumb_size_input = self.glv.get_element('id', 'thumb_size')
        thumb_size_input.clear()
        thumb_size_input.send_keys(str(thumb_size))

        # Upload images
        for image in images:
            self.glv.sleep(1)
            js = "document.querySelector('.qq-upload-button-selector input[type=file]').style.display = 'block';"
            self.glv.run_js(js)
            file_input = self.glv.get_element('css', '.qq-upload-button-selector input[type=file]')
            file_input.send_keys(image)

        # Click upload button
        upload_button = self.glv.get_element('id', 'Upload Image(s)')
        upload_button.click()

        # Wait for upload to complete and redirect to result page
        wait = WebDriverWait(self.glv.driver, 15)  # Wait up to 15 seconds
        try:
            wait.until(EC.presence_of_element_located((By.ID, "imgCodeIPF")))
        except TimeoutException:
            try:
                wait.until(EC.presence_of_element_located((By.ID, "imgCodeURF")))
            except TimeoutException:
                self.glv.log('Upload did not complete in the expected time', 'error')
                return []

        # Get uploaded image URLs with forum encodings
        try:
            # Try to get the forum code for multiple images
            forum_code = self.glv.get_element('id', 'imgCodeURF').get_attribute('value')
            image_codes = forum_code.strip().split(' ')
        except Exception as e:
            print(f"Error getting forum code for multiple images: {e}")
            # If that fails, get the forum code for a single image
            forum_code = self.glv.get_element('id', 'imgCodeIPF').get_attribute('value')
            image_codes = [forum_code.strip()]

        return image_codes

    def upload(self, images):
        cover_images = [img for img in images if 'cover' in img]
        other_images = [img for img in images if 'cover' not in img]

        result = []

        if cover_images:
            result.extend(self._upload(cover_images, 500))

        if other_images:
            result.extend(self._upload(other_images, 180))

        return result
