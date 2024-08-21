from captcha.image import ImageCaptcha
import io
from io import BytesIO
from PIL import Image

def the_image(text:str):
    captcha:ImageCaptcha = ImageCaptcha(
      width=800,
      height = 500,
      fonts = [
          './Jersey10-Regular.ttf',
          './Lato-Black.ttf',
          './OpenSans-Regular.ttf',
          './Roboto-Thin.ttf'
      ],
      font_sizes=(60, 40, 100)
    )
    data:BytesIO = captcha.generate(text)
    
    return data.read()
