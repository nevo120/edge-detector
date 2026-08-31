from PIL import Image
import time

#load pic dummy pic
img = Image.open("unknown.ico").convert("L")
image=list(img.getdata())
width, height = img.size

#for different img files
version = int(time.time())

#
image = [
    image[i * width:(i + 1) * width]
    for i in range(height)
]


#sobels
sobel_x = [

    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]
]
sobel_y = [
    [-1, -2, -1],
    [ 0,  0,  0],
    [ 1,  2,  1]
]

#grad matrix 
gradient = []
kernel_size = len(sobel_x)

#building the grad matrix to colletct changes from image
for start_row in range( height - kernel_size + 1):

    new_row = []
    for start_col in range(width - kernel_size + 1):
        totalX = 0
        totalY = 0

        for x in range(kernel_size):
            for y in range(kernel_size):
                totalX += image[start_row+x][start_col+y]*sobel_x[x][y]
                totalY += image[start_row+x][start_col+y]*sobel_y[x][y]

        magnitude = (totalX**2 + totalY**2) ** 0.5
        new_row.append(magnitude)

    gradient.append((new_row))


#edge matrix with significant differences 
threshold = 40
edge_matrix =[]

for row in gradient:
    new_row =[]

    for value in row:
        if value > threshold:
            new_row.append(255)
        else:
            new_row.append(0)

    edge_matrix.append(new_row)

output_height = len(edge_matrix)
output_width = len(edge_matrix[0])

edge_image = Image.new("L",(output_width,output_height))

#visualise the edges

flat_pixels = []

for row in edge_matrix:
    flat_pixels.extend(row)

edge_image.putdata(flat_pixels)


edge_image.save(f"edges{version}.png")
edge_image.show()