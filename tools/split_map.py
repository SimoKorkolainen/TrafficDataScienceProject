#!/usr/bin/env python3

from PIL import Image
Image.MAX_IMAGE_PIXELS = 1000000000   

from scipy import misc
import numpy as np
import math

north = 8388608.00
west = -548576.00
tile_size = 1024

#zoom_level = 7
#source_files = ['Taustakartta_320']
#zoom_level = 8
#source_files = ['K3', 'K4', 'L3', 'L4', 'L5', 'M3',  'M4', 'M5']
#zoom_level = 9
#source_files = ['K3R', 'K4L', 'K4R', 'L3R', 'L4L', 'L4R',  'M3R', 'M4L', 'M4R']
zoom_level = 10
source_files = ['K34R', 'K42L', 'K42R', 'L33R', 'L41L', 'L41R',  'L42L', 'L42R', 'L43L', 'L43R', 'L44L', 'L44R']

maps = []
map_west = []
map_north = []

for source_file in source_files:
    # Read World file
    world_data = []
    with open(str(zoom_level) + '/' + source_file + '.pgw') as f:
        world_data = f.read()
    world_data = world_data.split()
    delta_x = float(world_data[0])
    delta_y = float(world_data[3])
    map_west.append( float(world_data[4]) )
    map_north.append( float(world_data[5]) )
    # Read the map image
    maps.append( misc.imread(str(zoom_level) + '/' + source_file + '.png') )

# find dimensions of the area we are working with
max_west = float('Inf')
max_east = float('-Inf')
max_north = float('-Inf')
max_south = float('Inf')
for i in range(0, len(maps) ):
    if map_west[i] - abs(delta_x / 2) < max_west:
        max_west = map_west[i] - abs(delta_x / 2)
    if map_north[i] - abs(delta_y / 2) > max_north:
        max_north = map_north[i] - abs(delta_y / 2)

    height, width, colours = maps[i].shape
    map_east = map_west[i] - abs(delta_x / 2) + width * delta_x
    map_south = map_north[i] - abs(delta_y / 2) + height * delta_y

    if map_east > max_east:
        max_east = map_east
    if map_south < max_south:
        max_south = map_south

y_size = int((max_north-max_south ) / abs( delta_y ))
x_size = int((max_east-max_west ) / abs( delta_x) )
world = np.zeros( ( y_size, x_size, 3 ) )
# put map data to the world
for i in range(0, len(maps) ):
    x_start = int(( map_west[i] - abs(delta_x / 2) - max_west ) / abs( delta_x) )
    y_start = int(( max_north - map_north[i] + abs(delta_y / 2) ) / abs( delta_x) )
    height, width, colours = maps[i].shape
    world[ y_start : y_start + height, x_start : x_start + width, : ] = maps[i]

north_tile = int( math.ceil( (north - max_north) / ( abs( delta_y) * tile_size ) ) )
south_tile = int( math.floor( (north - max_south) / ( abs( delta_y) * tile_size ) ) )
west_tile = int( math.ceil( abs(max_west - west) / ( abs( delta_x) * tile_size ) ) )
east_tile = int( math.floor( abs(max_east - west) / ( abs( delta_x) * tile_size ) ) )

for x in range( west_tile, east_tile + 1 ):
    for y in range( north_tile, south_tile + 1 ):
        y_top = int( (max_north + delta_y / 2 - (north + y * delta_y * tile_size )) / abs(delta_y) )
        x_left = int( (west + x * delta_x * tile_size - max_west - delta_x / 2) / abs(delta_x) )
        print( x_left, y_top)
        tile = world[ y_top : y_top + tile_size, x_left : x_left + tile_size ]
        misc.imsave( str(zoom_level) + '/' + str(x) + '_' + str(y) + '.png', tile)      


#for x in [12, 13, 14, 15, 16, 17]:
#    for y in [24, 25, 26]:
#        y_top = int( (map_north + delta_y / 2 - (north + y * delta_y * tile_size )) / 64 )
#        x_left = int( (west + x * delta_x * tile_size - map_west - delta_x / 2) / 64 )
#        print( x_left, y_top)
#        tile = world[ y_top : y_top + 1024, x_left : x_left + 1024 ]
#        misc.imsave( str(zoom_level) + '/' + str(x) + '_' + str(y) + '.png', tile)

