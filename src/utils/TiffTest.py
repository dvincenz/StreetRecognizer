from PIL import Image
from PIL.TiffTags import TAGS
import exifread

Image.MAX_IMAGE_PIXELS = 328125000

IMAGE = './utils/1032-432.tif'

# Open image file for reading (binary mode)
f = open(IMAGE, 'rb')

# Return Exif tags
tags = exifread.process_file(f)

# Print the tag/ value pairs
for tag in tags.keys():
    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
        print("Key: " + str(tag) + ", value " + str(tags[tag]))