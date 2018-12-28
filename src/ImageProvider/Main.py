import sys
from ImageProviderConfig import ImageProviderConfig
from ImageProvider import ImageProvider

def main():
    if len(sys.argv) <= 1:
        print("please add image nr as argument, you can find the image numbers on https://map.geo.admin.ch/?lang=en&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.swisstopo.hiks-siegfried-ta25.metadata,ch.swisstopo.images-swissimage.metadata,ch.swisstopo.images-swissimage-dop10.metadata&layers_visibility=false,false,false,false,false,true,false&layers_timestamp=18641231,,,,,,&E=2669555.54&N=1218777.45&zoom=2&catalogNodes=457,485")
        return

    print("init downloader, this may take some time")
    config = ImageProviderConfig()
    config.set_azure_key_from_config("../config/azure.key")
    image_provider = ImageProvider(config)
    image_provider.get_image_as_wgs84(sys.argv[1])

if __name__ == "__main__":
    main()
