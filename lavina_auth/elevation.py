from lavina_server.settings import DATA_ROOT
from django.contrib.gis.gdal import GDALRaster
from math import sqrt, sin as sinus, degrees

# модуль для работы с картой высот, хранящейся в формате GeoTiff
# для чтения используется класс GDALRaster
# документация: https://docs.djangoproject.com/en/4.1/ref/contrib/gis/gdal/#gdalraster
# data/height_map.tif
FILE = DATA_ROOT + "height_map.tif"

# угловые секунды в одном градусе
SEC_PER_DEGREE = 60 * 60

# NOTE: в leaflet.js используется гео порядок координат: широта, долгота (lat, lng)
# в GDAL - "компьютерный", широта = Y (ось вниз), долгота = X: (lng, lat)
# для работы с координами я использую формат leaflet
# поэтому в функциях часто можно встретить перевернутые индексы

# assuming file crs is 4326 (WGS84), otherwise will not work
def coord_from_geo(lat, lng, rst):
    """По заданным координатам возвращает индекс ячейки
    с данными о высоте в этих координатах.
    ЗАМЕЧАНИЕ 1: функция работает только с растрами в координатной проекции 4326 (WGS84)
    ЗАМЕЧАНИЕ 2: lat и lng должны быть внутри области

    Параметры:
        lat (float): широта
        lng (float): долгота
        rst (GDALRaster): растр

    Возвращает:
        кортеж: (индекс_строки(j, y), индекс_cтолбца(i, x))
    """
    # узнаем координаты верхнего левого края области,
    # которая хранится в растре, а также размеры матрицы с данными о высоте
    # NOTE: extent возвращает координаты ограничивающего прямоугольника
    # в довольно странном формате - (xmin, ymin, xmax, ymax)
    # поэтому левый верхний угол = (ymax, xmin) (порядок lat lng)
    top_left = (rst.extent[3], rst.extent[0])
    array_dim = (rst.bands[0].width, rst.bands[0].height)
    # вычисляем разрешение растра в угловых секундах по широте и высоте
    # для этого считаем протяженность области в градусах по широте и долготе,
    # домножаем на SEC_PER_DEGREE
    # и делим на соответсвующую размерность матрицы данных
    sec_per_width = (rst.extent[2] - rst.extent[0]) * SEC_PER_DEGREE / array_dim[0]
    sec_per_height = (rst.extent[3] - rst.extent[1]) * SEC_PER_DEGREE / array_dim[1]
    # вычисляем координаты относительно верхнего левого края области (в угловых секундах)
    # NOTE: так как левый верхний угол: (ymax, xmin), то lat <= ymax, но lng >= xmin
    # поэтому top_left[0] - lat, но lng - top_left[1]
    sec_rel_coords = (top_left[0] - lat) * SEC_PER_DEGREE, (lng - top_left[1]) * SEC_PER_DEGREE
    # наконец, вычисляем индекс:
    # делим относительные координаты на разрешение
    return (int(round(sec_rel_coords[0] / sec_per_height, 0)), 
          int(round(sec_rel_coords[1] / sec_per_width, 0)))
    # NOTE: сейчас я уже не совсем понимаю, почему индексы возвращаются в перевернутом формате (Y, X) (aka (j, i))
    # возможно я хотел следовать везде порядку leaflet
    # но в функции get_el путаница = туда якобы передается сначала i, потом j
    # и потом для доступа данным они зачем-то меняются местами (!)
    # на самом деле, так как индексы возвращаются в формате (j, i), то
    # в get_el i = j и  j = i (!!!)
    # TODO: либо изменить порядок параметров функции get_el,
    # либо изменить вызов функции, либо тут изменить порядок на (i, j)


def geo_from_coords(x, y, rst):
    """По заданным индексам ячейки с данными возвращает
    координаты этой ячейки (долгота, широта).

    Args:
        x (int): индекс столбца (?)
        y (int): индекс строки (?)
        rst (GDALRaster): растр

    Returns:
        кортеж: (долгота, широта)
    """
    # для преобразования используем матрицу геотрансформации растра
    gt = rst.geotransform
    x_geo = gt[0] + y*gt[1] + x*gt[2]
    y_geo = gt[3] + y*gt[4] + x*gt[5]
    return y_geo, x_geo

def get_allowed_region():
    """Возвращает координаты нижнего левого и верхнего правого края
    области, хранящейся в FILE.

    Returns:
        кортеж: ((широта_нл, долгота_нл), (широта_вп, долгота_вп))
    """
    # NOTE: насколько помню, leaflet принимает именно такой формат
    # для создания прямоугольника
    a_r = GDALRaster(FILE, write=False).extent
    return ((a_r[1], a_r[0]),(a_r[3], a_r[2]))

