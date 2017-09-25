# -*- coding: utf-8 -*-
# directions = [0, 1, 2, 3, 4, 5, 6, 7]
# directions:{0:N, 1:NE, 2:E, 3:SE, 4:S, 5:SW, 6:W, 7:NW}
import sys
import operator
from math import sqrt
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument('-print', action='store_true')
parser.add_argument('--file', dest = 'filename', required = True)
args = parser.parse_args()


# read context from a file and cast it to the normal form
filename = args.filename
with open(filename) as f:
    lines = f.read().splitlines()
    # remove whitespace lines
    lines = list(filter(str.strip, lines))
    # create a empty grid with length of len(lines)
    grid = [[] for i in range(len(lines))]
    for i in range(len(lines)):
        # remove whitespace in each line
        line = list(filter(str.strip, lines[i]))
        grid[i] = list(map(int, line)) 
    width = len(grid[0])
    height = len(grid)
    # add 0 around the grid
    new_grid = [[] for i in range(height + 2)]
    for i in range(height + 2):
        new_grid[i] = [[] for j in range(width + 2)]
        if i == 0 or i == height + 1:
            for k in range(width + 2):
                new_grid[i][k] = 0
        else:
            for k in range(width + 2):
                if k == 0 or k == width + 1:
                    new_grid[i][k] = 0
                else:
                    new_grid[i][k] = grid[i-1][k-1]
    grid = new_grid[:]
    width = len(grid[0])
    height = len(grid)


# length of lines smaller than 2 or larger than 50
for i in range(len(grid)):
    if len(grid[i]) < 4 or len(grid[i]) > 52:
        print('Incorrect input.')
        sys.exit()
# not all the length of lines the same
for i in range(len(grid) - 1):
    if len(grid[i]) != len(grid[i + 1]):
        print('Incorrect input.')
        sys.exit()
# all the elements must be 0 or 1
for i in range(len(grid)):
    for j in range(len(grid[i])):
        if grid[i][j] is not 0 and grid[i][j] is not 1:
            print('Incorrect input.')
            sys.exit()


# sets of results
results = {}
# all points of a polygon
poly = []
# sets of polygons with all vertex of each polygon
polygons = {}
# dict of depth
depth_dict = {}

# check a point is inside the polygon
def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x or x <= xinters:
                inside = not inside
        p1x, p1y = p2x, p2y
    return inside


# compute the perimeter of the polygon
def polygon_perimeter(poly):
    perimeter1 = 0
    perimeter2 = 0
    for i in range(-1,len(poly)-1):
        # compute the length of vertical or horizontal side
        if poly[i][0] == poly[i+1][0] or poly[i][1] == poly[i+1][1]:
            perimeter1 += abs(poly[i+1][0] - poly[i][0]) + abs(poly[i+1][1] - poly[i][1])
        # compute the length of hypotenuse side
        else:
            perimeter2 += abs(poly[i][0] - poly[i+1][0])
    perimeter1 = round(perimeter1 * 0.4, 1)
    if perimeter1 == 0:
        perimeter = '%s*sqrt(.32)' % (perimeter2)
    else:
        if perimeter2 == 0:
            perimeter = '%s' % (perimeter1)
        else:
            perimeter = '%s + %s*sqrt(.32)' % (perimeter1, perimeter2)
    return perimeter


# compute the area of the polygon
def polygon_area(poly):
    n = len(poly)
    area = 0.00
    for i in range(n):
        j = (i + 1) % n
        area += poly[i][0] * poly[j][1]
        area -= poly[j][0] * poly[i][1]
    area = abs(area) / 2 * 0.16
    return area


