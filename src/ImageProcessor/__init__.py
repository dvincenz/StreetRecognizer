import argparse
from ImageProcessor.ImageProcessor import ImageProcessor
from ImageProcessor.ImageProcessorConfig import ImageProcessorConfig


def parse_args():
    parser = argparse.ArgumentParser(description='The ImageProcessor class can modify geo refrenced images based or with geojson data')
    parser.add_argument('target', metavar='TARGETPATH', type=str, help='output path to write coputed data')
    parser.add_argument('source', metavar='SOURCEPATH', type=str, help='path to source file')
    parser.add_argument('-m', '--method', metavar='METHOD', type=str, help='''
        Method used to tranform data: 
            `rasterizeGeojson` convert geojson to geotiff file, using a geoTiff (ortho photo) as coordinate and resolution provider, parameter -t is needed
            `cutgeoTiffs` cut one geoTiff based on the resolution of an other geoTiff, parameter -t is needed
            `excreteGeoTiff` excrete GeoTiff based on geoJson vector data (not implemented yet)
            `getPolygonShares` get size of polygon in defined are (not implemented yet)
    ''')
    parser.add_argument('-t', '--template', metavar='TEMPLATE', type=str, help='template path of geoTiff file to cut other geoTiff (source) file')
    return vars(parser.parse_args())
    

def run():
    configs = parse_args()
    Provider(**configs)

def Provider(**kwargs):
    if kwargs.get("config"):
        config = kwargs.get("config")
        return ImageProcessorConfig(config)
    config = ImageProcessorConfig(output_path = kwargs.get("target"))
    provider = ImageProcessor(config)
    method = kwargs.get("method").lower()
    if method == "rasterizegeojson":
        if not kwargs.get("template"):
            raise ValueError("the parameter --template (-t) is needed to set resolution of transofrmation")
        width, height = provider.get_pixel_width_heigh(kwargs.get("template"))
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
    if method == "excretegeotiff": 
        print("not implemented yet, sorry")
    if method == "getpolygonshares": 
        print("not implemented yet, sorry")
    raise ValueError('Image path or coordinates need to be set as argument. Use -h for more information')

if __name__ == "__main__":
    Provider()
