import argparse
import os
from PIL import Image

from Slicer import Slicer
from SlicerConfig import SlicerConfig

def parse_args():
    parser = argparse.ArgumentParser(description='Slice an image into equal, quadratic, optionally overlapping tiles.')
    parser.add_argument('image', metavar='IMAGE', type=str, help='the image to slice')
    parser.add_argument('target', metavar='TARGET', nargs='?', type=str, default='.', help='directory path to write the tiles to')
    parser.add_argument('-s', '--size', metavar='SIZE', type=int, default=1024, help='size in pixels of a single tile (default: 1024)')
    parser.add_argument('-o', '--overlap', metavar='OVERLAP', type=float, default=0.2, help='percentage of baseline tile overlapping (default: 0.2)')
    return parser.parse_args()

def main():
    args = parse_args()

    Image.MAX_IMAGE_PIXELS = 17500 * 12000

    # produces 294 tiles for orthophotos of size 17'500 x 12'000 px, with overlap of 20%
    config = SlicerConfig(tile_size=args.size, base_overlap_factor=args.overlap)
    slicer = Slicer(image_path=os.path.dirname(args.image), image_name=os.path.basename(args.image))

    config.print_debug_information(slicer.image.size)

    tiles = slicer.slice(config)
    slicer.save_tiles(tiles=tiles, config=config, out_path=args.target)

    # This stuff will be re-used for JSON and GeoData metadata
    # MAP_OFFSET = (0, 0)
    # NODES = []
    # with open('streets.json') as json_data:
    #     STREETS = json.load(json_data)
    #     for street in STREETS:
    #         NODES.append((street[0], street[1]))

    # STREETS = []
    # for idx, node in enumerate(NODES):
    #     if idx > 0:
    #         STREETS.append((NODES[idx-1], node))

    # def toParametricLine(a, b):
    #     return (a, (b[0] - a[0], b[1] - a[1]))

    # https://stackoverflow.com/questions/4977491/determining-if-two-line-segments-intersect/4977569#4977569

    # def lineSegmentsIntersect(line1, line2):
    #     ((x00, y00), (x01, y01)) = toParametricLine(line1[0], line1[1])
    #     ((x10, y10), (x11, y11)) = toParametricLine(line2[0], line2[1])
    #     d = x11 * y01 - x01 * y11
    #     if d == 0:
    #         return False
    #     s = ((x00 - x10) * y01 - (y00 - y10) * x01) / d
    #     t = -(-(x00 - x10) * y11 + (y00 - y10) * x11) / d
    #     return s >= 0 and s <= 1 and t >= 0 and t <= 1

    # def isPointInBox(p, box):
    #     xmin = min(box[0][0], box[1][0])
    #     xmax = max(box[0][0], box[1][0])
    #     ymin = min(box[0][1], box[1][1])
    #     ymax = max(box[0][1], box[1][1])
    #     return p[0] > xmin and p[0] < xmax and p[1] > ymin and p[1] < ymax

    # def lineSegmentContained(line, box):
    #     return isPointInBox(line[0], box) or isPointInBox(line[1], box)

    # def getBoundingLineSegments(a, b):
    #     return [
    #         (a, (a[0], b[1])),
    #         (a, (b[0], a[1])),
    #         ((a[0], b[1]), b),
    #         ((b[0], a[1]), b)
    #     ]

    # def transformPointToMapCoordinates(p):
    #     return (
    #         p[0] - MAP_OFFSET[0],
    #         Y_SIZE - (p[1] - MAP_OFFSET[1])
    #     )

    # def transformStreetToMapCoordinates(streetToTransform):
    #     return (
    #         transformPointToMapCoordinates(streetToTransform[0]),
    #         transformPointToMapCoordinates(streetToTransform[1])
    #     )

if __name__ == "__main__":
    main()
