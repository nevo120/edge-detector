from PIL import Image

#sobel edge detection function
def sobel_edge(image_path, threshold=40):

    #load image and convert to grayscale
    img = Image.open(image_path).convert("L")
    pixels = list(img.getdata())
    width, height = img.size

    #turn pixel list into matrix
    image = [
        pixels[i * width:(i + 1) * width]
        for i in range(height)
    ]

    #sobel kernels
    sobel_x = [
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ]

    sobel_y = [
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1]
    ]

    kernel_size = len(sobel_x)

    #gradient matrix
    gradient = []

    #move kernel over image
    for start_row in range(height - kernel_size + 1):
        new_row = []

        for start_col in range(width - kernel_size + 1):
            total_x = 0
            total_y = 0

            #calculate sobel x and y for current window
            for x in range(kernel_size):
                for y in range(kernel_size):
                    pixel = image[start_row + x][start_col + y]

                    total_x += pixel * sobel_x[x][y]
                    total_y += pixel * sobel_y[x][y]

            #combine x and y changes
            magnitude = (total_x**2 + total_y**2) ** 0.5
            new_row.append(magnitude)

        gradient.append(new_row)

    #edge matrix after threshold
    edge_matrix = []

    for row in gradient:
        new_row = []

        for value in row:
            if value > threshold:
                new_row.append(255)
            else:
                new_row.append(0)

        edge_matrix.append(new_row)

    #create output image
    output_height = len(edge_matrix)
    output_width = len(edge_matrix[0])

    edge_image = Image.new("L", (output_width, output_height))

    #turn matrix back into pixel list
    flat_pixels = []

    for row in edge_matrix:
        flat_pixels.extend(row)

    edge_image.putdata(flat_pixels)

    return edge_image