import sys
from ImageProviderConfig import ImageProviderConfig
from ImageProvider import ImageProvider

def main():
    if len(sys.argv) <= 1:
        print("please add image nr as argument, you can find the image numbers on https://map.geo.admin.ch/?lang=en&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.swisstopo.hiks-siegfried-ta25.metadata,ch.swisstopo.images-swissimage.metadata,ch.swisstopo.images-swissimage-dop10.metadata&layers_visibility=false,false,false,false,false,true,false&layers_timestamp=18641231,,,,,,&E=2669555.54&N=1218777.45&zoom=2&catalogNodes=457,485")
        return

    print("init downloader, this may take some time")
    config = ImageProviderConfig()
    config.SetAzureKeyFromConfig("./config/azure.key")
    imageProvider = ImageProvider(config)
    imageProvider.GetImageAsWgs84(sys.argv[1])

if __name__ == "__main__":
    main()
