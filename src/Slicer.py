import os
from PIL import Image

file = "./DummyMap.png"
map = Image.open(file)

boxSize = 100

xsize, ysize = map.size

parts = []
for x in range(0, xsize, boxSize):
    for y in range(0, ysize, boxSize):
        parts.append(map.crop((x, y, x + boxSize, y + boxSize)))

if not os.path.exists("./out"):
    os.makedirs("./out")

for i, part in enumerate(parts):
    part.save("./out/part" + str(i) + ".png", "PNG")