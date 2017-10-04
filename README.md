# Polygons
An assignment of COMP9021(Programming Principles) written in Python3. Implemented some basic functions related to polygons like perimeter computation, area computation, convex property checking and so on.


function polygon_area(poly): Computing the current polygon area by the (x,y) value of points. Input a polygon (a list of points), return a number which is area.

function polygon_depth(poly): Finding how many polygons there are around the current polygon. Input a polygon (a list of points), return a number which is depth.

function poly_convex(area,poly): Finding the convex property of the current polygon. Input a polygon (a list of points) and an original area, computing the current area by removing a point every time, if current area is larger than original area then break the loop and the polygon is not convex. Return the convex property at last.

function poly_rotations(poly): Computing the number of invariant rotations. Input a polygon (a list of points), irritate the list by move the first point to the last one which makes a new list and compare the new list with the original list every time, if they are same then make the number of invariant rotations plus one. Return the number at last.
