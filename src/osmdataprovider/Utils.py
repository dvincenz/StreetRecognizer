import math

from geoutils.Types import GeoLineSegment
from geoutils.Types import GeoRect
from geoutils.Types import GeoPoint

def get_features_intersecting_rect(osm_data: dict, rect: GeoRect):
    if osm_data['type'] != 'FeatureCollection':
        raise ValueError('Expected osm_data to be a geojson FeatureCollection')

    result = []
    for feature in osm_data['features']:
        for i in range(0, len(feature['geometry']['coordinates']) - 1):
            curr_p = feature['geometry']['coordinates'][i]
            next_p = feature['geometry']['coordinates'][i+1]
            curr_geo = GeoPoint(east=curr_p[0], north=curr_p[1])
            next_geo = GeoPoint(east=next_p[0], north=next_p[1])
            line_segment = GeoLineSegment(a=curr_geo, b=next_geo)
            if rect.does_line_segment_intersect(line_segment=line_segment):
                result.append(feature)
                break

    return result
