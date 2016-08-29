from math import pi, cos, tan, radians, log


def calc_tile(lng, lat, zoomlevel):
    tilecounts = [1, 1, 1, 40, 40, 80, 80, 320, 1E3, 2E3, 2E3, 4E3, 8E3, 16E3, 16E3, 32E3]
    rlat = radians(lat)
    tilecount = tilecounts[zoomlevel]
    x_tile = int((lng + 180.0) / 360.0 * tilecount)
    y_tile = int((1.0 - log(tan(rlat) + (1 / cos(rlat))) / pi) / 2.0 * tilecount)
    return x_tile, y_tile


# data example
# can be found in iitc consule log
# 113.85128617286682,22.565680958159387,113.8652765750885,22.572606084022222

region = input('Data:\n').split(',')
maxlng = float(region[2])
maxlat = float(region[3])
minlng = float(region[0])
minlat = float(region[1])
minxtile, maxytile = calc_tile(minlng, minlat, 15)
maxxtile, minytile = calc_tile(maxlng, maxlat, 15)
tilekeys = ''
for xtile in range(minxtile, maxxtile + 1):
    for ytile in range(minytile, maxytile + 1):
        tilekey = '15_{}_{}_0_8_100'.format(xtile, ytile)
        tilekeys += '\"' + tilekey + '\", '
print(tilekeys)
