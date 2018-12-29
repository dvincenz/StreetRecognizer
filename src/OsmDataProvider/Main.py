import sys
from OsmDataProvider import OsmDataProvider
import argparse
from OsmDataProviderConfig import OsmDataProviderConfig

def parse_args():
    parser = argparse.ArgumentParser(description='get osm data for a wgs84 geotiff or custom coordinate box')
    parser.add_argument('target', metavar='PATH', type=str, help='output path to write geojson files')
    parser.add_argument('-p', '--imagepath', metavar='IMAGEPATH', type=str, help='path to a geotiff wgs84 image')
    parser.add_argument('-ll', '--lowerleft', metavar='LOWERLEFT', type=str, help='lower left coordinates (E, N)')
    parser.add_argument('-ur', '--upperright', metavar='UPPERRIGHT', type=str, help='upper right coordinates (E, N)')
    return parser.parse_args()

def main():
    args = parse_args()
    #todo: defining buffer for other types of ways. may export config in config file
    buffer_definitons = {}
    buffer_definitons["unclassified"] = 0.000023
    buffer_definitons["tertiary"] = 0.000030
    buffer_definitons["footway"] = 0.000013
    buffer_definitons["path"] = 0.000013
    buffer_definitons["track"] = 0.000020
    config = OsmDataProviderConfig(output_path = args.target, buffer = buffer_definitons)
    provider = OsmDataProvider(config)
    if args.imagepath:
        return provider.export_ways_by_image(args.imagepath)
    if args.lowerleft and args.upperright:
        return provider.export_ways_by_coordinates(args.lowerleft, args.upperright)
    raise ValueError('Image path or coordinates need to be set as argument. Use -h for more information')

if __name__ == "__main__":
    main()
