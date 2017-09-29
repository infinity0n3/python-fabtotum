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

from shapely.geometry import Point,LineString,Polygon,MultiPolygon,box
from shapely.ops import cascaded_union
from shapely.ops import linemerge
from shapely import affinity
from shapely import speedups
from shapely.prepared import prep

from pprint import pprint

import os

#import numpy as np

if speedups.available:
    speedups.enable()

def project_point_to_object(point, geometry):
    """Find nearest point in geometry, measured from given point.
    
    Args:
        point: a shapely Point
        geometry: a shapely geometry object (LineString, Polygon)
        
    Returns:
        a shapely Point that lies on geometry closest to point
    """
    from sys import maxint
    nearest_point = None
    min_dist = maxint
    
    if isinstance(geometry, Polygon):
        for seg_start, seg_end in pairs(list(geometry.exterior.coords)):
            line_start = Point(seg_start)
            line_end = Point(seg_end)
        
            intersection_point = project_point_to_line(point, line_start, line_end)
            cur_dist =  point.distance(intersection_point)
        
            if cur_dist < min_dist:
                min_dist = cur_dist
                nearest_point = intersection_point
    
    elif isinstance(geometry, LineString):
        for seg_start, seg_end in pairs(list(geometry.coords)):
            line_start = Point(seg_start)
            line_end = Point(seg_end)
        
            intersection_point = project_point_to_line(point, line_start, line_end)
            cur_dist =  point.distance(intersection_point)
        
            if cur_dist < min_dist:
                min_dist = cur_dist
                nearest_point = intersection_point
    else:
        raise NotImplementedError("project_point_to_object not implemented for"+
                                  " geometry type '" + geometry.type + "'.")
    return nearest_point

