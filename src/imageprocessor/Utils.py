from osgeo import gdal

def get_corner_coordinates(image_path: str):
    ds = gdal.Open(image_path)
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    transformation = ds.GetGeoTransform()
    upper_left = [transformation[0], transformation[3]]
    lower_left = [transformation[0],transformation[3] + (transformation[5]*rows)]
    upper_right = [transformation[0] + (transformation[1]*cols), transformation[3]]
    lower_right = [transformation[0] + (transformation[1]*cols), transformation[3] + (transformation[5]*rows)]
    return [upper_left, lower_left, upper_right, lower_right]
