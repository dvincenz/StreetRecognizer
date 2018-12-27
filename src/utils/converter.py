import json
from osgeo import gdal,ogr,osr
import requests
import subprocess



# with open('osm2geojson/file2.json') as f:
#     data = json.load(f)
#     for val in data["features"][0]["geometry"]["coordinates"][0]:
#         val = converter.WGStoCHx(val[1],val[0])
#         y = converter.WGStoCHy(val[1],val[0]) 
#         print(x)
#         print(y)

def GetCornerCoordinates(gt, cols, rows):
    upperLeft = [gt[0], gt[3]]
    lowerLeft = [gt[0],gt[3] + (gt[5]*rows)]
    upperRight = [gt[0] + (gt[1]*cols), gt[3]]
    lowerRight = [gt[0] + (gt[1]*cols), gt[3] + (gt[5]*rows)]
    return [upperLeft, lowerLeft, upperRight, lowerRight]

def GetTransformation(cornerCoordinates, cols, rows):
    sizex = (cornerCoordinates[3][1] - cornerCoordinates[0][1]) / cols
    sizey = (cornerCoordinates[3][0] - cornerCoordinates[0][0]) / rows
    # return (cornerCoordinates[0][0], sizex, 0.0, cornerCoordinates[0][1], 0.0, sizey)
    return (cornerCoordinates[0][1], sizex, 0.0, cornerCoordinates[0][0], 0.0, sizey)

def GetCoordinatesOfImage(image):
    ds=gdal.Open(image)
    gt=ds.GetGeoTransform()
    return GetCornerCoordinates(gt, ds.RasterXSize, ds.RasterYSize)

def TranformImageCoordinates(cornerCordinates):
    result = []
    for c in cornerCordinates:
        result.append(tranform2wgs84(c))
    return result

def tranform2wgs84(imageCordinates):
    transofrmedCorrdinates = requests.get('http://geodesy.geo.admin.ch/reframe/lv95towgs84?easting=' + str(imageCordinates[0]) + '&northing='+ str(imageCordinates[1]) +'&altitude=0').json()
    x = transofrmedCorrdinates["coordinates"][1]
    y = transofrmedCorrdinates["coordinates"][0]
    return [x, y]


def TranformImage2wgs84(image):
    tranformedCoordinates = TranformImageCoordinates(GetCoordinatesOfImage(image)) ##ok
    ds=gdal.Open(image, gdal.GF_Write) 
    tranformed = GetTransformation(tranformedCoordinates, ds.RasterXSize, ds.RasterYSize) 
    ds.SetGeoTransform(tranformed)
    print(tranformed)
    bashCommand = "/usr/src/app/extensions/gdal_edit.py -a_srs EPSG:4326 " + image
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate() 
    return

ds=gdal.Open(image, gdal.GF_Write)
transformer = GetTransformation(tranformedCoordinates, ds.RasterXSize, ds.RasterYSize)
GetCornerCoordinates(transformer, ds.RasterXSize, ds.RasterYSize)



image = './in/tmp9/DOP25_LV95_1091-14_2013_1_13.tif'





TranformImage2wgs84(image)


imageCordinates = TranformImageCoordinates(GetCoordinatesOfImage(image))



image = './in/tmp7/DOP25_LV95_1091-14_2013_1_13.tif'
    bashCommand = "/usr/src/app/extensions/gdal_edit.py -a_srs EPSG:2056 " + image
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate() 


8.4964559 / 47.3655897

