from string import hexdigits
import struct
from lavina_server.settings import DATA_ROOT

CORE_LAT = 67
CORE_LONG = 33
FILENAME = DATA_ROOT + "N67E033.hgt"
VOID_DATA = -32768

def get_sample(f, i, j):
    # TODO: неоптимизированное чтение файла, все время перемещаемся с начала, а не
    # c текущей позиции
    f.seek(((i - 1) * 1201 + (j - 1)) * 2)  # go to the right spot,
    buf = f.read(2)  # read two bytes and convert them:
    val = struct.unpack('>h', buf)  # ">h" is a signed two byte integer
    if not val == -32768:  # the not-a-valid-sample value
        return val
    else:
        return None

def coord_to_hgt_tile_indexes(lat, lng):
    arclat = (lat - CORE_LAT) * 3600
    arclng = (lng - CORE_LONG) * 3600
    return (1201 - int(round(arclat / 3, 0)),
            (int(round(arclng / 3, 0))))

def hgt_tile_indexes_to_coords(i, j):
    return ((1201 - i) * 3 / 3600 + CORE_LAT,
            j*3 / 3600 + CORE_LONG)

def get_elevation_around(lat, lng):
    indexes = coord_to_hgt_tile_indexes(lat, lng)
    j = indexes[1] - 1
    data = []
    with open(FILENAME, "rb") as f:
        while j < (indexes[1] + 2):
            i = indexes[0] - 1
            data.append([])
            while i < (indexes[0] + 2):
                elevation = get_sample(f, i, j)[0]
                data[-1].append({'elevation': elevation, 
                                'coords': hgt_tile_indexes_to_coords(i, j)})
                i += 1
            j += 1

    coord_error = (data[1][1]["coords"][0] - lat,
                   data[1][1]["coords"][1] - lng)
                   
    return {'data': data, 'error': coord_error}


def get_relief(place):
    bounds = place.geometry.extent
    topLeft = coord_to_hgt_tile_indexes(bounds[0], bounds[1])
    bottomRight = coord_to_hgt_tile_indexes(bounds[2], bounds[3])
    result = []
    heighest_point = None 
    with open(FILENAME, "rb") as f:
        f.seek(((topLeft[0] - 1) * 1201 + (topLeft[1] - 1)) * 2)
        for i in range(bottomRight[0], topLeft[0]+1):
            result.append([])
            for j in range(topLeft[1], bottomRight[1] + 1):
                val = struct.unpack('>h', f.read(2))
                result[-1].append({'elevation': val[0] if val[0] != VOID_DATA else None,
                                   'coords': hgt_tile_indexes_to_coords(i, j)})
                if heighest_point is None or \
                   result[-1][-1]['elevation'] < heighest_point['elevation']:
                     heighest_point = result[-1][-1]
            f.seek((1201 + (1200 - bottomRight[1]))*2, 1)
    return (heighest_point, result)

def test(place):
    bounds = place.geometry.extent
    relief = get_relief(place)
    print(bounds[0], bounds[1], sep=' ')
    print(relief[1][0][0]['coords'])
    print(bounds[2], bounds[3], sep=' ')
    print(relief[1][-1][-1]['coords'])
    print(relief[1][-1][-1]['elevation'])
    elevation = get_elevation_around(relief[1][-1][-1]['coords'][0], 
                                     relief[1][-1][-1]['coords'][1])
    print(elevation["data"][1][1]['elevation'])
    print(elevation["error"])

    

def constrain(val, min_val, max_val):    
    return min(max_val, max(min_val, val))

def get_around(x, y, relief_map):
    rows = relief_map[constrain(x - 1, 0, len(relief_map)) :
                      constrain(x + 1, 0, len(relief_map))]
    height = len(relief_map[0])
    rows = [row[constrain(y - 1, 0, height) : 
                constrain(y + 1, 0, height)]  for row in rows]
    return rows
            
            
if __name__ == "__main__":
    lat, lng = 67.61916666666667, 33.75
    print(get_elevation_around(lat, lng))
    # lat, lng = 67.618511, 33.750900
   