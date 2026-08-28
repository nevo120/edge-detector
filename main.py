image = [
[10,10,10,200,200],
[10,10,10,200,200],
[10,10,10,200,200]
]

threshold = 50

edges=[]

for row in image:
     new_row = []
     for pixel in row:

        new_row.append(0)

     edges.append(new_row)


for row_index,row in enumerate(image):
    for i in range(len(row)-1):
        differenceHor = abs(row[i+1]-row[i])
      
        if differenceHor > threshold:
               edges[row_index][i] = 255

for row_index in range(len(image)-1):
    for i in range(len(image[row_index])):
        differenceVer = abs(image[row_index+1][i]-image[row_index][i])
        if differenceVer>threshold:
               edges[row_index][i] = 255

for row in edges:
    print(row)               
