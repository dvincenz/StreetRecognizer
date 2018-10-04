import json
import os
from PIL import Image

file = "./DummyMap.png"
map = Image.open(file)

boxSize = 100
mapOffset = (100, 100)

xsize, ysize = map.size

parts = []
for x in range(0, xsize, boxSize):
    for y in range(0, ysize, boxSize):
        part = {}
        part['part'] = map.crop((x, y, x + boxSize, y + boxSize))
        part['a'] = (x,y)
        part['b'] = (x + boxSize, y + boxSize)
        parts.append(part)

if not os.path.exists("./out"):
    os.makedirs("./out")

nodes = []
with open('streets.json') as json_data:
    streets = json.load(json_data)
    for street in streets:
        nodes.append((street[0], street[1]))

streets = []
for idx, node in enumerate(nodes):
    if idx > 0:
        streets.append((nodes[idx-1], node))

def toParametricLine(a, b):
    return (a, (b[0] - a[0], b[1] - a[1]))

# https://stackoverflow.com/questions/4977491/determining-if-two-line-segments-intersect/4977569#4977569
def lineSegmentsIntersect(line1, line2):
    ((x00, y00), (x01, y01)) = toParametricLine(line1[0], line1[1])
    ((x10, y10), (x11, y11)) = toParametricLine(line2[0], line2[1])
    d = x11 * y01 - x01 * y11
    if d == 0:
        return False
    s = ((x00 - x10) * y01 - (y00 - y10) * x01) / d
    t = -(-(x00 - x10) * y11 + (y00 - y10) * x11) / d
    return s >= 0 and s <= 1 and t >= 0 and t <= 1

def isPointInBox(p, box):
    xmin = min(box[0][0], box[1][0])
    xmax = max(box[0][0], box[1][0])
    ymin = min(box[0][1], box[1][1])
    ymax = max(box[0][1], box[1][1])
    return p[0] > xmin and p[0] < xmax and p[1] > ymin and p[1] < ymax

def lineSegmentContained(line, box):
    return isPointInBox(line[0], box) or isPointInBox(line[1], box)

def getBoundingLineSegments(a, b):
    return [
        (a, (a[0], b[1])),
        (a, (b[0], a[1])),
        ((a[0], b[1]), b),
        ((b[0], a[1]), b)
    ]

def transformPointToMapCoordinates(p):
    return (
        p[0] - mapOffset[0],
        ysize - (p[1] - mapOffset[1])
    )

def transformStreetToMapCoordinates(street):
    return (
        transformPointToMapCoordinates(street[0]),
        transformPointToMapCoordinates(street[1])
    )

for i, part in enumerate(parts):
    intersects = False
    for street in streets:
        transformedStreet = transformStreetToMapCoordinates(street)
        if lineSegmentContained(transformedStreet, (part['a'], part['b'])):
            intersects = True
            break
        
        for segment in getBoundingLineSegments(part['a'], part['b']):
            if lineSegmentsIntersect(transformedStreet, segment):
                intersects = True
                break
        
        if intersects:
            break
    
    if intersects:
        part['part'].save("./out/part" + str(i) + ".png", "PNG")
    else:
        print("skipping part %s, it does not intersect any streets" % i)
