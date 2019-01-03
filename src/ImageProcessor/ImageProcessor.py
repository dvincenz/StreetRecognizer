from osgeo import gdal, ogr, GDALRasterizeOptions
from ImageProcessor.Utils import get_corner_coordinates
import os
import subprocess
from ImageProcessor.ImageProcessorConfig import ImageProcessorConfig


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

        target_image = gdal.GetDriverByName('GTiff').Create(os.path.join(self.config.out_path, file_name), cols, rows*-1, 1, gdal.GDT_Byte) 
        target_image.SetGeoTransform((x_min, pixel_width, 0, y_max, 0, pixel_height))
        # todo projection not as string
        target_image.SetProjection('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]')
        gdal.RasterizeLayer(target_image, [1], jsonlayer, burn_values=[255])
        target_image.FlushCache()
        target_image = None
        return os.path.join(self.config.out_path, file_name)



    def cut_geo_images(self, base_image_path: str, to_cut_image_path: str):
        coordinates = get_corner_coordinates(base_image_path)
        file_name = os.path.splitext(os.path.basename(base_image_path))[0] + "_cut_raster.tif"
        # todo may use python wrapper and not command line interface
        bash_command = "gdalwarp -te {0} {1} {2} {3} {4} {5}".format(
                coordinates[1][0], 
                coordinates[1][1], 
                coordinates[3][0], 
                coordinates[0][1],
                to_cut_image_path,
                os.path.join(self.config.out_path, file_name))
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate() 
        return os.path.join(self.config.out_path, file_name)
            
    def get_pixel_width_heigh(self, image_path: str):
        image = gdal.Open(image_path)
        image_tranformation = image.GetGeoTransform()
        return (image_tranformation[1], image_tranformation[5])












# gdal.RasterizeLayer()





# image = gdal.Open("../data/in/ortho/wgs84/DOP25_LV95_1091-23_2013_1_13.tif")
# image_tranformation = image.GetGeoTransform()


# shape = ogr.Open("../data/temp/DOP25_LV95_1091-23_2013_1_13_polygon.shp")
# geojson = ogr.Open("../data/in/osm/vector/DOP25_LV95_1091-23_2013_1_13_polygon.json")
# layer = shape.GetLayer()
# jsonlayer = geojson.GetLayer()
# pixel_width = image_tranformation[1]
# pixel_height = image_tranformation[5]


# x_min, x_max, y_min, y_max = layer.GetExtent()

# cols = int((x_max - x_min) / pixel_width)
# rows = int((y_max - y_min) / pixel_height)

# resolution = 1
# target_ds = gdal.GetDriverByName('GTiff').Create('../data/temp/1091-23x.tif', round(cols/resolution), round(rows*-1/resolution), 1, gdal.GDT_Byte) 
# target_ds.SetGeoTransform((x_min, pixel_width*resolution, 0, y_max, 0, pixel_height*resolution))
# target_ds.SetProjection('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]')
# gdal.RasterizeLayer(target_ds, [1], jsonlayer, burn_values=[255])
# target_ds.FlushCache()
# target_ds = None


# coordinates[1][1] 



#     def cut_geotiff(self, base_image_path: str, to_cut_image_path: str):
#         pixel_width, pixel_height = self.get_pixel_width_heigh(to_cut_image_path)
#         base_image_coordinate = get_corner_coordinates(base_image_path)
#         to_cut_image_coordinates = get_corner_coordinates(to_cut_image_path)
#         cut_top = -round((to_cut_image_coordinates[0][1] - base_image_coordinate[0][1]) / pixel_height)
#         cut_bottom = round((to_cut_image_coordinates[1][1] - base_image_coordinate[1][1]) / pixel_height)
#         cut_left = -round((to_cut_image_coordinates[0][0] - base_image_coordinate[0][0]) / pixel_width)
#         cut_right = round((to_cut_image_coordinates[2][0] - base_image_coordinate[2][0]) / pixel_width)
#         image_to_cut = Image.open(to_cut_image_path, 'r')
#         width, height = image_to_cut.size
#         img = image_to_cut.crop((cut_left, cut_top, width - cut_right - cut_left, height - cut_top - cut_bottom))
#         img.save('../data/in/osm/raster/temp.if', "geotiff")

# base_image_path = '../data/in/ortho/wgs84/DOP25_LV95_1091-23_2013_1_13.tif'
# to_cut_image_path = '../data/temp/1091-23x.tif'




# def get_pixel_width_heigh(image_path: str):
#         image = gdal.Open(image_path)
#         image_tranformation = image.GetGeoTransform()
#         return (image_tranformation[1], image_tranformation[5])


# base_image = gdal.Open(base_image_path)
# to_cut_image = gdal.Open(to_cut_image_path)

# base_image







#     def _get_corner_coordinates(transformation: [], cols: int, rows: int):
#         upper_left = [transformation[0], transformation[3]]
#         lower_left = [transformation[0],transformation[3] + (transformation[5]*rows)]
#         upper_right = [transformation[0] + (transformation[1]*cols), transformation[3]]
#         lower_right = [transformation[0] + (transformation[1]*cols), transformation[3] + (transformation[5]*rows)]
#         return [upper_left, lower_left, upper_right, lower_right]










#         target_ds = gdal.GetDriverByName('GTiff').Create(out_path, round(cols/10), round(rows*-1/10), 1,gdal.GDT_Byte) 
#         target_ds.SetGeoTransform((8.499156610827178, 0.000029990429732, 0, 47.410556698329550, 0, -0.000029990639256))
#         # python ./utils/gdal_edit.py -a_srs EPSG:4326 ../data/temp/1091-23o.tif
#         target_ds.SetProjection('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]')
#         gdal.RasterizeLayer(target_ds, [1], layer, burn_values=[255])
#         target_ds.FlushCache()
#         target_ds = None









# vector = shape
# output_path = '../data/temp/1091-23_a.tif'
# x_size = 2592 # 25927
# y_size = 1185 # 11858
# options = ['ATTRIBUTE=FID']

# vector_to_raster(vector, output_path, x_size, y_size, options)


# from PIL import Image
# import numpy
# im = Image.open('../data/temp/1091-23n.tif')
# im2 = Image.open('../data/temp/1091-23t.tif')
# imarray1 = numpy.array(im)
# imarray2 = numpy.array(im2)

# imarray1[0]
# imarray2[0]

# for line in imarray2[0]:
#     for pixel in imarray2[0]:
#         if pixel != 0:
#             print(pixel)

# for pixel in imarray2[5]:
#         if pixel != 0:
#             print(pixel)

# working_image = gdal.Open('../data/temp/1091-23n.tif')
# working_image.GetProjection()





# py Slicer ../data/in/ortho/wgs84/DOP25_LV95_1091-23_2013_1_13.tif ../data/out

# py Slicer ../data/in/osm/raster/out.tif ../data/out