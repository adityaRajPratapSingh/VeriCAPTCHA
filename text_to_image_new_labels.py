from captcha.image import ImageCaptcha
import io
from io import BytesIO
from PIL import Image

def the_image_labels(text:str):
    captcha:ImageCaptcha = ImageCaptcha(
      width=150,
      height = 50,
      fonts = [
          #'./Jersey10-Regular.ttf',
          #'./Lato-Black.ttf',
          './OpenSans-Regular.ttf',
          './Roboto-Thin.ttf'
      ],
      font_sizes=(40, 50)
    )
    data:BytesIO = captcha.generate(text)
    
    return data.read()
