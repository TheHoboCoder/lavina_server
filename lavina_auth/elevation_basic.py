import struct
from lavina_server.settings import DATA_ROOT

CORE_LAT = 67
CORE_LONG = 33

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
    magical_correction = 0.0008333333333325754
    return ((1200 - i) * 3 / 3600 + CORE_LAT + magical_correction,
            j*3 / 3600 + CORE_LONG)

def get_elevation_around(lat, lng):
    indexes = coord_to_hgt_tile_indexes(lat, lng)
    filename = DATA_ROOT + "N67E033.hgt"
    j = indexes[1] - 1
    data = []
    with open(filename, "rb") as f:
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


if __name__ == "__main__":
    lat, lng = 67.61916666666667, 33.75
    # lat, lng = 67.618511, 33.750900
   