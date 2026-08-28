from PIL import Image,ImageFilter
import time
testimage = Image.open("unknown.ico")
gray = testimage.convert("L")
gray = gray.filter(ImageFilter.GaussianBlur(radius=1.5))
version = int(time.time())
width,height = gray.size
threshold = 3
edge_image = Image.new("L",(width,height),0)
for y in range(height-1):
    for x in range(width-1):
        pixel = gray.getpixel((x,y))
        pixel_right = gray.getpixel((x+1,y))
        pixel_down = gray.getpixel((x,y+1))
        differencecVer = abs((pixel_down - pixel)) 
        differencecHor = abs((pixel_right - pixel))
        if differencecHor > threshold or differencecVer > threshold:
            edge_image.putpixel((x,y),255)

edge_image.save(f"edges{version}.png")

 
