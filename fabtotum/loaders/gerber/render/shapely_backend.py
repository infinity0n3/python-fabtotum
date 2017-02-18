#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Daniel Kesler <kesler.daniel@gmail.com>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#~ from shapely.geometry import Point,LineString,box
import shapely.geometry as sg
#~ from shapely.geometry.polygon import LinearRing
#from shapely.geometry import LinearRing,MultiPolygon
#from shapely.geometry.polygon import orient
from shapely.ops import cascaded_union
from shapely.ops import linemerge
from shapely import affinity
from shapely import speedups

if speedups.available:
    speedups.enable()

import copy
import json
import numpy as np

from .render import GerberContext, RenderSettings
from .theme import THEMES
from ..primitives import *

try:
    from cStringIO import StringIO
except(ImportError):
    from io import StringIO


class ShapelyContext(GerberContext):

    def __init__(self, ignore_width = False):
        super(ShapelyContext, self).__init__()
        self.figs = []
        self.cut_figs = []
        self.bounds = ((0,0), (0,0))
        self.origin = (0,0)
        self.size = (0,0)
        self.ignore_width = ignore_width

    def set_ignore_width(self, ignore_width):
        self.ignore_width = ignore_width

    def set_bounds(self, bounds, new_surface=False):
        origin_in_inch = (bounds[0][0], bounds[1][0])
        size_in_inch = (abs(bounds[0][1] - bounds[0][0]),
                        abs(bounds[1][1] - bounds[1][0]))                        
        self.bounds = bounds
        self.origin = origin_in_inch
        self.size = size_in_inch
    
    def translete(self, xoff, yoff):
        ofigs = []
        for f in self.figs:
            tmp = affinity.translate(f, xoff=xoff, yoff=yoff)
            ofigs.append(tmp)
        self.figs = ofigs

    def mirror_x(self, x = 0):
        ofigs = []
        center=(x,0,0)
        for f in self.figs:
            tmp = affinity.scale(f, xfact=-1, yfact=1,origin=center)
            ofigs.append(tmp)
        self.figs = ofigs

    def _render_line(self, line, color):
        #print("TODO: render line")
        if isinstance(line.aperture, Circle):
            width = line.aperture.diameter / 2.0
                            
            if self.ignore_width:
                self.figs.append( sg.LineString([line.start,line.end]) )
            else:
                if width < 0.1:
                    return
                self.figs.append( sg.LineString([line.start,line.end]).buffer(width, cap_style=1, join_style=1, resolution=8) )
        elif isinstance(line.aperture, Rectangle):
            print("TODO: render line [aperture=rect]")
            #~ points = [self.scale_point(x) for x in line.vertices]
            #~ self.ctx.set_line_width(0)
            #~ self.ctx.move_to(*points[0])
            #~ for point in points[1:]:
                #~ self.ctx.line_to(*point)
            #~ self.ctx.fill()
            
    def __wrapTo360(self, angle):
        angle = np.fmod(angle,360);
        if angle < 0:
            angle += 360;
        return angle;
            
    def _render_arc(self, arc, color):
        #~ print("TODO: render arc")
        center = arc.center
        start = arc.start
        end = arc.end
        radius =  arc.radius
        angle1 = np.rad2deg(arc.start_angle)
        angle2 = np.rad2deg(arc.end_angle)
        width = arc.aperture.diameter if arc.aperture.diameter != 0 else 0.001
        
        if angle1 > angle2:
            angle1 = self.__wrapTo360(angle1)
            angle2 = self.__wrapTo360(angle2)
        
        angle1 = np.deg2rad(angle1)
        angle2 = np.deg2rad(angle2)
        
        step = 0.1
        
        reverse = False
        
        #if angle1 > angle2:
        #    reverse = True
        
        sign = 1
        if reverse:
            tmp = angle1
            angle1 = angle2
            angle2 = tmp
            sign = -1
            
        angle = abs(angle1 - angle2)
        steps = int(abs(angle / step))
        
        x0 = center[0]
        y0 = center[1]
        
        points = []
    
        steps -= 2
    
        points.append( start )
    
        for a in xrange(steps):
            angle = angle1 + sign*(a+1)*step
            x2 = x0 + np.cos(angle)*radius
            y2 = y0 + np.sin(angle)*radius
            
            points.append( (x2,y2) )

            x1 = x2
            y1 = y2
            have_prev = True

        points.append( end )

        #~ print "arc", center, start, end, radius, angle1, angle2, arc.direction
        
        if self.ignore_width:
            self.figs.append( sg.LineString(points) )

    def _render_region(self, region, color):       
        points = []
        points.append( region.primitives[0].start )
        
        for prim in region.primitives:
            if isinstance(prim, Line):
                points.append( prim.end )
            else:
                center = prim.center
                radius = prim.radius
                angle1 = prim.start_angle
                angle2 = prim.end_angle
                if prim.direction == 'counterclockwise':
                    print "TODO: arc-ccw in regions"
                    print "arc (ccw)", center, radius, angle1, angle2
                else:
                    print "TODO: arc-cw in regions"
                    print "arc (cw)", center, radius, angle1, angle2

        tmp = []
        coords = []

        for pt in points:
            if pt in tmp:
                idx = tmp.index(pt)
                sub = tmp[idx:]

                if len(sub) > 2:
                    sub.append(sub[0])
                    coords.append(sub[:])
                
                last = tmp[idx]
                tmp = tmp[:idx]
            else:
                tmp.append(pt)

        tmp.append(last)
        tmp.append(tmp[0])
            
        poly = sg.Polygon(coords[-1], coords[:-1] )
        self.figs.append(poly)
        
    def _render_circle(self, circle, color):
        self.figs.append( sg.Point(circle.position).buffer(circle.radius, cap_style=1, join_style=1) )

    def _render_rectangle(self, rectangle, color):
        self.figs.append( sg.box(  rectangle.lower_left[0], 
                                rectangle.lower_left[1],
                                rectangle.lower_left[0]+rectangle.width,
                                rectangle.lower_left[1]+rectangle.height,
                             ) )

    def _render_obround(self, obround, color):
        c1 = obround.subshapes['circle1']
        c2 = obround.subshapes['circle2']
        # rect is calculate automatically
        self.figs.append( sg.LineString([c1.position, c2.position]).buffer(c1.radius, cap_style=1, join_style=1) )

    def _render_polygon(self, primitive, color):
        print("TODO: render poly")
        pass

    def _render_drill(self, primitive, color):
        #~ print("TODO: render drill")
        pass

    def _render_test_record(self, primitive, color):
        print("TODO: render test record")
        pass

    def _save_polygons(self):
        i = 0
        
        content = {
            'cuts': [],
            'polys': []
        }
        
        for cut_fig in self.cut_figs:
            j = 0
            
            xy = []
            for pt in cut_fig.exterior.coords:
                xy.append(pt)
            
            poly = { 'exterior': xy, 'interiors': [] }
            
            for i in cut_fig.interiors:
                xyi = []
                for pt in i.coords:
                    xyi.append(pt)
                    
                poly['interiors'].append(xyi)
                
            
            content['cuts'].append(poly)
            
        for fig in self.figs:
            xy = []
            for pt in fig.exterior.coords:
                xy.append(pt)
            poly = { 'exterior': xy, 'interiors': [] }
            
            for i in fig.interiors:
                xyi = []
                for pt in i.coords:
                    xyi.append(pt)
                    
                poly['interiors'].append(xyi)
            
            content['polys'].append(poly)
                   
        with open('output.json'.format(len(self.figs)), 'w') as f:
            f.write( json.dumps(content) )

    def _merge_polygons(self):
        merge = []
        lines_only = True
        for fig in self.figs:
            if fig.geom_type != 'LineString' and \
               fig.geom_type != 'MultiLineString':
               lines_only = False
            merge.append(fig)
            
        for fig in merge:
            self.figs.remove(fig)
            
        if lines_only and self.ignore_width:
            result = linemerge(merge)
        else:
            try:
                result = cascaded_union(merge)
            except Exception as e:
                print "ERROR:", e

        if result.geom_type == 'Polygon' or result.geom_type == 'LineString':
            self.figs.append( result )
        elif result.geom_type == 'MultiPolygon' or result.geom_type == 'MultiLineString':
            for f in result:
                self.figs.append(f)

    def _new_render_layer(self, color=None, mirror=False):
        #~ print("_new_render_layer")
        pass

    def _flatten(self):
        self._merge_polygons()
        #~ self._save_polygons()

    def _paint_background(self, force=False):
        #~ print("_paint_background")
        pass
