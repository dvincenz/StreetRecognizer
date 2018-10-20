import json
import os

from PIL import Image

FILE = "./DummyMap.png"
MAP = Image.open(FILE)

BOX_SIZE = 100
MAP_OFFSET = (100, 100)

X_SIZE, Y_SIZE = MAP.size

PARTS = []
for x in range(0, X_SIZE, BOX_SIZE):
    for y in range(0, Y_SIZE, BOX_SIZE):
        part = {}
        part['part'] = MAP.crop((x, y, x + BOX_SIZE, y + BOX_SIZE))
        part['a'] = (x, y)
        part['b'] = (x + BOX_SIZE, y + BOX_SIZE)
        PARTS.append(part)

if not os.path.exists("./out"):
    os.makedirs("./out")

NODES = []
with open('streets.json') as json_data:
    STREETS = json.load(json_data)
    for street in STREETS:
        NODES.append((street[0], street[1]))

STREETS = []
for idx, node in enumerate(NODES):
    if idx > 0:
        STREETS.append((NODES[idx-1], node))

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
        p[0] - MAP_OFFSET[0],
        Y_SIZE - (p[1] - MAP_OFFSET[1])
    )

def transformStreetToMapCoordinates(streetToTransform):
    return (
        transformPointToMapCoordinates(streetToTransform[0]),
        transformPointToMapCoordinates(streetToTransform[1])
    )

for i, part in enumerate(PARTS):
    intersects = False
    for street in STREETS:
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
