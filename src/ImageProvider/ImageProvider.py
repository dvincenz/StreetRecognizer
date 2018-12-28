from azure.storage.blob import BlockBlobService, PublicAccess
import os
import subprocess
from ImageProviderConfig import ImageProviderConfig

class ImageProvider:
    EPSG_LV95 = "EPSG:2056"
    EPSG_WGS84 = "EPSG:4326"
    def __init__ (self, config: ImageProviderConfig):
        self.config = config
        self.block_blob_service = BlockBlobService(account_name=config.azure_blob_account, account_key=config.azure_blob_key) 
        self.allImages = self.block_blob_service.list_blobs(config.azure_blob_name)

    def get_image(self, image_number: str):
        tif_image_names = []
        for image in self.allImages:
            if image.name.find(image_number) >= 0:
                if os.path.exists(self.config.image_url + "/raw/" + image.name):
                    print("skip download file " + image.name + " because file already exists")
                else:
                    self._download(image.name)
                if image.name.find("tif") >= 0:
                    tif_image_names.append(image.name)
        if(tif_image_names):
            print("no images with number " + image_number + " were found")
        return tif_image_names

    def get_image_as_wgs84(self, image_number):
        _image_names = self.get_image(image_number)
        for _image_name in _image_names:
            self._set_to_lv95(_image_name)
            self._convert_to_wgs84(_image_name)

    def _convert_to_wgs84 (self, image_name):
        path = self.config.image_url + "/raw/" + image_name
        path_out = self.config.image_url + "/wgs84/" + image_name
        if os.path.exists(path_out):
            print("file " + path_out + "already exists, skip tranformation")
            return
        print("convertig image " + image_name + " to WGS84, that may take some time, enjoy your personal heater aka pc")
        bash_command = "gdalwarp " + path + " " + path_out + " -s_srs " + self.EPSG_LV95 + " -t_srs " + self.EPSG_WGS84
        if not os.path.exists(self.config.image_url + "/wgs84/"):
                os.makedirs(self.config.image_url + "/wgs84/")
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate() 
    
    def _set_to_lv95 (self, image_name):
        image_url = self.config.image_url + "/raw/" + image_name
        bash_command = "./utils/gdal_edit.py -a_srs "+ self.EPSG_LV95 + " " + image_url
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate() 

    def _download(self, image_name):
        path = self.config.image_url + "/raw"
        print("downloading " + image_name + " to " + path + "/" + image_name)
        if not os.path.exists(path):
                os.makedirs(path)
        self.block_blob_service.get_blob_to_path(self.config.azure_blob_name, image_name, path + "/" + image_name)


