#Written by Yakun Zhao for COMP9021 assignment2

import sys
import re
import copy
from math import sqrt
from argparse import ArgumentParser

#from PIL import Image

parser = ArgumentParser()
parser.add_argument('-print', action='store_true')
parser.add_argument('--file', dest = 'filename', required = True)
args = parser.parse_args()

filename = args.filename
def org_grid():
    org_grid = []
    try:
        #with open('polys_2.txt') as file:
        with open(filename) as file:
            for line in file:
                line_of_grid = re.findall(r'[\d]', line)
                if line_of_grid != []:
                    org_grid.append(line_of_grid)
    except ValueError:
        print ("Incorrect input.")
        sys.exit()
    return org_grid

org_grid = org_grid()
height = len(org_grid)
width = len(org_grid[0])

# two incorrect situations
try:
    if width > 50 or width < 2 or height > 50 or height < 2:
        raise ValueError
    for i in range(height):
        for j in range(width):
            if org_grid[i][j] is not '0' and org_grid[i][j] is not '1':
                raise ValueError
except ValueError:
    print ("Incorrect input.")
    sys.exit()


#add a circle 0 around the org_grid to avoid overflow
zero_grid = []
for i in range(height+2):
    zero_grid.append([])
    for j in range(width+2):
        zero_grid[i].append([])
        if i == 0 or i == height +1:
            zero_grid[i][j] = '0'
        else:
            if j == 0 or j == width+1:
                zero_grid[i][j] = '0'
            else:
                zero_grid[i][j] = org_grid[i-1][j-1]
grid = zero_grid
height = len(grid)
width = len(grid[0])
               
         

path = []
dir_dic = {0:'N', 1:'NE', 2:'E', 3:'SE', 4:'S', 5:'SW', 6:'W', 7:'NW'}



def just_vertex(path):
    path_vertex = path
    path_not_vertex = []
    path_vertex.append((path[0][0],path[0][1]))
    for i in range(len(path)-2):
        vector1 = (path[i+1][0]-path[i][0],path[i+1][1]-path[i][1])
        vector2 = (path[i+2][0]-path[i+1][0],path[i+2][1]-path[i+1][1])
        if vector1 != vector2:
            continue
        else:
            path_not_vertex.append(path[i+1])
    for e in path_not_vertex:
        path_vertex.remove(e)
    return path_vertex
    


def just_perimeter(path_vertex):
    straight_line = 0
    slash_line = 0
    for i in range(len(path_vertex)-1):
        if path_vertex[i+1][0] == path_vertex[i][0] or path_vertex[i+1][1] == path_vertex[i][1]:
            straight_line += abs(path_vertex[i+1][0] - path_vertex[i][0]) + abs(path_vertex[i+1][1] - path_vertex[i][1])
        elif path_vertex[i+1][0] != path_vertex[i][0] and path_vertex[i+1][1] != path_vertex[i][1]:
            slash_line += abs(path_vertex[i+1][0] - path_vertex[i][0])
    straight_line = round(straight_line * 0.4, 1)
    if straight_line == 0:
        if slash_line == 0:
            poly_perimeter = 0
        else:
            poly_perimeter = '%s*sqrt(.32)' % (slash_line)
    else:
        if slash_line == 0:
            poly_perimeter = straight_line
        else:
            poly_perimeter = '%s + %s*sqrt(.32)' % (straight_line, slash_line)
    return poly_perimeter



def just_area(path_vertex):
    temp_area = 0.00
    for i in range(len(path_vertex)):
        j = (i + 1) % len(path_vertex)
        temp_area += path_vertex[i][0] * path_vertex[j][1] - path_vertex[j][0] * path_vertex[i][1]
    poly_area = abs(temp_area) / 2 * (0.4 ** 2)
    return poly_area



def just_convex(poly_area, path_vertex):
    poly_convex = 'yes'
    org_area = poly_area
    if len(path_vertex) > 3:
        for i in range(len(path_vertex)):
            copied_vertex = copy.deepcopy(path_vertex)
            copied_vertex.pop(i)
            new_area = just_area(copied_vertex)
            if new_area <= org_area:
                poly_convex = 'yes'
            else:
                poly_convex = 'no'
                break           
    return poly_convex

        

# cos(each_vertex), convex(each_vertex), left_side_long, right_side_long 
def just_inv_roat(poly_area, path_convex):
    org_area = poly_area
    path_convex.pop()
    vertex_inf = []
    for i in range(-1, len(path_convex)-1):
        j = i + 1
        # i+1 point   2 vector
        notclockwise_vector = (path_convex[i][0] - path_convex[i-1][0], path_convex[i][1] - path_convex[i-1][1])
        clockwise_vector = (path_convex[i+1][0] - path_convex[i][0], path_convex[i+1][1] - path_convex[i][1])
        # i+1 point   2 edge
        notclockwise_long = sqrt(notclockwise_vector[0] ** 2 + notclockwise_vector[1] ** 2)
        clockwise_long = sqrt(clockwise_vector[0] ** 2 + clockwise_vector[1] ** 2)
        # i+1 point cos
        cos_vertex = (notclockwise_vector[0] * clockwise_vector[0] + notclockwise_vector[1] * clockwise_vector[1]) / (notclockwise_long * clockwise_long)
        # i+1 judge if it is convex
        copied_vertex = copy.deepcopy(path_vertex)
        copied_vertex.pop(i)
        new_area = just_area(path_vertex)
        if new_area <= org_area:
            poly_convex = 'yes'
        else:
            poly_convex = 'no'
        vertex_inf.append((cos_vertex, poly_convex, notclockwise_long, clockwise_long))
    #print(vertex_inf)
    number_of_roat = 0
    for i in range(1, len(vertex_inf)+1):
        front_vertex = vertex_inf[:-i]
        last_vertex = vertex_inf[len(vertex_inf)-i:]
        compared_inf = last_vertex + front_vertex
        if compared_inf == vertex_inf:
            number_of_roat += 1
    return number_of_roat



def judge_inside_point(testx, testy, path_vertex):
    if_point_inside = False
    polyx1 = path_vertex[0][0]
    polyy1 = path_vertex[0][1]
    polysides = len(path_vertex)+1
    for i in range(polysides):
        polyx2 = path_vertex[i % len(path_vertex)][0]
        polyy2 = path_vertex[i % len(path_vertex)][1]
        if min(polyy1, polyy2) < testy <= max(polyy1, polyy2) and testx <= max(polyx1, polyx2):
            if polyy2 != polyy1:
                diff = (testy - polyy1) * (polyx2 - polyx1) / (polyy2 - polyy1) + polyx1
            if polyx1 == polyx2 or testx <= diff:
                if_point_inside = not if_point_inside
        polyx1 = polyx2
        polyy1 = polyy2
##        if (polyy2 < testy and polyy1 >=testy) or (polyy1 < testy and polyy2 >= testy) and testx <= max(polyx1, polyx2):
##            if (polyx2 + (testy - polyy2))/(polyy1-polyy2) * (polyx1 - polyx2) < testx:
##                if_point_inside = not if_point_inside
    return if_point_inside



def just_depth(path_vertex):
    poly_depth = 0
    testx = path_vertex[0][0]
    testy = path_vertex[0][1]
    for i in path_dic:
        if_point_inside = judge_inside_point(testx, testy, path_dic[i])
        if if_point_inside == True:
            poly_depth += 1
    return poly_depth



#(i-1,j),(i-1,j+1),(i,j+1),(i+1,j+1),(i+1,j),(i+1,j-1),(i,j-1),(i-1,j-1)
#   N       NE        E        SE       S        SW       W        NW
#L = [(i-1,j),(i-1,j+1),(i,j+1),(i+1,j+1),(i+1,j),(i+1,j-1),(i,j-1),(i-1,j-1)]
# find the next point which is a 1
def get_next_point(i,j,direction):
    # find next point from the correct direction
    for w in range(5,13):
        find_dir = (direction + w) % 8
        if find_dir == 0:
            i0 = i-1
            j0 = j
        elif find_dir == 1:
            i0 = i-1
            j0 = j+1
        elif find_dir == 2:
            i0 = i
            j0 = j+1
        elif find_dir == 3:
            i0 = i+1
            j0 = j+1
        elif find_dir == 4:
            i0 = i+1
            j0 = j
        elif find_dir == 5:
            i0 = i+1
            j0 = j-1
        elif find_dir == 6:
            i0 = i
            j0 = j-1
        elif find_dir == 7:
            i0 = i-1
            j0 = j-1
        new_direction = find_dir
        if grid[i0][j0] == '1':
            grid[i0][j0] = '0'
            break
        else:
            # if there is no 1 for this 1
            i0 = 'zero1'
            j0 = 'zero1'
            new_direction = 'zero1'
            #continue
    return i0,j0, new_direction



#find (i,j) = 1 and begin with it and find a polygon     
def get_polygon(i, j, direction):
    path.append((i,j))
    i0, j0, new_direction = get_next_point(i,j,direction)       
    if i0 == 'zero1' and j0 == 'zero1' and new_direction == 'zero1':
        #if there is only one point in the path, means incorrect
        if len(path) == 1:
            print('Cannot get polygons as expected.')
            sys.exit()
        else:
            #if it is a end road, set that point to 'end' point, and pop it from the path            
            grid[i][j] = 'end'
            path.pop()
            # and go back to the last i,j continue from next direction
            i = path[len(path)-1][0]
            j = path[len(path)-1][1]
            continue_dir_vector = (path[len(path)-2][0] - i, path[len(path)-2][1] - j)
            if continue_dir_vector == (0,1):
                last_direction = 0
            elif continue_dir_vector == (1,1):
                last_direction = 1
            elif continue_dir_vector == (1,0):
                last_direction = 2
            elif continue_dir_vector == (1,-1):
                last_direction = 3
            elif continue_dir_vector == (0,-1):
                last_direction = 4
            elif continue_dir_vector == (-1,-1):
                last_direction = 5
            elif continue_dir_vector == (-1,0):
                last_direction = 6
            elif continue_dir_vector == (-1,1):
                last_direction = 7
            path.pop()
            get_polygon(i, j, last_direction)
    elif (i0, j0) in path:
        pass
    elif (i0, j0) not in path:
        get_polygon(i0, j0, new_direction)
    return path



#from the left-up corner , begin to find polygons
# n polygons: n path
path_dic = {}
# n polygons: n path_vertex
vertex_dic = {}
# n polygons: n each_perimeter
perimeter_dic = {}
# n polygons: n each_area
area_dic = {}
# n polygons: n each_convex
convex_dic = {}
# n polygons: n each_roat
inv_roat_dic = {}
# n polygons: n each_depth
depth_dic = {}
#polygons's index, which is the key of other dictionaries
path_index = 1
for i in range(height):
    for j in range(width):
        if grid[i][j] == '1' :
            path = get_polygon(i,j,2)
            if len(path) <= 2:
                print('Cannot get polygons as expected.')
                sys.exit()
            else:
                #put each path into the dic
                path_dic[path_index] = path
                #get each path's vertexs and put each of them into the dic
                path_vertex = just_vertex(path)
                vertex_dic[path_index] = path_vertex
                #get each polygons' perimeter and put each of them into the dic
                each_perimeter = just_perimeter(path_vertex)
                perimeter_dic[path_index] = each_perimeter
                #get each polygons' area and put each of them into the dic
                each_area = just_area(path_vertex)
                area_dic[path_index] = each_area
                #get each polygons' convex and put each of them into the dic
                each_convex = just_convex(each_area, path_vertex)
                convex_dic[path_index] = each_convex
                #get each polygons' times of invariant rotations and put each of them into the dic
                each_roat = just_inv_roat(each_area, path_vertex)
                inv_roat_dic[path_index] = each_roat
                #get each polygons' depth and put each of them into the dic
                each_depth = just_depth(path_vertex)
                depth_dic[path_index] = each_depth

                path_index += 1
                path = []
            for a in range(height):
                for b in range(width):
                    if grid[a][b] == 'end':
                        grid[a][b] = '1'

#keep 2 decimal place in the number, including two zero.
for i in range(1,len(area_dic)+1):
    area_dic[i] = '%.2f' % area_dic[i]

##for i in range(1,len(path_dic)+1):
##    print(f'Polygon {i}:')
##    print(f'    Perimeter: {perimeter_dic[i]}')
##    print(f'    Area: {area_dic[i]}')
##    print(f'    Convex: {convex_dic[i]}')
##    print(f'    Nb of invariant rotations: {inv_roat_dic[i]}')
##    print(f'    Depth: {depth_dic[i]}')


for i in range(1,len(path_dic)+1):
    print('Polygon {}:'. format(i))
    print('    Perimeter: {}'. format(perimeter_dic[i]))
    print('    Area: {}'. format(area_dic[i]))
    print('    Convex: {}'. format(convex_dic[i]))
    print('    Nb of invariant rotations: {}'. format(inv_roat_dic[i]))
    print('    Depth: {}'. format(depth_dic[i]))



height = len(grid) - 2
width = len(grid[0]) - 2
#samedepth_dic is {depth:[depth_index]}
#looks like this
#{0: [1, 4, 6], 1: [2, 8, 10, 33], 2: [3, 12, 14, 34], 3: [5, 16, 18, 35], 4: [7, 20, 22, 36]
#, 5: [9, 23, 24, 37], 6: [11, 25, 26, 38], 7: [13, 27, 28, 39]
#, 8: [15, 29, 30, 40], 9: [17, 31, 32, 41], 10: [19, 42], 11: [21, 43]}
samedepth_dic = {}
largest_depth = 0
for i in range(1, len(depth_dic)+1):
    if largest_depth < depth_dic[i]:
        largest_depth = depth_dic[i]
for i in range(largest_depth+1):
    samedepth_dic[i] = []    
for i in range(1, len(depth_dic)+1):
    depth_index = depth_dic[i]
    for e in samedepth_dic:
        if e == depth_index:
            samedepth_dic[e].append(i)

max_area = 0.00
min_area = float(area_dic[1])
for i in range(1, len(area_dic)+1):
    if max_area < float(area_dic[i]):
        max_area = float(area_dic[i])
    if min_area > float(area_dic[i]):
        min_area = float(area_dic[i])


##if args.print == True:
##    tex_filename = filename + '.tex'
##    with open(tex_filename, 'w') as tex_file:
##        print('\\documentclass[10pt]{article}\n'
##              '\\usepackage{tikz}\n'
##              '\\usepackage[margin=0cm]{geometry}\n'
##              '\\pagestyle{empty}\n'
##              '\n'
##              '\\begin{document}\n'
##              '\n'
##              '\\vspace*{\\fill}\n'
##              '\\begin{center}\n'
##              '\\begin{tikzpicture}[x=0.4cm, y=-0.4cm, thick, brown]', file = tex_file)
##
##        print(f'\\draw[ultra thick] (0, 0) -- ({width-1}, 0) -- ({width-1}, {height-1}) -- (0, {height-1}) -- cycle;', file = tex_file)        
##        for i in range(len(samedepth_dic)):
##            print(f'%Depth {i}', file = tex_file)
##            for j in range(len(samedepth_dic[i])):
##                vertex_line = ''
##                target_vertex = vertex_dic[samedepth_dic[i][j]]
##                for z in range(len(target_vertex)):
##                    vertex_line += '(%s, %s) -- ' % (target_vertex[z][1]-1, target_vertex[z][0]-1)
##                now_area = float(area_dic[samedepth_dic[i][j]])
##                mid_number = ((max_area - now_area) / (max_area - min_area)) * 100
##                mid_number = int(round(mid_number, 0))
##                print(f'\\filldraw[fill=orange!{mid_number}!yellow] {vertex_line}cycle;', file = tex_file)
##
##
##        print('\\end{tikzpicture}\n'
##              '\\end{center}\n'
##              '\\vspace*{\\fill}\n'
##              '\n'
##              '\\end{document}', file = tex_file)        

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

        print('\\draw[ultra thick] (0, 0) -- ({}, 0) -- ({}, {}) -- (0, {}) -- cycle;'. format(width-1, width-1, height-1, height-1), file = tex_file)        
        for i in range(len(samedepth_dic)):
            print('%Depth {}'. format(i), file = tex_file)
            for j in range(len(samedepth_dic[i])):
                target_vertex = vertex_dic[samedepth_dic[i][j]]
                vertex_line = ''
                for z in range(len(target_vertex)):
                    vertex_line += '(%s, %s) -- ' % (target_vertex[z][1]-1, target_vertex[z][0]-1)
                now_area = float(area_dic[samedepth_dic[i][j]])
                mid_number = ((max_area - now_area) / (max_area - min_area)) * 100
                mid_number = int(round(mid_number, 0))
                print('\\filldraw[fill=orange!{}!yellow] {}cycle;'. format(mid_number, vertex_line), file = tex_file)


        print('\\end{tikzpicture}\n'
              '\\end{center}\n'
              '\\vspace*{\\fill}\n'
              '\n'
              '\\end{document}', file = tex_file)        
