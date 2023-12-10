# Importing the PIL library
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def AddTextToImage(input, text: str, outputPath, fontSize=65, pos=(0, 0), color=(255, 0, 0)):
    image = None
    if isinstance(input, str):
        image = Image.open(input)
    else:
        print("input is no str")
        image = input
    if not isinstance(image, Image.Image):
        print("AddTextToImage fail")
        return None
    I1 = ImageDraw.Draw(image)

    encoding = ""
    fontPath = "../Files/test/font/Graffiti.ttf"
    myFont = ImageFont.truetype(fontPath, fontSize, encoding=encoding)
    I1.text(xy=pos, text=text, font=myFont, fill=color)
    # image.show()
    image.save(outputPath)
