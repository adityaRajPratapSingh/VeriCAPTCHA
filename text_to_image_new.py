from captcha.image import ImageCaptcha
import io
from io import BytesIO
from PIL import Image

def the_image(text:str):
    captcha:ImageCaptcha = ImageCaptcha(
      width=400,
      height = 400,
      fonts = [
          './Jersey10-Regular.ttf',
          './Lato-Black.ttf',
          './OpenSans-Regular.ttf',
          './Roboto-Thin.ttf'
      ],
      font_sizes=(70, 40, 100, 30)
    )
    data:BytesIO = captcha.generate(text)
    return data.read()
