import requests
from PIL import Image
from io import BytesIO
import base64

def image_from_url(url):
    img = requests.get(url)
    return img.content

