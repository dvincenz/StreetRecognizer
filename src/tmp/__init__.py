import argparse
from imageprocessor.ImageProcessor import ImageProcessor
from imageprocessor.ImageProcessorConfig import ImageProcessorConfig
from geodataprovider.GeoDataProvider import GeoDataProvider


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''
The ImageProcessor class can modify geo refrenced images based or with geojson data 
Method used to tranform data: 
    `rasterizeGeojson` convert geojson to geotiff file, using a geoTiff (ortho photo) 
        as coordinate and resolution provider, parameter -t is needed
    `cutgeoTiffs` cut one geoTiff based on the resolution of an other geoTiff, parameter -t is needed''')

    parser.add_argument('source', metavar='SOURCEPATH', type=str, help='path to source file')
    parser.add_argument('target', metavar='TARGETPATH', type=str, help='output path to write coputed data')
    parser.add_argument('-m', '--method', metavar='METHOD', type=str, help='select method (see main description for more information)')
    parser.add_argument('-t', '--template', metavar='TEMPLATE', type=str, help='template path of geoTiff file to cut other geoTiff (source) file')
    return vars(parser.parse_args())
    

def run():
    configs = parse_args()
    Provider(**configs)

def Provider(**kwargs):
    if kwargs.get("config"):
        config = kwargs.get("config")
        return ImageProcessor(config)
    config = ImageProcessorConfig(output_path = kwargs.get("target"))
    provider = ImageProcessor(config)
    method = kwargs.get("method").lower()
    if method == "rasterizegeojson":
        if not kwargs.get("template"):
            raise ValueError("the parameter --template (-t) is needed to set resolution of transofrmation")
        geo_data = GeoDataProvider((kwargs.get("template"))
        width =  geo_data.get_pixel_width()
        height = geo_data.get_pixel_hight()
        image_name = provider.get_raster_from_geojson(kwargs.get("source"), width,  height)
        print("image created " + image_name)
        print("cutting image...")
        image_name = provider.cut_geo_image(kwargs.get("template"), image_name)
        print("done, output: " + image_name)
        return
    if method == "cutgeotiffs":
        image_name = provider.cut_geo_image(kwargs.get("template"), kwargs.get("source"))
        print("done, output: " + image_name)
        return
    raise ValueError('Image path or coordinates need to be set as argument. Use -h for more information')

if __name__ == "__main__":
    Provider()