# compute the number of invariant rotations
def poly_rotations(poly):
    # compute the value of cos and convex of each vertex
    vertex = []
    for i in range(-1,len(poly)-1):
        dif1 = ((poly[i][0] - poly[i-1][0]),(poly[i][1] - poly[i-1][1]))
        dif2 = ((poly[i+1][0] - poly[i][0]),(poly[i+1][1] - poly[i][1]))
        # compute inner product and the length of each vector
        inner_product = (dif1[0] * dif2[0]) + (dif1[1] * dif2[1])
        dif1_length = sqrt(dif1[0] ** 2 + dif1[1] ** 2)
        dif2_length = sqrt(dif2[0] ** 2 + dif2[1] ** 2)
        cos_value = inner_product / (dif1_length * dif2_length)
        # check the vertex is convex or not
        new_poly = poly[:]
        new_poly.pop(i)
        area = polygon_area(poly)
        new_area = polygon_area(new_poly)
        if new_area > area:
            convex = 1
        else:
            convex = 0
        vertex.append((cos_value,convex,dif1_length,dif2_length))
    nb_of_invariant_rotations = 0
    for i in range(1, len(vertex) + 1):
        new_vertex = vertex[len(vertex)-i:len(vertex)] + vertex[:-i]
        if new_vertex == vertex:
            nb_of_invariant_rotations += 1
    return nb_of_invariant_rotations


# compute the depth of the polygon
def polygon_depth(poly):
    depth = 0
    x = poly[0][0]
    y = poly[0][1]
    for i in polygons:
        is_point_inside_polygon = point_inside_polygon(x, y, polygons[i])
        if is_point_inside_polygon == True:
            depth += 1
    return depth


# check the polygon is convex
def poly_convex(area,poly):
    convex = 'yes'
    if len(poly) != 3:
        for i in range(len(poly)):
            new_poly = poly[:]
            new_poly.pop(i)
            new_area = polygon_area(new_poly)
            if new_area > area:
                convex = 'no'
                break
    return convex


# delete the redundant points
def get_polygons(poly):
    points_not_vertex = []
    for i in range(-1, len(poly)-1):
        dif1 = ((poly[i][0] - poly[i-1][0]),(poly[i][1] - poly[i-1][1]))
        dif2 = ((poly[i+1][0] - poly[i][0]),(poly[i+1][1] - poly[i][1]))
        if dif1 == dif2:
            points_not_vertex.append(poly[i])
    for i in points_not_vertex:
        poly.remove(i)
    return poly


# get point by direction one by one
def get_point_by_direction(i, j, search_direction):
    if search_direction == 0:
        i = i - 1
        j = j
    if search_direction == 1:
        i = i - 1
        j = j + 1
    if search_direction == 2:
        i = i
        j = j + 1
    if search_direction == 3:
        i = i + 1
        j = j + 1
    if search_direction == 4:
        i = i + 1
        j = j
    if search_direction == 5:
        i = i + 1
        j = j - 1
    if search_direction == 6:
        i = i
        j = j - 1
    if search_direction == 7:
        i = i - 1
        j = j - 1
    return i, j, search_direction


# find next point
def find_next_point(i, j, line_direction):
    for k in range(5, 13):
        search_direction = (line_direction + k) % 8
        m, n, new_line_direction = get_point_by_direction(i, j, search_direction)
        if grid[m][n] == 1:
            grid[m][n] = 0
            break
        else:
            m = None
            n = None
            new_line_direction = None
            continue
    return m, n, new_line_direction


# get direction by vector
def get_direction(direction_vector):
    if direction_vector == (-1,0):
        return 0
    if direction_vector == (-1,1):
        return 1
    if direction_vector == (0,1):
        return 2
    if direction_vector == (1,1):
        return 3
    if direction_vector == (1,0):
        return 4
    if direction_vector == (1,-1):
        return 5
    if direction_vector == (0,-1):
        return 6
    if direction_vector == (-1,-1):
        return 7


# find a polygon with start point (i,j) with direction
def find_polygon(i, j, line_direction):
    poly.append((i, j))
    m, n, lnew_ine_direction = find_next_point(i, j, line_direction)
    # if cannot find next point, set the value into 2, remove the last elemnt of poly and find continue 
    if m == n == lnew_ine_direction == None:
        if len(poly) == 1:
            print('Cannot get polygons as expected.')
            sys.exit()
        else:
            grid[i][j] = 2
            poly.pop()
            i = poly[len(poly)-1][0]
            j = poly[len(poly)-1][1]
            direction_vector = ((poly[len(poly)-1][0] - poly[len(poly)-2][0]),(poly[len(poly)-1][1] - poly[len(poly)-2][1]))
            line_direction = get_direction(direction_vector)
            poly.pop()
            find_polygon(i, j, line_direction)
    # if the point is in the poly then this is the start
    elif (m, n) in poly:
        pass
    # if the point is not in the poly and the point is not the start point
    elif (m, n) not in poly:
        find_polygon(m, n, lnew_ine_direction)