Upper Left  (   8.4571096,  47.4053306) (  8d27'25.59"E, 47d24'19.19"N)
Lower Left  (   8.4571096,  47.3655897) (  8d27'25.59"E, 47d21'56.12"N)
Upper Right (   8.4964559,  47.4053306) (  8d29'47.24"E, 47d24'19.19"N)
Lower Right (   8.4964559,  47.3655897) (  8d29'47.24"E, 47d21'56.12"N)

Upper Left  ( 2676875.000, 1251000.000) (  8d27'29.62"E, 47d24'24.11"N)
Lower Left  ( 2676875.000, 1248000.000) (  8d27'27.76"E, 47d22'46.97"N)
Upper Right ( 2681250.000, 1251000.000) (  8d30'58.29"E, 47d24'22.22"N)
Lower Right ( 2681250.000, 1248000.000) (  8d30'56.32"E, 47d22'45.08"N)

Upper_Left = tranform2wgs84([2672500.0, 1251000.0])
Lower_Left = tranform2wgs84([2672500.0, 1248000.0])
Upper_Right = tranform2wgs84([2676875.0, 1248000.0]) 
Lower_Right = tranform2wgs84([2676875.0, 1251000.0])



# file:///C:/Users/dvi.PX/Downloads/Report16-03.pdf

def tranform2lv95(imageCordinates):
    transofrmedCorrdinates = requests.get('http://geodesy.geo.admin.ch/reframe/wgs84tolv95?easting=' + str(imageCordinates[0]) + '&northing='+ str(imageCordinates[1]) +'&altitude=0').json()
    x = transofrmedCorrdinates["coordinates"][0]
    y = transofrmedCorrdinates["coordinates"][1]
    return [x, y]


def tranform2wgs84(imageCordinates):
    transofrmedCorrdinates = requests.get('http://geodesy.geo.admin.ch/reframe/lv95towgs84?easting=' + str(imageCordinates[0]) + '&northing='+ str(imageCordinates[1]) +'&altitude=0').json()
    x = transofrmedCorrdinates["coordinates"][0]
    y = transofrmedCorrdinates["coordinates"][1]
    return [x, y]

transofrmedCorrdinates = requests.get('http://geodesy.geo.admin.ch/reframe/lv95towgs84?easting=' + str(imageCordinates[0]) + '&northing='+ str(imageCordinates[1]) +'&altitude=0').json()

x = transofrmedCorrdinates["coordinates"][0]
y = transofrmedCorrdinates["coordinates"][1]

# (2676875.0, 0.25, 0.0, 1251000.0, 0.0, -0.25)

ds=gdal.Open(image)
tranform = ([x, 0.0025, 0.0, y, 0.0, -0.0025])
ds.SetGeoTranform(tranform)
geotransform = ([ your_top_left_x, 30, 0, your_top_left_y, 0, -30 ])



import json
def convertGeoJson2CH95(filename):
    with open(filename, 'r+') as f:
        data = json.load(f)
        coordinates = data['features'][0]["geometry"]["coordinates"]
        i = 0
        for valueGroup in coordinates:
            m = 0
            for value in valueGroup:
                value = tranform2lv95(value)
                valueGroup[m] = value
                m += 1
                print(value)
            coordinates[i] = valueGroup
            i += 1
        data['features'][0]["geometry"]["coordinates"] = coordinates
        f.seek(0) 
        json.dump(data, f, indent=8)
        return coordinates

        
Upper_Left = tranform2wgs84([2676875.000, 1251000.000])
Lower_Left = tranform2wgs84([2676875.000, 1248000.000])
Upper_Right = tranform2wgs84([2681250.000, 1251000.000]) 
Lower_Right = tranform2wgs84([2681250.000, 1248000.000])


# 2672500.0 1251000.0
# 2672500.0 1248000.0
# 2676875.0 1248000.0
# 2676875.0 1251000.0

ullon =  tranform2wgs84([2672500.000, 1251000.000])
ullat = tranform2wgs84([2672500.000, 1248000.000])
lrlon = tranform2wgs84([2676875.000, 1251000.000])
lrlat = tranform2wgs84([2676875.000, 1248000.000])


bashCommand = "gdal_translate -of GTiff -a_ullr " + [2672500.000, 1251000.000] + " " + [2672500.000, 1248000.000] + " " + [2676875.000, 1251000.000] + " " + [2676875.000, 1248000.000] + " -a_srs EPSG:2056 " + image + " " + image +".out"

import subprocess
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate() 


import gdal_edit

gdal_edit 

convertGeoJson2CH95('./utils/osm2geojson/test.json')

# 1. define missing coordinate system
# /usr/src/app/extensions/gdal_edit.py -a_srs EPSG:2056 ./in/Ortho/DOP25_LV95_1091-13_2013_1_13.tif
# 2. transform coordinate system
