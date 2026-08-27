pixels = [10,12,11,15,210,215,218]
for i in range(len(pixels)-1):
    difference = abs(pixels[i+1] - pixels[i])
    print (difference)