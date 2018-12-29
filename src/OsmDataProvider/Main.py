import sys
from OsmDataProvider import OsmDataProvider
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='get osm data for a wgs84 geotiff or custom coordinate box')
    parser.add_argument('path', metavar='PATH', type=str, help='output geojson file path')
    parser.add_argument('-p', '--imagepath', metavar='IMAGEPATH', type=str, help='path to a geotiff wgs84 image')
    parser.add_argument('-ll', '--lowerleft', metavar='LOWERLEFT', type=str, help='lower left coordinates (E, N)')
    parser.add_argument('-ur', '--upperright', metavar='UPPERRIGHT', type=str, help='upper right coordinates (E, N)')
    return parser.parse_args()

def main():
    args = parse_args()
    print(args)
    provider = OsmDataProvider()
    if args.imagepath:
        return provider.get_ways_by_image(args.path, args.imagepath)
    if args.lowerleft and args.upperright:
        return provider.get_ways_by_coordinates(args.path, args.lowerleft, args.upperright)
    raise ValueError('Image path or coordinates need to be set as argument. Use -h for more information')

if __name__ == "__main__":
    main()
