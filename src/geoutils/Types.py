from shapely.geometry import LineString
import random

class GeoPoint:
    def __init__(self, east: float, north: float):
        self.east = east
        self.north = north

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash((self.east, self.north))

    def __str__(self):
        return '({0}E, {1}N)'.format(self.east, self.north)


class ParametricGeoLine:
    def __init__(self, base: GeoPoint, vector: GeoPoint):
        self.base = base
        self.vector = vector


class GeoLineSegment:
    def __init__(self, a: GeoPoint, b: GeoPoint):
        self.a = a
        self.b = b

    def extend_to_parametric_geo_line(self) -> ParametricGeoLine:
        return ParametricGeoLine(base=self.a, vector=GeoPoint(east=self.b.east - self.a.east, north=self.b.north - self.a.north))

    def does_line_segment_intersect(self, other: 'GeoLineSegment') -> bool:
        # https://stackoverflow.com/questions/4977491/determining-if-two-line-segments-intersect/4977569#4977569
        self_param = self.extend_to_parametric_geo_line()
        other_param = other.extend_to_parametric_geo_line()
        determinant = other_param.vector.east * self_param.vector.north - self_param.vector.east * other_param.vector.north
        if determinant == 0:
            # The line segments are parallel, and thus do not intersect
            return False
        # Find the intersection parameters of both ParametricGeoLines
        s = ((self_param.base.east - other_param.base.east) * self_param.vector.north - (self_param.base.north - other_param.base.north) * self_param.vector.east) / determinant
        t = -(-(self_param.base.east - other_param.base.east) * other_param.vector.north + (self_param.base.north - other_param.base.north) * other_param.vector.east) / determinant
        # Check, if the intersection parameters are in the valid range for the line segment (i.e. not on the extended part of the segment)
        return 0 <= s <= 1 and 0 <= t <= 1


class GeoRect:
    def __init__(self, a: GeoPoint, b: GeoPoint):
        self.a = a
        self.b = b

    def is_point_inside(self, point: GeoPoint) -> bool:
        xmin = min(self.a.east, self.b.east)
        xmax = max(self.a.east, self.b.east)
        ymin = min(self.a.north, self.b.north)
        ymax = max(self.a.north, self.b.north)
        return point.east > xmin and point.east < xmax and point.north > ymin and point.north < ymax

    def does_line_segment_intersect(self, line_segment: GeoLineSegment) -> bool:
        if self.is_point_inside(line_segment.a) or self.is_point_inside(line_segment.b):
            return True

        for bounding_line_segment in self.get_bounding_line_segments():
            if line_segment.does_line_segment_intersect(bounding_line_segment):
                return True

    def get_bounding_line_segments(self) -> [GeoLineSegment]:
        return [
            GeoLineSegment(self.a, GeoPoint(east=self.a.east, north=self.b.north)),
            GeoLineSegment(self.a, GeoPoint(east=self.b.east, north=self.a.north)),
            GeoLineSegment(GeoPoint(east=self.a.east, north=self.b.north), self.b),
            GeoLineSegment(GeoPoint(east=self.b.east, north=self.a.north), self.b)
        ]


class GeoLines:
    def __init__(self, line_strings):
        self.line_strings = line_strings
        self.lines = []
        self.total_length = 0
        for way in self.line_strings:
            line = LineString(way["geometry"]["coordinates"])
            self.total_length += line.length
            self.lines.append(line)
        self.lines.sort(key=lambda x: x.length, reverse=True)

    def random_points(self, number):
        random_points = []
        random_numbers = []
        for _ in range(0, number):
            random_numbers.append(random.uniform(0,self.total_length))
            random_numbers.sort()

        temp_length = 0
        for line in self.lines:
            temp_length += line.length
            for random_number in random_numbers:
                if temp_length > random_number:
                    point = line.interpolate(random.uniform(0, line.length))
                    random_points.append(GeoPoint(point.x, point.y))
                    if len(self.lines) >= len(random_numbers):
                        random_numbers.remove(random_number)
                        break
        return random_points
