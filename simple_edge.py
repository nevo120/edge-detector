from PIL import Image, ImageFilter

#simple edge detection function
def simple_edge(image_path, threshold=3, blur_radius=1.5):

    #load image and convert to grayscale
    img = Image.open(image_path).convert("L")

    #reduce noise
    gray = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    width, height = gray.size

    #create black output image
    edge_image = Image.new("L", (width, height), 0)

    #check horizontal and vertical pixel differences
    for y in range(height - 1):
        for x in range(width - 1):

            pixel = gray.getpixel((x, y))
            pixel_right = gray.getpixel((x + 1, y))
            pixel_down = gray.getpixel((x, y + 1))

            difference_hor = abs(pixel_right - pixel)
            difference_ver = abs(pixel_down - pixel)

            #mark significant changes as edges
            if difference_hor > threshold or difference_ver > threshold:
                edge_image.putpixel((x, y), 255)

    return edge_image