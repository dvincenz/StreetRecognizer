import json
import math
import os
import shutil


from PIL import Image
from geodataprovider.GeoDataProvider import GeoDataProvider
from osmdataprovider.OsmDataProvider import OsmDataProvider
from osmdataprovider.OsmDataProviderConfig import OsmDataProviderConfig
from slicer.SlicerConfig import SlicerConfig


class Tile:
    def __init__(self, image: Image, coords: ((int, int), (int, int))):
        self.image = image
        top_left, bottom_right = coords
        self.left, self.top = top_left
        self.right, self.bottom = bottom_right


class Slicer:
    def __init__(self, image_path: str, image_name: str):
        self.image_name = image_name
        self.image = Image.open(os.path.join(image_path, image_name))

    def slice(self, config: SlicerConfig):
        print('slicing...')

        width, height = self.image.size
        step_x = config.tile_size - config.x.get_overlap_offset(width)
        step_y = config.tile_size - config.y.get_overlap_offset(height)
        max_x = width - math.floor(config.tile_size / 2)
        max_y = height - math.floor(config.tile_size / 2)
        max_tiles = math.ceil(max_x / step_x) * math.ceil(max_y / step_y)

        tiles = []
        # TODO: This might be multi-threadable, depending on behavior of image.crop, however this isn't too slow, anyway
        for x in range(0, max_x, step_x):
            for y in range(0, max_y, step_y):
                left = x
                top = y
                right = left + config.tile_size
                bottom = top + config.tile_size
                tile_image = self.image.crop((left, top, right, bottom))
                tile = Tile(image=tile_image, coords=(
                    (left, top), (right, bottom)))
                tiles.append(tile)

                if len(tiles) % 50 == 0:
                    print('  {0:d}/{1:d} ({2:.1%})'.format(len(tiles),
                                                           max_tiles, len(tiles) / max_tiles))
        return tiles

    def save_tiles(self, tiles: [Tile], config: SlicerConfig, out_path: str, remove_existing=True):
        print('saving... (to ' + os.path.abspath(out_path) + ')')

        out_dir = os.path.join(out_path, os.path.splitext(self.image_name)[0])

        if remove_existing and os.path.exists(out_dir):
            shutil.rmtree(out_dir, ignore_errors=True)

        os.makedirs(out_dir, exist_ok=True)

        width, height = self.image.size

        geo_data_provider = GeoDataProvider(geo_tiff_path=self.image.filename)
        c_left, c_top = geo_data_provider.pixel_to_coords(0, 0)
        c_right, c_bottom = geo_data_provider.pixel_to_coords(width, height)

        osm_config = OsmDataProviderConfig(output_path=None)
        osm_data_provider = OsmDataProvider(config=osm_config)

        data = {}
        data['imageName'] = self.image_name
        data['imageSize'] = {
            'width': width,
            'height': height
        }
        data['wgs84'] = {
            'top': c_top,
            'left': c_left,
            'bottom': c_bottom,
            'right': c_right
        }
        data['tileConfig'] = {
            'tileSize': config.tile_size,
            'overlapPixelsX': config.x.get_overlap_offset(width),
            'overlapPixelsY': config.y.get_overlap_offset(height),
            'overlapFactorX': config.x.get_overlap_offset(width) / config.tile_size,
            'overlapFactorY': config.y.get_overlap_offset(height) / config.tile_size,
            'numTilesX': config.x.get_num_tiles(width),
            'numTilesY': config.y.get_num_tiles(height)
        }
        data['tileDirectory'] = os.path.splitext(self.image_name)[0]
        data['tiles'] = []

        # TODO: This should be multi-threadable (with non-deterministic order of tiles in the data-array)
        for i, tile in enumerate(tiles):
            tile_name = "{:0>3d},{:0>3d}.png".format(tile.top, tile.left)
            tile.image.save(os.path.join(out_dir, tile_name), "PNG")

            c_left, c_top = geo_data_provider.pixel_to_coords(
                tile.left, tile.top)
            c_right, c_bottom = geo_data_provider.pixel_to_coords(
                tile.right, tile.bottom)

            # FIXME: This is slow AF, should probably only get this data once per orthofoto and calculate for tiles manually
            #ways = osm_data_provider.get_ways_by_coordinates(lower_left=[c_left, c_bottom], upper_right=[c_right, c_top])
            ways = []

            data['tiles'].append({
                'tileName': tile_name,
                'pixels': {
                    'top': tile.top,
                    'left': tile.left,
                    'bottom': tile.bottom,
                    'right': tile.right
                },
                'wgs84': {
                    'top': c_top,
                    'left': c_left,
                    'bottom': c_bottom,
                    'right': c_right
                },
                'ways': {
                    'features': ways,
                    'type': 'FeatureCollection'
                }
            })

            if (i+1) % 50 == 0:
                print('  {0:d}/{1:d} ({2:.1%})'.format((i+1),
                                                       len(tiles), (i+1) / len(tiles)))

        with open(out_dir + '.json', 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4)