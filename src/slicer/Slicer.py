import json
import math
import os
import shutil

from PIL import Image
from geodataprovider.GeoDataProvider import GeoDataProvider
from slicer.SlicerConfig import SlicerConfig


class Tile:
    def __init__(self, image: Image, coords: ((int, int), (int, int))):
        self.image = image
        top_left, bottom_right = coords
        self.left, self.top = top_left
        self.right, self.bottom = bottom_right


class Slicer:
    def __init__(self, image_path: str, image_name: str, osm_data: dict):
        self.image_name = image_name
        self.image = Image.open(os.path.join(image_path, image_name))
        self.osm_data = osm_data

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
                tiles.append(self._slice_tile(config=config, x=x, y=y))
                self._print_progress(len(tiles), max_tiles)

        return tiles

    def _slice_tile(self, config: SlicerConfig, x: int, y: int):
        left = x
        top = y
        right = left + config.tile_size
        bottom = top + config.tile_size
        tile_image = self.image.crop((left, top, right, bottom))
        tile = Tile(image=tile_image, coords=((left, top), (right, bottom)))
        return tile

    def save_tiles(self, tiles: [Tile], config: SlicerConfig, out_path: str, remove_existing=True):
        print('saving... (to ' + os.path.abspath(out_path) + ')')

        out_dir = os.path.join(out_path, os.path.splitext(self.image_name)[0])

        if remove_existing and os.path.exists(out_dir):
            shutil.rmtree(out_dir, ignore_errors=True)

        os.makedirs(out_dir, exist_ok=True)

        geo_data_provider = GeoDataProvider(geo_tiff_path=self.image.filename)

        data = self._init_ortho_data(
            geo_data_provider=geo_data_provider, config=config)

        # TODO: This should be multi-threadable (with non-deterministic order of tiles in the data-array)
        for i, tile in enumerate(tiles):
            data['tiles'].append(self._save_tile(
                tile=tile, out_dir=out_dir, geo_data_provider=geo_data_provider))
            self._print_progress(i+1, len(tiles))

        with open(out_dir + '.json', 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4)

    def _init_ortho_data(self, geo_data_provider: GeoDataProvider, config: SlicerConfig):
        width, height = self.image.size
        c_left, c_top = geo_data_provider.pixel_to_coords(0, 0)
        c_right, c_bottom = geo_data_provider.pixel_to_coords(width, height)

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
        return data

    @staticmethod
    def _save_tile(tile: Tile, out_dir: str, geo_data_provider: GeoDataProvider):
        tile_name = "{:0>3d},{:0>3d}.png".format(tile.top, tile.left)
        tile.image.save(os.path.join(out_dir, tile_name), "PNG")

        c_left, c_top = geo_data_provider.pixel_to_coords(
            tile.left, tile.top)
        c_right, c_bottom = geo_data_provider.pixel_to_coords(
            tile.right, tile.bottom)

        # FIXME: This is slow AF, should probably only get this data once per orthofoto and calculate for tiles manually
        #ways = osm_data_provider.get_ways_by_coordinates(lower_left=[c_left, c_bottom], upper_right=[c_right, c_top])
        ways = []

        return {
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
        }

    @staticmethod
    def _print_progress(num_processed: int, num_total: int):
        if num_processed % 50 == 0:
            print('  {0:d}/{1:d} ({2:.1%})'.format(
                num_processed,
                num_total,
                num_processed / num_total))
