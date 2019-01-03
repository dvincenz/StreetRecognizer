import argparse
import sys

from ImageProvider.ImageProvider import ImageProvider
from ImageProvider.ImageProviderConfig import ImageProviderConfig

def parse_args():
    parser = argparse.ArgumentParser(description='get images from an azure blob storage and convert images from LV95 to WGS84 coordinate system')
    parser.add_argument('imageNumber', metavar='IMAGENUMBER', type=str, help='the image number, you can find the image numbers on https://bit.ly/2QUgMUA"')
    parser.add_argument('-i', '--inputpath', metavar='INPUTPATH',  type=str, help='overwrite input path')
    parser.add_argument('-o', '--outputpath', metavar='OUTPUTPATH', type=str, help='overwrite output path')
    parser.add_argument('-aa', '--azureaccount', metavar='AZUREACCOUNT', type=str, help='set azure account, if not only discover local saved images')
    parser.add_argument('-ab', '--azureblob', metavar='AZUREBLOB', type=str, help='set azure blob name, only used if azure is in use')

    return vars(parser.parse_args())

def run():
    configs = parse_args()
    Provider(**configs)

def Provider(**kwargs):
    if kwargs.get("config"):
        config = kwargs.get("config")
        return ImageProvider(config)
    config = ImageProviderConfig( 
        input_path = kwargs.get("inputpath"), 
        output_path =  kwargs.get("outputpath"),
        azure_blob_name =  kwargs.get("azureblob"),
        azure_blob_account = kwargs.get("azureaccount"))
    image_provider = ImageProvider(config)
    image_provider.get_image_as_wgs84(kwargs.get("imageNumber"))

if __name__ == "__main__":
    Provider()