class ToolpathContext(object):
    """ Gerber rendering context base class

    Provides basic functionality and API for generating toolpath.

    Attributes
    ----------

    drill_color : tuple (<float>, <float>, <float>)
        Color used for rendering drill hits. Format is the same as for `color`.
    """

    class DistanceMap(object):
        def __init__(self, size):
            self.size = size
            self.table = []
            for i in range(0,size-1):
                ti = [0] * (size-i-1)
                self.table.append(ti)
            
        def get_distance(self, a, b):
            i1 = min(a,b)
            i2 = max(a,b)-1
            if a == b:
                return 1e6
            return self.table[i1][i2-i1]
            
        def set_distance(self, a, b, d):
            i1 = min(a,b)
            i2 = max(a,b)-1
            self.table[i1][i2-i1] = d

        def get_closest(self, a):
            dmin = 1e5
            idx = None
            for i in range(0, self.size):
                d = self.get_distance(a,i)
                if d < dmin:
                    dmin = d
                    idx = i
                    
            return idx,dmin
            
        def clear(self, a):
            for i in range(0, self.size):
                self.set_distance(a,i, 1e6)

    class Path(object):
        def __init__(self, lines):
            self.lines = lines
            self.active = True
            self.distance_to = []
            self.index = 0
            
        def distance(self, path_object):
            return self.lines.distance(path_object.lines)
            
        def buffer(self, *k):
            return self.lines.buffer(*k)

    def __init__(self):
        self._tool_list = []
        self.settings = {'connect' : False}
        
    def add_tool(self, tool_d):
        self._tool_list.append(tool_d)

    def generate_paths(self, shapes, tool_d):
        """
        @shapes Shapely shapes describing the path to be cut
        @tool_d Tool diameter 
        Toolpath generation function.
        """
        raise NotImplementedError('"generate_paths" function must be implemented')
    
    def connect_paths(self, paths, shapes, tool_d):
        tmp = paths[:]
        conn = []
        
        tool_r = tool_d / 2.0
        
        dm = ToolpathContext.DistanceMap(len(paths))
        
        l = len(paths)
        for i in range(0,l):
            p1 = paths[i]
            #marge.append( Polygon(p1) )
            # a big number so that the search skipes this one
            for j in range(i+1, l):
                p2 = paths[j]
                d = p1.distance(p2)
                dm.set_distance(i,j,d)
        
        print(dm.table)
        
        
        cnt = l
        idx0 = 0
        marge = []
        while cnt > 1:
            idx1,d = dm.get_closest(idx0)
            dm.clear(idx0)

            # Create connection polygon            
            t1 = paths[idx0]
            t2 = paths[idx1]
            
            # Find intersections
            d2 = (d / 2.0)
            p1 = t1.buffer(d2)
            p2 = t2.buffer(d2)
            it = p1.intersection(p2)
                        
            if it.geom_type == 'MultiLineString':
                x = list(it)
            else:
                x = [it]

            for i in x:
                if i.geom_type == 'LineString':
                    if i.length >= tool_d*2:
                        l1 = i.parallel_offset(d2, side='right')
                        l2 = i.parallel_offset(d2, side='left')
                        mp1 = l1.interpolate(l1.length/2)
                        mp2 = l2.interpolate(l2.length/2)
                        p3 = Polygon( LineString([mp1,mp2]).buffer(tool_r,cap_style=3) )
                        marge.append(p3)
                        conn.append( p3.exterior )
                        break
            
            marge.append( Polygon(paths[idx0]) )
            marge.append( Polygon(paths[idx1]) )
            p4 = cascaded_union(marge)
            
            marge = [p4]
            
            #~ if cnt == 4:
                #~ break
            
            #print(p4)
            #conn.append( p4.exterior )
                    
            #return conn
            #conn.append(p4.exterior)  
            
            cnt = cnt - 1
            idx0 = idx1
        
        #p4 = cascaded_union(marge)
        #conn.append( marge[0].exterior)
        #print(marge)
        
        #conn.append()
        #~ p4 = cascaded_union(marge)
        #~ for g in marge[0].geoms:
            #~ print(g)
            #~ if g.geom_type == 'Polygon':
                #~ conn.append( g.exterior )
            #~ else:
                #~ conn.append( g )
        
        #~ while True:
            #~ idx1 = idx_list[0]
            #~ idx2 = None
            #~ t1 = tmp[idx1]
            #~ t2 = None
            #~ dmin = 1e6
            #~ #tmp.remove(t1)
            #~ idx_list.remove(idx1)
        #~ 
            #~ for tt_idx in idx_list:
                #~ #d = tt.distance(t1)
                #~ d = dm.get_distance(idx1, tt_idx)
                #~ if d < dmin:
                    #~ t2 = tmp[tt_idx]
                    #~ idx2 = tt_idx
                    #~ dmin = d
                #~ 
            #~ if t2:
                #~ #tmp.remove(t2)
                #~ idx_list.remove(idx2)
                #~ #self.find_closest_point(t1,t2,dmin)
                #~ d2 = (dmin / 2.0)
                #~ p1 = t1.buffer(d2)
                #~ p2 = t2.buffer(d2)
                #~ 
                #~ it = p1.intersection(p2)
                #~ 
                #~ p1 = Polygon(t1)
                #~ p2 = Polygon(t2)
                #~ marge = [p1, p2]
                #~ 
                #~ if it.geom_type == 'MultiLineString':
                    #~ x = list(it)
                #~ else:
                    #~ x = [it]
                #~ 
                #~ for i in x:
                    #~ if i.geom_type == 'LineString':
                        #~ if i.length >= tool_d*2:
                            #~ l1 = i.parallel_offset(d2, side='right')
                            #~ l2 = i.parallel_offset(d2, side='left')
                            #~ mp1 = l1.interpolate(l1.length/2)
                            #~ mp2 = l2.interpolate(l2.length/2)
                            #~ p3 = Polygon( LineString([mp1,mp2]).buffer(tool_r,cap_style=3) )
                            #~ marge.append(p3)
                            #~ break
                            #~ 
                #~ p4 = cascaded_union(marge)
                #~ tmp.append( p4.exterior )
            #~ else:
                #~ conn.append( t1.exterior )
                #~ 
            #~ if len(idx_list) == 1:
                #~ conn.append( tmp[idx1] )
                #~ break
            #~ print('paths', len(idx_list) )
                
        return conn

    def optimize(self, paths):
        return paths

    def generate(self, shapes):
        """
        Generate toolpahs based on shapes input.
        """
        print("Generating paths")
        # Select the first tool
        tool_d = self._tool_list[0]
        
        paths = self.generate_paths(shapes, tool_d)
        
        paths = self.optimize(paths)
        
        if self.settings['connect']:
            print("Connecting paths")
            # Future use for complete material removal toolpaths
            conn = self.connect_paths(paths, shapes, tool_d)
        else:
            conn = paths
        
        return conn
        
