
#%% [markdown]
# ## global configuration
# get, tranform, slice and prepair for model learning
#%%
import os
import subprocess

from utils.logger import get_logger

logger = get_logger("model1")

image_number = "DOP25_LV"

#%% [markdown]
# ## get images and tranform to WGS84
#%%
import imageprovider
from imageprovider import ImageProviderConfig

config = ImageProviderConfig(azure_blob_account="swisstopo", output_path="../data/in/ortho/wgs84")
images = imageprovider.Provider(config=config)
image_names = images.get_images_names(image_number)
logger.info("total transofrm images: " + str(len(image_names)))
all_images = images.get_image_as_wgs84(image_number)

#%% [markdown]
# ## get the needed osm data

#%%
import osmdataprovider
from osmdataprovider import OsmDataProviderConfig

config = OsmDataProviderConfig(output_path = "../data/in/osm/vector", buffer={})
osm_data = osmdataprovider.Provider(config=config)
for image_name in all_images:
    try:
        osm_data.export_ways_by_image('../data/in/ortho/wgs84/' + image_name)
    except Exception as e:
        logger.error('get osm data - ' + e)
#%% [markdown]
# ## Transform osm data to raster

#%%
import imageprocessor
from imageprocessor import ImageProcessorConfig

config = ImageProcessorConfig(output_path="../data/in/osm/raster")
processor = imageprocessor.Provider(config=config)

for image_name in all_images:
    try:
        json_path = '../data/in/osm/vector/{0}_polygon.json'.format(os.path.splitext(image_name)[0])
        base_image = "../data/in/ortho/wgs84/"+image_name
        processor.burn_attribute = processor.add_print_attribute(json_path)
        width, height = processor.get_pixel_width_heigh(base_image)
        json_raster = processor.get_raster_from_geojson(json_path, width, height)
        logger.info("tranformed image " + json_raster)
        json_raster_cut = processor.cut_geo_image(base_image, json_raster)
        logger.info("cut image " +json_raster_cut)
    except Exception as e:
        logger.error('osm2raster - ' + e)

#%% [markdown]
# ## Slice images
# todo call slicer without subprocess

#%%
for image in all_images:
    try:
        bash_command = "python slicer ../data/in/ortho/wgs84/{0} {1}".format(image, '../data/out')
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate() 
        
        bash_command = "python slicer ../data/in/osm/raster/{0}_cut_raster.tif {1}".format(os.path.splitext(image_name)[0], '../data/out')
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate() 
    except Exception as e:
        logger.error('slicing ' + e)
