import json
import os

from PIL import Image

# X1 = 2642913.3763101
# X2 = 2722086.6236899
# Y1 = 1231766.0165963
# Y2 = 1273233.9834037
# BBOX = "{},{},{},{}".format(X1, Y1, X2, Y2)
# IMAGE_WIDTH = 512
# IMAGE_HEIGHT = 512
# WMS_URL = "http://wms.zh.ch/OrthoZHWMS?LAYERS=orthophotos&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&FORMAT=image%2Fjpeg&CRS=EPSG%3A2056&SRS=EPSG%3A2056&BBOX={}&WIDTH={}&HEIGHT={}".format(
#     BBOX, IMAGE_WIDTH, IMAGE_HEIGHT)
# print(WMS_URL)

IMAGE_NAME = '1032-432.tif'
FILE = './in/Ortho/' + IMAGE_NAME

Image.MAX_IMAGE_PIXELS = 328125000
ORTHOPHOTO = Image.open(FILE)

BOX_SIZE = 1024 # produces 330 tiles for orthophotos of size 21'875 x 15'000 px
MAP_OFFSET = (0, 0)

X_SIZE, Y_SIZE = ORTHOPHOTO.size

PARTS = []
for x in range(0, X_SIZE, BOX_SIZE):
    for y in range(0, Y_SIZE, BOX_SIZE):
        part = {}
        part['part'] = ORTHOPHOTO.crop((x, y, x + BOX_SIZE, y + BOX_SIZE))
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


OUT_DIRECTORY = "./out/" + IMAGE_NAME
if not os.path.exists(OUT_DIRECTORY):
    os.mkdir(OUT_DIRECTORY)

for i, part in enumerate(PARTS):
    partName = "{}/{:0>3d},{:0>3d}.png".format(
        OUT_DIRECTORY, part['a'][1], part['a'][0])
    part['part'].save(partName, "PNG")
