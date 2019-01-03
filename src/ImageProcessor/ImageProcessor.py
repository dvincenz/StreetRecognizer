from osgeo import gdal, ogr
from Utils import get_corner_coordinates
import os
import subprocess
from ImageProcessorConfig import ImageProcessorConfig


class ImageProcessor:
    def __init__(self, config: ImageProcessorConfig):
        self.config = config

    def get_raster_from_geojson(self, geojson_path:str, pixel_width: int, pixel_height: int):
        file_name = os.path.splitext(os.path.basename(geojson_path))[0] + "_raster.tif" 
        geojson = ogr.Open(geojson_path)
        jsonlayer = geojson.GetLayer()
        x_min, x_max, y_min, y_max = jsonlayer.GetExtent()

        cols = int((x_max - x_min) / pixel_width)
        rows = int((y_max - y_min) / pixel_height)      

        target_image = gdal.GetDriverByName('GTiff').Create(os.path.join(self.config.output_path, file_name), cols, rows*-1, 1, gdal.GDT_Byte) 
        target_image.SetGeoTransform((x_min, pixel_width, 0, y_max, 0, pixel_height))
        # todo projection not as string
        target_image.SetProjection('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]')
        gdal.RasterizeLayer(target_image, [1], jsonlayer, burn_values=[255])
        target_image.FlushCache()
        target_image = None
        return os.path.join(self.config.output_path, file_name)



    def cut_geo_image(self, base_image_path: str, to_cut_image_path: str):
        coordinates = get_corner_coordinates(base_image_path)
        file_name = os.path.splitext(os.path.basename(base_image_path))[0] + "_cut_raster.tif"
        # todo may use python wrapper and not command line interface
        bash_command = "gdalwarp -te {0} {1} {2} {3} {4} {5}".format(
                coordinates[1][0], 
                coordinates[1][1], 
                coordinates[3][0], 
                coordinates[0][1],
                to_cut_image_path,
                os.path.join(self.config.output_path, file_name))
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate() 
        return os.path.join(self.config.output_path, file_name)
            
    def get_pixel_width_heigh(self, image_path: str):
        image = gdal.Open(image_path)
        image_tranformation = image.GetGeoTransform()
        return (image_tranformation[1], image_tranformation[5])
