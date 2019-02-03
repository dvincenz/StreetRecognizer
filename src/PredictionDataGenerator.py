import argparse
import os

import geojson
import progressbar

from geoutils.RandomImageProvider import RandomImageProvider
from osmdataprovider import Provider
from osmdataprovider.OsmDataProviderConfig import OsmDataProviderConfig

def _parse_args():
    parser = argparse.ArgumentParser(description='Generates prediction data for the micro model.')
    parser.add_argument('-o', '--output', type=str, default='../data/in/micro-predict', help='directory path to place the generated prediction images')
    parser.add_argument('--meta-data', type=str, default='../data/metadata.db', help='path to the metadata sqlite database file')
    parser.add_argument('--osm-path', type=str, default='../data/in/osm', help='directory path to read/write OSM data to/from')
    parser.add_argument('-n', '--number', type=int, help='maximum number of streets to generate prediction data for (default: unlimited)')
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
            output_file='unlabeled-ways-filtered.json'
        )
    else:
        print("--pbf not provided; skipping OSM export")

# 1) Create sample images of all ways (or subset thereof)
    geojson_file = os.path.join(args['osm_path'], 'unlabeled-ways-filtered.json')
    with open(geojson_file, mode='r', encoding='UTF-8') as file:
        geojson_data = geojson.load(file)

    line_strings = []
    for way in geojson_data.features:
        if isinstance(way.geometry, geojson.LineString):
            line_strings.append(way)

    widgets = [
        ' [', os.path.basename(os.path.normpath(args['output'])), '] ',
        progressbar.Percentage(), ' ',
        progressbar.SimpleProgress(), ' ',
        progressbar.Bar(),
        progressbar.Timer(), ' ',
        progressbar.ETA()
    ]

    maximum_lines = len(line_strings)

    if args['number']:
        maximum_lines = min(args['number'], maximum_lines)

    with progressbar.ProgressBar(max_value=len(line_strings), widgets=widgets) as bar:
        # TODO: This loop is slow AF, since we always only pass 1 street to the RandomImageProvider,
        # which makes it impossible to optimize loading of the Orthos across streets.
        for i in range(0, maximum_lines):
            line_string = line_strings[i]
            with RandomImageProvider(
                    image_size=args['sample_size'],
                    out_path=os.path.join(args['output'], line_string.id[4:]),
                    metadata=args['meta_data'],
                    verbose=args['verbose']
            ) as rip:
                rip.get_random_images(
                    number=args['sample_number'],
                    line_strings=[line_string],
                    show_progress=True
                )
            bar.update(i+1)

if __name__ == "__main__":
    run()