def get_el(i, j, band):
    """По индексам ячейки i и j возвращает высоту в этой ячейке
    NOTE: Путаница с индексами

    Args:
        i (int): i, но на самом деле j
        j (int): j, но на самом деле i
        band (GDALBand): band c данными

    Returns:
        int: значение высоты
    """
    return band.data(offset=(j, i), size=(1, 1))[0]

def get_relief(bounds):
    """По заданному ограничивающему прямоугольнику bounds
    возвращает информацию о точке с наибольшей высотой и
    массив с информацией о высоте в пределах этого прямоугольника

    Args:
        bounds (tuple): (широта_вл, долгота_вл, широта_нп, долгота_нп)

    Returns:
        tuple: (инфа_о_точке_с_наибольшей_высотой, двумерный_массив_инфы_о_точках)
               инфа_о_точке = {'elevation': высота(int), 'coords': [lat, lng]}
    """
    rst = GDALRaster(FILE, write=False)
    # находим индексы верхней левой и правой нижней ячейки
    topLeft = coord_from_geo(bounds[0], bounds[1], rst)
    bottomRight = coord_from_geo(bounds[2], bounds[3], rst)
    result = []
    heighest_point = None 
    band = rst.bands[0]
    # TODO: устаревший способ чтения, 
    # можно сразу получить из растра нужную область
    # c помощью band.data(offset=(topLeft[1], topLeft[0]), size=размеры_области)[0]
    # NOTE: из-за путаницы индексом в get_el,
    # i это j, то есть индекс строки
    # а j это i - индекс столбца
    for i in range(bottomRight[0], topLeft[0]+1):
        result.append([])
        for j in range(topLeft[1], bottomRight[1] + 1):
            val = get_el(i, j, band)
            result[-1].append({'elevation': val,
                                'coords': geo_from_coords(i, j, rst)})
            if heighest_point is None or \
                result[-1][-1]['elevation'] > heighest_point['elevation']:
                    heighest_point = result[-1][-1]
    return (heighest_point, result)

def constrain(val, min_val, max_val):    
    return min(max_val, max(min_val, val))

def get_around(x, y, band):
    """По индексам ячеки x и y последовательно возвращает высоты вокруг этой ячейки, включая ее
    Это функция - генератор, она не возвращает сразу весь массив,
    а при каждом очередном вызове возвращает следующее значение в массиве

    Args:
        x (int): строка (?)
        y (int): столбец (?)
        band (GDALBand): band

    Yields:
        tuple: ((x, y), высота)
        Порядок возвращения: (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                             (x - 1, y), (x, y), (x + 1, y),
                             (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)
        
    """
    bounds_x = constrain(x - 1, 0, band.width), constrain(x + 1, 0, band.width) + 1
    height = band.height
    bounds_y = constrain(y - 1, 0, height), constrain(y + 1, 0, height) + 1
    reg = band.data(offset=(bounds_x[0], bounds_y[0]), size=(3, 3))
    for i in range(bounds_x[0], bounds_x[1]):
        for j in range(bounds_y[0], bounds_y[1]):
            if i == x and j == y:
                continue
            yield (i, j), get_el(i, j, band)

def get_distance(latlng1, latlng2):
    """Возвращает расстояние (в метрах)
    между двумя координами.
    TODO: значение считается неправильно

    Args:
        latlng1 (tuple): [lat, lng]
        latlng2 (tuple): [lat, lng]

    Returns:
        float: Расстояние в метрах
    """
    lat_meters = abs(latlng1[0] - latlng2[0]) * 111.139
    lng_meters = abs(latlng1[1] - latlng2[1]) * 111.139
    return sqrt(lat_meters**2 + lng_meters**2)

def get_sin_cos_angle(distance, elevation):
    """Возвращает синус, косинус и угол по
    расстоянию и разнице высот.
    По сути distance (x) - катет, прилежащий к углу
    elevation (y) = катет, противоположный углу

    Args:
        distance (float): расстояние в метрах
        elevation (int): разница высот

    Returns:
        tuple: (sin, cos, angle)
    """
    sin = elevation / distance
    cos = sqrt(1 - sin**2)
    angle = degrees(sinus(sin))
    return sin, cos, angle

def trace_path(start_point, mass, fraction):
    rst = GDALRaster(FILE, write=False)
    band = rst.bands[0]
    current_point = start_point
    coords = coord_from_geo(current_point[0], current_point[1], rst)
    current_point = (coords, get_el(coords[0], coords[1], band))
    count_same = 0
    next_point = None
    velocity = 0
    traced_path = []
    info = []
    while len(traced_path) < 1000:

        for point in get_around(current_point[0][0], current_point[0][1], band):
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
            return traced_path, info, (current_point, next_point)
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