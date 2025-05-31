import re

# Define Regular Expressions as constants for clarity and reusability
URL_PATTERN = r"(\[url.*.\[img.*.\[\/img\]\[\/url\])"
IMAGE_PATTERN = r"(\[img.*.\[\/img\])"


class ImageExtractor:
    """Class to extract image URLs from provided text"""

    def __init__(self, glv):
        """
        Initialize with a global object that contains a regex_group method

        :param glv: An object providing a regex_group method to perform regex operations
        """
        self.glv = glv

    def extract(self, text):
        """
        Extracts cover and additional image URLs from the provided text

        :param text: Text content containing image and URL tags
        :return: Dictionary with 'cover' image and list of 'images'
        """
        url_matches = self.glv.regex_group(text, URL_PATTERN)
        image_matches = self.glv.regex_group(text, IMAGE_PATTERN)

        images = {
            'cover': '',
            'images': []
        }

        # Determine the cover image
        if len(url_matches) > 1 and len(image_matches) > 1:
            if image_matches[0] in url_matches[0]:
                images['cover'] = url_matches[0]
                del url_matches[0]
                del image_matches[0]
            else:
                images['cover'] = image_matches[0]
                del image_matches[0]
        elif len(image_matches) > 1:
            images['cover'] = image_matches[0]
            del image_matches[0]
        else:
            images['cover'] = ''

        # Extract remaining images from URL matches or image matches
        if len(url_matches) > 0:
            imgs = re.split(r'\[/url\]', url_matches[0], flags=re.IGNORECASE)
            for img in imgs:
                img = img.strip(' ')
                if img:
                    images['images'].append(f'{img}[/url]')
        elif len(image_matches) > 0:
            imgs = re.split(r'\[/img\]', image_matches[0], flags=re.IGNORECASE)
            for img in imgs:
                img = img.replace(' ', '')
                if img:
                    images['images'].append(f'{img}')

        return images
