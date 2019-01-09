### This file generates the training and test data set used with our micro model.
### Inspired by CIFAR-10, this generates 60k 32x32 pixel images labeled across
### 10 classes. There are 6k images per class.

import argparse
from subprocess import call
import threading

# According to http://taginfo.openstreetmap.ch/keys/surface#values, the 10 most
# labeled surfaces are: asphalt, gravel, paved, ground, unpaved, grass, dirt, concrete, compacted, fine_gravel
# fine_gravel has 2'424 labeled highways, therefor taking 3 random samples from every highway suffices to
# obtain 6k images in total for every class.

CLASSES = [
    'asphalt',
    'gravel',
    'paved',
    'ground',
    'unpaved',
    'grass',
    'dirt',
    'concrete',
    'compacted',
    'fine_gravel'
]

# Obtained from https://planet.osm.ch/
OSM_PBF_FILE = "../data/in/osm/switzerland-exact.osm.pbf"

def parse_args():
    parser = argparse.ArgumentParser(description='Generates training (and test) data for the micro model.')
    # parser.add_argument('tiledata', metavar='TILEDATA', type=str, help='path to the JSON containing the tile data for an ortho photo')
    # parser.add_argument('datasource', metavar='DB', type=str, help='path to the database file')
    # parser.add_argument('--clean', action='store_true', help='Cleans (drops) the database and re-initializes it')
    return vars(parser.parse_args())

class OsmosisThread (threading.Thread):
    def __init__(self, name, surface):
        threading.Thread.__init__(self)
        self.name = name
        self.surface = surface

    def run(self):
        print("[{0}] Starting...".format(self.name))
        osm_xml_file = "../data/in/osm/training-data-micro-{0}.osm".format(self.surface)
        osm_geojson_file = "../data/in/osm/training-data-micro-{0}.json".format(self.surface)
        print("[{0}] Reading ways with surface {1}...".format(self.name, self.surface))
        call(["osmosis",
            "--read-pbf", OSM_PBF_FILE,
            "--tf", "accept-ways", "surface={0}".format(self.surface),
            "--tf", "reject-relations",
            "--used-node",
            "--write-xml", osm_xml_file])
        with open(osm_geojson_file, 'w') as file:
                call(["osmtogeojson", osm_xml_file], stdout=file)
        print("[{0}] Exiting...".format(self.name))

# TODO: Move this into OsmDataProvider
def get_labeled_ways():
    threads = []
    for surface in CLASSES:
        thread = OsmosisThread(name="Thread-{0}".format(surface), surface=surface)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Done!")

def run():
    parse_args()

# 1) Randomly select 2'000 ways among all labeled ways in Switzerland
    print("Reading labeled ways from Switzerland extract, this might take several minutes...")
    get_labeled_ways()

# 2) Pick 3 points along every way

# 3) Take a sample image at the selected points

# 4) Store the images in labeled directories

if __name__ == "__main__":
    run()
