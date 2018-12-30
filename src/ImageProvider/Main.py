import sys
from ImageProviderConfig import ImageProviderConfig
from ImageProvider import ImageProvider
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='get images from an azure blob storage and convert images from LV95 to WGS84 coordinate system')
    parser.add_argument('imageNumber', metavar='IMAGENUMBER', type=str, help='the image number, you can find the image numbers on https://bit.ly/2QUgMUA"')
    parser.add_argument('-i', '--inputpath', metavar='OUTPUTPATH', default="../data/in/ortho/wgs84", type=str, help='overwrite input path')
    parser.add_argument('-o', '--outputpath', metavar='OUTPUTPATH', default="../data/in/ortho/raw", type=str, help='overwrite output path')
    parser.add_argument('-aa', '--azureaccount', metavar='AZUREACCOUNT', type=str, help='set azure account, only used if azure is in use')
    parser.add_argument('-ab', '--azureblob', metavar='AZUREBLOB', default="rawdata", type=str, help='set azure blob name, only used if azure is in use')

    return parser.parse_args()

def main():
    args = parse_args()
    config = ImageProviderConfig(
        is_azure = args.azureaccount != None, 
        input_path = args.inputpath, 
        output_path = args.outputpath,
        azure_blob_name = args.azureblob,
        azure_blob_account = args.azureaccount)
    if args.azureaccount != None:
        config.set_azure_key_from_config("../config/azure.key")
    image_provider = ImageProvider(config)
    
    image_provider.get_image_as_wgs84(args.imageNumber)

if __name__ == "__main__":
    main()
