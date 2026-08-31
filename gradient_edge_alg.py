import math
from PIL import Image,ImageFilter
import time


testimage = Image.open("unknown.ico")
gray = testimage.convert("L")
gray = gray.filter(ImageFilter.GaussianBlur(radius=1.5))

width,height = gray.size

edge_image = Image.new("L",(width,height),0)

threshold = 5

for y in range(height-1):
    for x in range(width-1):

     pixel = gray.getpixel((x,y))
     pixel_right = gray.getpixel((x+1,y))
     pixel_down = gray.getpixel((x,y+1))

     Gx= pixel_right-pixel
     Gy = pixel_down-pixel
     gradient= math.sqrt(Gx**2+Gy**2)

     if gradient > threshold:
        edge_image.putpixel((x,y),255)


version= int(time.time())
edge_image.save(f"gradEdges{version}.png")

     