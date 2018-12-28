from azure.storage.blob import BlockBlobService, PublicAccess
import os
import subprocess
from ImageProviderConfig import ImageProviderConfig


class ImageProvider:
    EPSG_LV95 = "EPSG:2056"
    EPSG_WGS84 = "EPSG:4326"
    def __init__ (self, config: ImageProviderConfig):
        self.config = config
        self.block_blob_service = BlockBlobService(account_name=config.azureBlobAccount, account_key=config.azureBlobKey) 
        self.allImages = self.block_blob_service.list_blobs(config.azureBlobName)

    def GetImage(self, imageNumber: str):
        tifImageNames = []
        for image in self.allImages:
            if image.name.find(imageNumber) >= 0:
                if os.path.exists(self.config.imageUrl + "/raw/" + image.name):
                    print("skip download file " + image.name + " because file already exists")
                else:
                    self.__download__(image.name)
                if image.name.find("tif") >= 0:
                    tifImageNames.append(image.name)
        if(len(tifImageNames) == 0):
            print("no images with number " + imageNumber + " were found")
        return tifImageNames

    def GetImageAsWgs84(self, imageNumber):
        imageNames = self.GetImage(imageNumber)
        for imageName in imageNames:
            self.__set2LV95__(imageName)
            self.__convert2Wgs84__(imageName)

    def __convert2Wgs84__ (self, imageName):
        path = self.config.imageUrl + "/raw/" + imageName
        pathOut = self.config.imageUrl + "/wgs84/" + imageName
        if os.path.exists(pathOut):
            print("file " + pathOut + "already exists, skip tranformation")
            return
        print("convertig image " + imageName + " to WGS84, that may take some time, enjoy your personal heater aka pc")
        bashCommand = "gdalwarp " + path + " " + pathOut + " -s_srs " + self.EPSG_LV95 + " -t_srs " + self.EPSG_WGS84
        if not os.path.exists(self.config.imageUrl + "/wgs84/"):
                os.makedirs(self.config.imageUrl + "/wgs84/")
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate() 
    
    def __set2LV95__ (self, imageName):
        imageUrl = self.config.imageUrl + "/raw/" + imageName
        bashCommand = "/usr/src/app/extensions/gdal_edit.py -a_srs "+ self.EPSG_LV95 + " " + imageUrl
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate() 

    def __download__(self, imageName):
        path = self.config.imageUrl + "/raw"
        print("downloading " + imageName + " to " + path + "/" + imageName)
        if not os.path.exists(path):
                os.makedirs(path)
        self.block_blob_service.get_blob_to_path(self.config.azureBlobName, imageName, path + "/" + imageName )


