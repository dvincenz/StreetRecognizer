import math


class SlicerConfig:
    def __init__(self, tile_size: int, base_overlap_factor: float):
        self.tile_size = tile_size
        self.base_overlap_factor = base_overlap_factor
        self.x = DimensionConfig(
            tile_size=tile_size, base_overlap_factor=base_overlap_factor)
        self.y = DimensionConfig(
            tile_size=tile_size, base_overlap_factor=base_overlap_factor)

    def print_debug_information(self, size: (int, int)):
        width, height = size
        num_tiles_x = self.x.get_num_tiles(width)
        num_tiles_y = self.y.get_num_tiles(height)
        print('X overlap: ' + self.x.get_overlap_string(width))
        print('Y overlap: ' + self.y.get_overlap_string(height))
        print('Expected Tiles: ' + str(num_tiles_x) + 'x' + str(num_tiles_y)
              + ' (' + str(num_tiles_x * num_tiles_y) + ')')
        print('The current settings produce the following error, due to rounding pixels per tile:')
        print('    X: ' + self.x.get_rounding_error_string(width))
        print('    Y: ' + self.y.get_rounding_error_string(height))


class DimensionConfig:
    def __init__(self, tile_size: int, base_overlap_factor: float):
        self.tile_size = tile_size
        self.base_overlap = tile_size * base_overlap_factor

    def get_num_tiles(self, size: int):
        return math.floor((size - self.base_overlap) / (self.tile_size - self.base_overlap) + 0.5)

    def get_overlap_offset(self, size: int):
        num_tiles = self.get_num_tiles(size)
        return math.ceil((size - num_tiles * self.tile_size) / (1 - num_tiles))

    def get_overlap_string(self, size: int):
        return str(self.get_overlap_offset(size)) + " ({0:.2%})".format(self.get_overlap_offset(size) / self.tile_size)

    def get_rounding_error_string(self, size: int):
        num_tiles = self.get_num_tiles(size)
        overlap_offset = self.get_overlap_offset(size)
        actual_size = num_tiles * (self.tile_size - overlap_offset) + overlap_offset
        if actual_size > size:
            return str(actual_size - size) + 'px of "black borders" ({0:.4%})'.format((actual_size - size) / size)

        if actual_size < size:
            return str(size - actual_size) + 'px missing ({0:.4%})'.format((size - actual_size) / size)

        return 'none!'
