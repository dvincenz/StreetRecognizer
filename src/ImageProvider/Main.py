import sys
from ImageProviderConfig import ImageProviderConfig
from ImageProvider import ImageProvider
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='get images from an azure blob storage and convert images from LV95 to WGS84 coordinate system')
    parser.add_argument('imageNumber', metavar='IMAGENUMBER', type=str, help='the image number, you can find the image numbers on https://bit.ly/2QUgMUA"')
    return parser.parse_args()

def main():
    args = parse_args()
    print("init downloader, this may take some time")
    config = ImageProviderConfig()
    config.set_azure_key_from_config("../config/azure.key")
    image_provider = ImageProvider(config)
    image_provider.get_image_as_wgs84(args.imageNumber)

if __name__ == "__main__":
    main()
