image = [
[10,10,10,200,200],
[10,10,10,200,200],
[10,10,10,200,200]
]

threshold = 50

for row_index,row in enumerate(image):
    for i in range(len(row)-1):
        differenceHor = abs(row[i+1]-row[i])
        print(differenceHor)
        if differenceHor > threshold:
                print(f"edge detected at row {row_index} between pixels {i} and {i+1}")

for row_index in range(len(image)-1):
    for i in range(len(image[row_index])):
        differenceVer = abs(image[row_index+1][i]-image[row_index][i])
        if differenceVer>threshold:
                print(f"edge detected at {row_index},{row_index+1} at the pixel {i}")

