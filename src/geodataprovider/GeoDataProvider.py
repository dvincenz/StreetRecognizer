from osgeo import gdal

from geoutils.Types import GeoPoint
from geoutils.Types import GeoRect

class GeoDataProvider:
    def __init__(self, geo_tiff_path: str):
        self.geo_tiff_path = geo_tiff_path
        self.data_source = gdal.Open(self.geo_tiff_path)

        # GDAL affine transform parameters, According to gdal documentation xoff/yoff are image left corner, a/e are pixel wight/height and b/d is rotation and is zero if image is north up.
        self._xoff, self._a, self._b, self._yoff, self._d, self._e = self.data_source.GetGeoTransform()
        self._xsize = self.data_source.RasterXSize
        self._ysize = self.data_source.RasterYSize

    def get_pixel_size(self) -> (int, int):
        return (self._xsize, self._ysize)

    def get_bounding_rect(self) -> GeoRect:
        return GeoRect(
            a=self.pixel_to_geo_point(0, 0),
            b=self.pixel_to_geo_point(self._xsize, self._ysize)
        )

    def pixel_to_geo_point(self, x, y) -> GeoPoint:
        """Returns global coordinates from pixel x, y coords"""
        east = self._a * x + self._b * y + self._xoff
        north = self._d * x + self._e * y + self._yoff
        return GeoPoint(east=east, north=north)

    def geo_point_to_pixel(self, point: GeoPoint) -> (int, int):
        """Returns pixel x, y coords from global coordinates"""
        y = (self._d * (point.east - self._xoff) + self._a * (self._yoff - point.north)
            ) / (self._b * self._d - self._a * self._e)
        x = (point.east - self._b * y - self._xoff) / self._a
        return (x, y)

    def get_lower_left_coordinates(self):
        return self.pixel_to_geo_point(0, self.data_source.RasterYSize)

    def get_upper_right_coordinates(self):
        return self.pixel_to_geo_point(self.data_source.RasterXSize, 0)

    def get_pixel_width(self):
        return self._a
    def get_pixel_hight(self):
        return self._e
