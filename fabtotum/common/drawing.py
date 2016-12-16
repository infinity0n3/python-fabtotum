#!/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016 FABtotum, http://www.fabtotum.com
#
# This file is part of FABUI.
#
# FABUI is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# FABUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FABUI.  If not, see <http://www.gnu.org/licenses/>.

__authors__ = "Daniel Kesler"
__license__ = "GPL - https://opensource.org/licenses/GPL-3.0"
__version__ = "1.0"

# Import external modules
import numpy as np
from fabtotum import dxfgrabber

class Layer2D(object):
    def __init__(self, name, color = 255):
        self.name = name
        self.color = color
        self.primitives = []
        
    def addPrimitive(self, data):
        self.primitives.append(data)

class Drawing2D(object):
    """
    :todo: 
       - filled circle
       - filled ellipse
       - filled polyline
    """
    
    def __init__(self):
        self.primitives = []
        self.layers = []
        self.max_x = 0
        self.max_y = 0
        self.min_x = 0
        self.min_y = 0
    
    def extend_bounds(self, points):
        
        if type(points) is list:
            pass
        elif type(points) is tuple:
            points = [ points ]
        else:
            print 'neither a tuple or a list'
            return
        
        for pt in points:
            if pt[0] > self.max_x:
                self.max_x = pt[0]
                
            if pt[0] < self.min_x:
                self.min_x = pt[0]
                
            if pt[1] > self.max_y:
                self.max_y = pt[1]
                
            if pt[1] < self.min_y:
                self.min_y = pt[1]
    
    def add_layer(self, name = None, color = 255):
        idx = len(self.layers)
        if name is None:
            name = 'Layer_{0}'.format(idx)
        #data = {'name' : name, 'primitives' : [], 'color' : color}
        layer = Layer2D(name, color)
        self.layers.append(layer)
        return idx
        
    def add_rect(self, x1, y1, x2, y2, layer = 0, filled = False):
        points = [
            (x1,y1),
            (x2,y1),
            (x2,y2),
            (x1,y2)
        ]
        data = { 'type' : 'rect', 'first': (x1,y1), 'second' : (x2,y2), 'points' : points, 'filled' : filled }
        self.layers[layer].addPrimitive(data)
        self.extend_bounds(points)
        
    def add_line(self, start, end, layer = 0):
        data = { 'type' : 'line', 'points': [start, end] }
        self.layers[layer].addPrimitive(data)
        
        self.extend_bounds(start)
        self.extend_bounds(end)
        
    def add_polyline(self, points, closed = False, layer = 0, filled = False):
        if closed:
            points.append(points[0])
        data = { 'type' : 'polyline', 'points' : points, 'closed' : closed, 'filled' : filled }
        self.layers[layer].addPrimitive(data)
        self.extend_bounds(points)
        
    def add_circle(self, center, radius, layer = 0, filled = False):
        points = self.__circle(center, radius)
        data = { 'type' : 'circle', 'center' : center, 'radius' : radius, 'points' : points, 'filled' : filled }
        self.layers[layer].addPrimitive(data)
        self.extend_bounds(points)
    
    def add_arc(self, center, radius, start, end, layer = 0):
        points = self.__arc(center, radius, start, end)
        data = { 'type' : 'arc', 'center' : center, 'radius' : radius, 'start' : start, 'end': end, 'points' : points }
        self.layers[layer].addPrimitive(data)
        self.extend_bounds(points)
    
    def add_spline(self, control_points, knots, degree, layer = 0):
        
        npts = len(control_points)
        k = degree + 1
        #~ p1 = (dxf.header['$SPLINESEGS'] or 8) * npts
        p1 = (8) * npts
        
        points = self.__rbspline(npts, k, p1, control_points, knots)
        
        data = { 'type' : 'spline', 'control_points' : control_points, 'knots' : knots, 'degree' : degree, 'points' : points}
        #~ self.primitives.append(data)
        self.layers[layer].addPrimitive(data)
        self.extend_bounds(points)
    
    def add_ellipse(self, center, major_axis, ratio, start, end, layer = 0, filled = False):
        points = self.__ellipse(center, major_axis, ratio, start, end)
        data = { 'type' : 'ellipse', 'center' : center, 'major_axis' : major_axis, 'ratio' : ratio, 'start' : start, 'end' : end, 'points' : points, 'filled' : filled}
        #~ self.primitives.append(data)
        self.layers[layer].addPrimitive(data)
        self.extend_bounds(points)
    
    def __ellipse_point(self, center, r1, r2, rotM, t):
        x1 = r1 * np.cos( np.radians(t) )
        y1 = r2 * np.sin( np.radians(t) )
        tmp = np.array([x1,y1])
        p1 = center + (tmp * rotM)
        return p1.A1[0], p1.A1[1]
        
    def __ellipse(self, center, axis, ratio, start, end, step = 10.0):
        
        points = []
        x0 = center[0]
        y0 = center[1]
        # Get length of axis vector
        r1 = np.linalg.norm(axis)
        # Get second radius
        r2 = r1 * ratio
        
        # Get axis angle
        if axis[0] == 0:
            a = np.radians(90.0) 
        elif axis[1] == 0:
            a = np.radians(0.0) 
        else:
            a = np.arctan(axis[1] / axis[0])

        # Prepare rotation matrix
        center = np.array([x0,y0])
        c1 = np.cos(a)
        c2 = np.sin(a)
        rotM = np.matrix([
            [c1,c2],
            [-c2,c1]
        ])
        rotMCCW = np.matrix([
            [c1,-c2],
            [c2,c1]
        ])
        
        eye = np.matrix([ [1.0, 0.0], [0.0, 1.0] ])
        
        fix = 0
        if start > end:
            start += 180.0
            if start > 360.0:
                start -= 360.0
            end += 180.0
                   
        have_prev = False
        
        tl = np.arange(start, end, step)
        
        for t in tl:
            x2,y2 = self.__ellipse_point(center, r1, r2, rotM, t)

            points.append( (x2,y2) )

            #if have_prev:
                #self.draw_line(x1,y1, x2,y2)
            
            x1 = x2
            y1 = y2
            have_prev = True

        x2,y2 = self.__ellipse_point(center, r1, r2, rotM, end)
        points.append( (x2,y2) )
        #self.draw_line(x1,y1, x2,y2)
        
        return points
        
    def __circle(self, center, radius, step = 10.0):
        x0 = center[0]
        y0 = center[1]
        r = radius
        points = []
        start = 0.0
        end = 360.0
        steps = int( 360.0 / step )

        have_prev = False
        
        for a in xrange(steps):
            angle = np.deg2rad(start + a*step)
            x2 = x0 + np.cos(angle)*r
            y2 = y0 + np.sin(angle)*r
            
            points.append( (x2,y2) )
            #~ if have_prev:
                #~ self.draw_line(x1,y1, x2,y2, color)

            x1 = x2
            y1 = y2
            have_prev = True
            
        if (start + (steps-1)*step) != end:
            angle = np.deg2rad(end)
            x2 = x0 + np.cos(angle)*r
            y2 = y0 + np.sin(angle)*r
            
            #~ self.draw_line(x1,y1, x2,y2, color)
            points.append( (x2,y2) )
            
        return points
        
    def __arc(self, center, radius, start, end, step = 10.0):
        """
        Draw an arc.
        """
        x0 = center[0]
        y0 = center[1]
        points = []
        r = radius
        angle = end - start
        if angle < 0:
            angle += 360
        
        steps = int(abs(angle / step))

        have_prev = False
        
        for a in xrange(steps):
            angle = np.deg2rad(start + a*step)
            x2 = x0 + np.cos(angle)*r
            y2 = y0 + np.sin(angle)*r
            
            #~ if have_prev:
                #~ self.draw_line(x1,y1, x2,y2, color)
            points.append( (x2,y2) )

            x1 = x2
            y1 = y2
            have_prev = True
            
        if (start + (steps-1)*step) != end:
            angle = np.deg2rad(end)
            x2 = x0 + np.cos(angle)*r
            y2 = y0 + np.sin(angle)*r
            
            #~ self.draw_line(x1,y1, x2,y2, color)
            points.append( (x2,y2) )
            
        return points
        
    def __rbasis(self, c, t, npts, x, h):
        """
        Generates rational B-spline basis functions for an open knot vector.
        :note: Source code converted from LibreCad (rs_spline.cpp)
        
        """
        nplusc = npts + c
        temp = np.zeros(nplusc)
        
        # calculate the first order nonrational basis functions n[i]
        for i in xrange(nplusc-1):
            if t >= x[i] and t < x[i+1]:
                temp[i] = 1

        # calculate the higher order nonrational basis functions
        for k in xrange(2,c+1):
            for i in xrange(nplusc-k):
                # if the lower order basis function is zero skip the calculation
                if temp[i] != 0:
                    temp[i] = ((t-x[i])*temp[i])/(x[i+k-1]-x[i])
                    
                # if the lower order basis function is zero skip the calculation
                if temp[i+1] != 0:
                    temp[i] += ((x[i+k]-t)*temp[i+1])/(x[i+k]-x[i+1])
                    
        # pick up last point
        if t >= x[nplusc-1]:
            temp[npts-1] = 1

        # calculate sum for denominator of rational basis functions
        sum = 0.0
        for i in xrange(npts):
            sum += temp[i]*h[i]

        r = np.zeros(npts)
        # form rational basis functions and put in r vector
        if sum != 0:
            for i in xrange(npts):
                r[i] = (temp[i]*h[i])/sum
        return r

    def __rbspline(self, npts, k, p1, b, knot):
        """
        Generates a rational B-spline curve using a uniform open knot vector.
        :note: Source code converted from LibreCad (rs_spline.cpp)
        
        :param npts: Number of control points
        :param k: Spline degree
        :param b: Control point list
        :param knot: knot list
        """
        p = []
        h = np.ones(npts+1)
        nplusc = npts + k

        # generate the open knot vector (we have one already)
        x = knot

        # calculate the points on the rational B-spline curve
        t = 0.0
        step = x[nplusc-1] / (p1-1)
            
        vp = np.zeros(shape=(p1,2))
            
        for i in xrange(p1):
            if x[nplusc-1] - t < 5e-6:
                t = x[nplusc-1]
            # generate the basis function for this value of t
            nbasis = self.__rbasis(k, t, npts, x, h)

            # generate a point on the curve
            for j in xrange(npts):
                x0 = b[j][0] * nbasis[j]
                y0 = b[j][1] * nbasis[j]
                vp[i] += ( x0, y0 )
                
            t += step
            
            p.append( vp[i] )
            
        return p
        
    def transform(self, sx = 1.0, sy = 1.0, ox = 0.0, oy = 0.0):
        self.max_x *= sx
        self.max_y *= sy
        self.min_x *= sx
        self.min_y *= sy
        
        for l in self.layers:
            for e in l.primitives:
                t = e['type']
                
                if 'points' in e:
                    points = []
                    for p in e['points']:
                        points.append( ( (ox + p[0])*sx, (oy + p[1])*sy) )
                    e['points'] = points
                
                if t == 'polyline' or t == 'spline':
                    pass
                    #~ points = []
                    #~ for p in e['points']:
                        #~ points.append( ( (ox + p[0])*sx, (oy + p[1])*sy) )
                    #~ e['points'] = points
                elif t == 'circle' or t == 'arc':
                    p = e['center']
                    e['center'] = ( (ox + p[0])*sx, (oy + p[1])*sy)
                    e['radius'] *= (sx+sy) / 2.0
                elif t == 'ellipse':
                    p = e['center']
                    e['center'] = ( (ox + p[0])*sx, (oy + p[1])*sy)
                    m = e['major_axis']
                    e['major_axis'] = ( m[0] * sx, m[1] * sy, 0.0)
                    # TODO scale other parameters
        
    def scale(self, sx = 1.0, sy = 1.0):
        self.transform(sx, sy)
        
    def width(self):
        return self.max_x - self.min_x
        
    def height(self):
        return self.max_y - self.min_y
        
    def scale_to(self, target_width = 0.0, target_height = 0.0):
        width = self.width()
        height = self.height()
        
        sx = 1.0
        sy = 1.0
        
        if target_width != 0.0:
            sx = target_width / width
            sy = sx
            
        if target_height != 0.0:
            sy = target_height / height
            sx = sy

        self.scale(sx, sy)
        

    def normalize(self, margin = 0.1):
        self.transform(1.0, 1.0, -self.min_x+margin, -self.min_y+margin)
        
        width = self.max_x - self.min_x
        height = self.max_y - self.min_y
        
        self.min_x = 0
        self.min_y = 0
        self.max_x = width
        self.max_y = height

    def load_from_dxf(self, filename):
        dxf = dxfgrabber.readfile(filename)
            
        layer_map = {}

        print "- Layers:"
        for l in dxf.layers:
            print "  ", l.name, l.color, l.linetype
            color = 255
            layer_map[l.name] = self.add_layer(l.name, color)

        #~ print "- Blocks:"
        #~ for b in dxf.blocks:
            #~ print b.name
            
        #~ print "- Objects:"
        for o in dxf.objects:
            print o

        #~ print "- Entries:"
        for e in dxf.entities:
            t = e.dxftype
            #~ print "== ", t
            if t == 'LWPOLYLINE' or t == 'POLYLINE':
                is_closed = False
                if e.is_closed:
                    is_closed = True
                self.add_polyline(e.points, is_closed, layer_map[e.layer])
                
            elif t == 'LINE':
                self.add_line(e.start, e.end, layer_map[e.layer])
                
            elif t == 'CIRCLE':
                self.add_circle(e.center, e.radius, layer_map[e.layer])
                
            elif t == 'ELLIPSE':
                self.add_ellipse(e.center, e.major_axis, e.ratio, np.rad2deg(e.start_param), np.rad2deg(e.end_param), layer_map[e.layer] )
                
            elif t == 'ARC':
                self.add_arc(e.center, e.radius, e.start_angle, e.end_angle, layer_map[e.layer])
                
            elif t == 'SPLINE':
                self.add_spline(e.control_points, e.knots, e.degree, layer_map[e.layer])

    #~ def optimize(self):
        #~ for l in self.layers:
            #~ for e in l.primitives:
