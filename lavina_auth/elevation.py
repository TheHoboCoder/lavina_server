from lavina_server.settings import DATA_ROOT
from django.contrib.gis.gdal import GDALRaster
from math import sqrt, sin as sinus, degrees

FILE = DATA_ROOT + "height_map.tif"

# assuming file crs is 4326 (WGS84), otherwise will not work
def coord_from_geo(lat, lng, rst):
    top_left = (rst.extent[3], rst.extent[0])
    array_dim = (len(rst.bands[0].data()[0]), len(rst.bands[0].data()))
    sec_per_width = (rst.extent[2] - rst.extent[0])*3600 / array_dim[0]
    sec_per_height = (rst.extent[3] - rst.extent[1])*3600 / array_dim[1]
    sec_rel_coords = (top_left[0] - lat) * 3600, (lng - top_left[1]) * 3600
    return (int(round(sec_rel_coords[0] / sec_per_height, 0)), 
          int(round(sec_rel_coords[1] / sec_per_width, 0)))

def geo_from_coords(x, y, rst):
    gt = rst.geotransform
    x_geo = gt[0] + y*gt[1] + x*gt[2]
    y_geo = gt[3] + y*gt[4] + x*gt[5]
    return y_geo, x_geo

def get_allowed_region():
    a_r = GDALRaster(FILE, write=False).extent
    return ((a_r[0], a_r[1]),(a_r[2], a_r[3]))

def get_relief(bounds):
    rst = GDALRaster(FILE, write=False)
    topLeft = coord_from_geo(bounds[0], bounds[1], rst)
    bottomRight = coord_from_geo(bounds[2], bounds[3], rst)
    result = []
    heighest_point = None 
    for i in range(bottomRight[0], topLeft[0]+1):
        result.append([])
        for j in range(topLeft[1], bottomRight[1] + 1):
            val = rst.bands[0].data()[i][j]
            result[-1].append({'elevation': val,
                                'coords': geo_from_coords(i, j, rst)})
            if heighest_point is None or \
                result[-1][-1]['elevation'] > heighest_point['elevation']:
                    heighest_point = result[-1][-1]
    return (heighest_point, result)

def constrain(val, min_val, max_val):    
    return min(max_val, max(min_val, val))

def get_around(x, y, relief_map):
    bounds_x = constrain(x - 1, 0, len(relief_map)), constrain(x + 1, 0, len(relief_map)) + 1
    height = len(relief_map[0])
    bounds_y = constrain(y - 1, 0, height), constrain(y + 1, 0, height) + 1
    for i in range(bounds_x[0], bounds_x[1]):
        for j in range(bounds_y[0], bounds_y[1]):
            if i == x and j == y:
                continue
            yield (i, j), relief_map[i][j]

def get_distance(latlng1, latlng2):
    lat_meters = abs(latlng1[0] - latlng2[0]) * 111.139
    lng_meters = abs(latlng1[1] - latlng2[1]) * 111.139
    return sqrt(lat_meters**2 + lng_meters**2)

def get_sin_cos_angle(distance, elevation):
    sin = elevation / distance
    cos = sqrt(1 - sin**2)
    angle = degrees(sinus(sin))
    return sin, cos, angle

def trace_path(start_point, mass, fraction):
    rst = GDALRaster(FILE, write=False)
    data = rst.bands[0].data()
    current_point = start_point
    coords = coord_from_geo(current_point[0], current_point[1], rst)
    current_point = (coords, data[coords[0]][coords[1]])
    count_same = 0
    next_point = None
    velocity = 0
    traced_path = []
    info = []
    while len(traced_path) < 1000:

        for point in get_around(current_point[0][0], current_point[0][1], data):
            if next_point is None or point[1] < next_point[1]:
                next_point = point

        delta_elevation = abs(next_point[1] - current_point[1])
        traced_path.append(geo_from_coords(current_point[0][0], current_point[0][1], rst))
        if delta_elevation < 2:
            count_same += 1
            if count_same > 5:
                return traced_path, info, "stuck"
        else:
            count_same = 0

        # print(current_point)
        # print(next_point)
        distance = get_distance(current_point[0], next_point[0])
        # print(distance)
        sin, cos, angle = get_sin_cos_angle(distance, delta_elevation)
        # print(sin, cos)
        a = 9.8 * (sin - fraction*cos)
        if a < 0:
            return traced_path, info, "fraction is too high and angle is low"
        # print(a)
        d = velocity**2 + 4 * distance * (a / 2)
        t = (sqrt(d) - velocity) / 2
        
        if current_point[1] < next_point[1]:
            a = -a 
        velocity = a*t + velocity

        if velocity <= 0:
            return traced_path, info

        info.append({'time': t, 'velocity_at_end': velocity, 'delta_elevation': delta_elevation, 'angle': angle})
        current_point = next_point

    return traced_path, info, "exceed"

    
def test():
    rst = GDALRaster(FILE, write=False)
    test_data = ((67.60166666666667, 33.69583333333333, 510),
                 (67.58916666666667, 33.68666666666667, 514),
                 (67.66333333333333, 33.6925, 721),
                 (67.59666666666666, 33.69083333333333, 498))
    data = rst.bands[0].data()
    for row in test_data:
        coords = coord_from_geo(row[0], row[1], rst)
        print(coords)
        print(geo_from_coords(coords[0], coords[1], rst))
        print((row[0], row[1], row[2], data[coords[0]][coords[1]]))

def test_2():
    rst = GDALRaster(FILE, write=False)
    coords = coord_from_geo(67.59027777777779, 33.68666666664018, rst)
    return get_around(coords[0], coords[1], rst.bands[0].data())