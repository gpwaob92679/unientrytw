import io
import logging
import urllib.request

from PIL import Image
from PIL import ImageChops

logger = logging.getLogger(__name__)

with Image.open('reference_digits.png').convert('L') as img:
    REFERENCE_DIGITS = [img.crop((9 * i, 0, 9 * i + 8, 10)) for i in range(10)]


def data_uri_to_image(data_uri: str) -> Image.Image:
    img = urllib.request.urlopen(data_uri).read()
    img = Image.open(io.BytesIO(img))
    return img


def ocr_id(img: Image.Image) -> str:
    img = img.convert('L')
    assert img.width == 90 and img.height == 20
    # Binarization
    extrema = img.getextrema()
    threshold = (extrema[0] + extrema[1]) / 2
    img = img.point(lambda point: 255 if point > threshold else 0)

    result = ['?'] * 8
    for i in range(8):
        left = 5 + 9 * i
        digit_img = img.crop((left, 6, left + 8, 16))
        for reference_digit in range(10):
            difference = ImageChops.difference(
                digit_img, REFERENCE_DIGITS[reference_digit])
            if not difference.getbbox():  # Match found
                result[i] = str(reference_digit)
        if result[i] == '?':
            logger.warning('Match not found on digit %s', i)
    if ''.join(result) == '111312606':
        img.show()
    return ''.join(result)
