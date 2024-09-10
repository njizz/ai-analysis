from PIL import Image
from io import BytesIO
import base64


def base64_to_image(base64_string):
    '''Decode base64 string then convert the byte data to image.'''
    byte_data = base64.b64decode(base64_string)
    return Image.open(BytesIO(byte_data))