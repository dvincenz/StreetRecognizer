import argparse

from osmdataprovider import Provider
from osmdataprovider.OsmDataProviderConfig import OsmDataProviderConfig

def _parse_args():
    parser = argparse.ArgumentParser(description='Generates prediction data for the micro model.')
    parser.add_argument('-o', '--output', type=str, default='../data/in/micro', help='directory path to place the generated training images')
    parser.add_argument('--osm-path', type=str, default='../data/in/osm', help='directory path to read/write OSM data to/from')
    parser.add_argument('--num-threads', type=int, help='maximum number of threads to run concurrently (default: unlimited)')
    parser.add_argument('-p', '--pbf', type=str, help='OSM PBF extract used as input, obtained from e.g. https://planet.osm.ch/')
    parser.add_argument('--sample-size', type=int, default=32, help='size in pixels of the sample images taken at each point (default: 32)')
    parser.add_argument('--sample-number', type=int, default=3, help='number of samples per way (default 3)')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose output')
    return vars(parser.parse_args())

def run():
    args = _parse_args()

# 0) Export all unlabeled ways to geojson
    if args['pbf']:
        osm_data_provider = Provider(config=OsmDataProviderConfig(
            output_path=args['osm_path'],
            pbf_path=args['pbf']
        ))
        osm_data_provider.export_unlabeled_ways_from_pbf(
            output_file='unlabeled-ways.json'
        )
    else:
        print("--pbf not provided; skipping OSM export")

# 1) TODO: Create sample images of all ways (or subset thereof)

if __name__ == "__main__":
    run()
