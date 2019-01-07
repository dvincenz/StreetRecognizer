from osgeo import gdal

from geoutils.Types import GeoPoint

class GeoDataProvider:
    def __init__(self, geo_tiff_path: str):
        self.geo_tiff_path = geo_tiff_path
        self.data_source = gdal.Open(self.geo_tiff_path)

        # GDAL affine transform parameters, According to gdal documentation xoff/yoff are image left corner, a/e are pixel wight/height and b/d is rotation and is zero if image is north up.
        self._xoff, self._a, self._b, self._yoff, self._d, self._e = self.data_source.GetGeoTransform()

    def pixel_to_geo_point(self, x, y):
        """Returns global coordinates from pixel x, y coords"""
        east = self._a * x + self._b * y + self._xoff
        north = self._d * x + self._e * y + self._yoff
        return GeoPoint(east=east, north=north)