# find polygons
for i in range(height):
    for j in range(width):
        if grid[i][j] == 1:
            find_polygon(i, j, 2)
            # if the length of poly is 2, incorrect output
            if len(poly) <= 2:
                print('Cannot get polygons as expected.')
                sys.exit()
            else:
                vertex = get_polygons(poly)
                # move the point to left top conner to remove the effect of 0s around the grid
                vertex = [(v[0] - 1, v[1] - 1) for v in vertex]
                polygons[len(polygons) + 1] = vertex
                poly = []
            # reset all the 2 into 1
            for m in range(height):
                for n in range(width):
                    if grid[m][n] == 2:
                        grid[m][n] = 1


max_area = polygon_area(polygons[1])
min_area = polygon_area(polygons[1])
for i in polygons:
    perimeter = polygon_perimeter(polygons[i])
    area = polygon_area(polygons[i])
    max_area = max(max_area, area)
    min_area = min(min_area, area)
    convex = poly_convex(area,polygons[i])
    nb_of_invariant_rotations = poly_rotations(polygons[i])
    depth = polygon_depth(polygons[i])
    result = (perimeter, area, convex, nb_of_invariant_rotations, depth)
    results[i] = result
    depth_dict[i] = depth


#sort the depth_dict by depth asc
depth_dict = sorted(depth_dict.items(), key=operator.itemgetter(1))


# results = {1: (1, 2, 'yes', 4, 5), 2: (3, 4, 'no', 5, 6)}
for x in results:
    print(f"Polygon {x}:")
    print(f"    Perimeter: {results[x][0]}")
    print(f"    Area: {results[x][1]:.2f}")
    print(f"    Convex: {results[x][2]}")
    print(f"    Nb of invariant rotations: {results[x][3]}")
    print(f"    Depth: {results[x][4]}")


if args.print == True:
    tex_filename = filename.split('.')[0] + '.tex'
    with open(tex_filename, 'w') as tex_file:
        print('\\documentclass[10pt]{article}\n'
              '\\usepackage{tikz}\n'
              '\\usepackage[margin=0cm]{geometry}\n'
              '\\pagestyle{empty}\n'
              '\n'
              '\\begin{document}\n'
              '\n'
              '\\vspace*{\\fill}\n'
              '\\begin{center}\n'
              '\\begin{tikzpicture}[x=0.4cm, y=-0.4cm, thick, brown]', file = tex_file)


        print(f'\\draw[ultra thick] (0, 0) -- ({width-3}, 0) -- ({width-3}, {height-3}) -- (0, {height-3}) -- cycle;', file = tex_file)

        # first line
        print(f'%Depth {results[1][4]}', file = tex_file)
        first_line = ''
        for j in polygons[1]:
            first_line += '(%s, %s) -- ' % (j[1], j[0])
        first_area = results[1][1]
        first_colour = (max_area - first_area) * 100 / (max_area - min_area)
        first_colour = int(round(first_colour,0))
        print(f'\\filldraw[fill=orange!{first_colour}!yellow] {first_line}cycle;', file = tex_file)

        # from second line
        for i in range(1,len(depth_dict)):
            if depth_dict[i-1][1] != depth_dict[i][1]:
                print(f'%Depth {depth_dict[i][1]}', file = tex_file)
            print_line = ''
            for j in polygons[depth_dict[i][0]]:
                print_line += '(%s, %s) -- ' % (j[1], j[0])
            area = results[depth_dict[i][0]][1]
            colour = (max_area - area) * 100 / (max_area - min_area)
            colour = int(round(colour,0))
            print(f'\\filldraw[fill=orange!{colour}!yellow] {print_line}cycle;', file = tex_file)


        print('\\end{tikzpicture}\n'
              '\\end{center}\n'
              '\\vspace*{\\fill}\n'
              '\n'
              '\\end{document}', file = tex_file)