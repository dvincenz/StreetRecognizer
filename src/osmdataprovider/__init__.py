import argparse

from osmdataprovider.OsmDataProvider import OsmDataProvider
from osmdataprovider.OsmDataProviderConfig import OsmDataProviderConfig

def parse_args():
    parser = argparse.ArgumentParser(description='get osm data for a wgs84 geotiff or custom coordinate box')
    parser.add_argument('target', metavar='PATH', type=str, help='output path to write geojson files')
    parser.add_argument('-p', '--imagepath', metavar='IMAGEPATH', type=str, help='path to a geotiff wgs84 image')
    parser.add_argument('-ll', '--lowerleft', metavar='LOWERLEFT', type=str, help='lower left coordinates (E, N)')
    parser.add_argument('-ur', '--upperright', metavar='UPPERRIGHT', type=str, help='upper right coordinates (E, N)')
    return vars(parser.parse_args())

def run():
    configs = parse_args()
    Provider(**configs)

def Provider(**kwargs):
    if kwargs.get("config"):
        config = kwargs.get("config")
        return OsmDataProvider(config)
    config = OsmDataProviderConfig(output_path = kwargs.get("target"))
    provider = OsmDataProvider(config)
    if kwargs.get("imagepath"):
        provider.export_ways_by_image(kwargs.get("imagepath"))
        print("not defined buffer " + str(provider.not_defined_buffer))
        return
    if kwargs.get("lowerleft") and kwargs.get("upperright"):
        provider.export_ways_by_coordinates(kwargs.get("lowerleft"), kwargs.get("upperright"))
        return
    raise ValueError('Image path or coordinates need to be set as argument. Use -h for more information')

if __name__ == "__main__":
    Provider()
