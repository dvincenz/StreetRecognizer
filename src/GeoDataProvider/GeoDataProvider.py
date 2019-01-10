from osgeo import gdal

from geoutils.Types import GeoPoint

class GeoDataProvider:
    def __init__(self, geo_tiff_path: str):
        self.geo_tiff_path = geo_tiff_path
        self.data_source = gdal.Open(self.geo_tiff_path)

        # GDAL affine transform parameters, According to gdal documentation xoff/yoff are image left corner, a/e are pixel wight/height and b/d is rotation and is zero if image is north up.
        self._xoff, self._a, self._b, self._yoff, self._d, self._e = self.data_source.GetGeoTransform()

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
