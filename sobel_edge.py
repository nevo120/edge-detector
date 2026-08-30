image = [
    [10, 10, 10, 200, 200],
    [10, 10, 10, 200, 200],
    [10, 10, 10, 200, 200],
    [10, 10, 10, 200, 200],
    [10, 10, 10, 200, 200]
]

sobel_x = [
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]
]
total = 0
image_size = len(image)
kernel_size = len(sobel_x)
for start_row in range(image_size - kernel_size + 1):
    for start_col in range(image_size - kernel_size + 1):
        total = 0

        for x in range(kernel_size):
            for y in range(kernel_size):
                total += image[start_row+x][start_col+y]*sobel_x[x][y]

        print(total)
