import argparse
import json
import os
from PIL import Image

import osmdataprovider
from slicer.Slicer import Slicer
from slicer.SlicerConfig import SlicerConfig

def _parse_args():
    parser = argparse.ArgumentParser(description='Slice an image into equal, quadratic, optionally overlapping tiles.')
    parser.add_argument('image', metavar='IMAGE', type=str, help='the image to slice')
    parser.add_argument('target', metavar='TARGET', nargs='?', type=str, default='.', help='directory path to write the tiles to')
    parser.add_argument('-s', '--size', metavar='SIZE', type=int, default=1024, help='size in pixels of a single tile (default: 1024)')
    parser.add_argument('-o', '--overlap', metavar='OVERLAP', type=float, default=0.2, help='percentage of baseline tile overlapping (default: 0.2)')
    parser.add_argument('-d', '--osm-data', metavar='OSM_DATA', type=str, help='geojson file containing the osm data for the image to slice')
    return parser.parse_args()

def _get_osm_data(args):
    if args.osm_data:
        with open(args.osm_data, 'r') as file:
            return json.load(file)
    else:
        osmdataprovider.Provider(target='../data/in/osm/vector', imagepath=args.image)
        image_name = os.path.splitext(os.path.basename(args.image))[0]
        with open(os.path.join('../data/in/osm/vector', image_name + '_line.json'), 'r') as file:
            return json.load(file)

def main():
    args = _parse_args()

    Image.MAX_IMAGE_PIXELS = 17500 * 12000

    # produces 294 tiles for orthophotos of size 17'500 x 12'000 px, with overlap of 20%
    config = SlicerConfig(tile_size=args.size, base_overlap_factor=args.overlap)
    slicer = Slicer(
        image_path=os.path.dirname(args.image),
        image_name=os.path.basename(args.image),
        osm_data=_get_osm_data(args))

    config.print_debug_information(slicer.image.size)

    tiles = slicer.slice(config)
    slicer.save_tiles(tiles=tiles, config=config, out_path=args.target)

if __name__ == "__main__":
    main()
