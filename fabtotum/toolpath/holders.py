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

from shapely.geometry import Point,LineString,Polygon,box
from shapely.ops import cascaded_union
from shapely import affinity

from shapely.ops import cascaded_union
from shapely.ops import linemerge
from shapely import speedups

from .toolpath import ToolpathContext

def cut_line(line, distance):
    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        return [LineString(line)]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                LineString(coords[:i+1]),
                LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:])]


class HoldersToolpath(ToolpathContext):

	def __init__(self):
		super(HoldersToolpath, self).__init__()
		self.min_len = 10
		self.holder_size = 2
	
	def set_holder_params(self, holder_size=2, min_len=10):
		self.min_len = min_len
		self.holder_size = holder_size
	
	def add_holders(self, ring, holder_size, min_len):
		x = ring.xy[0]
		y = ring.xy[1]
			
		X1 = x[0]
		Y1 = y[0]

		lines = []

		for i in range(1,len(x)):
			X2 = x[i]
			Y2 = y[i]
			
			l = LineString( [(X1,Y1),(X2,Y2)] )
			
			if l.length >= min_len:
				lp1 = (l.length/2.0) - (holder_size/2.0)
				lp2 = (l.length/2.0) + (holder_size/2.0)
				
				hp1 = l.interpolate(lp1)
				hp2 = l.interpolate(lp2)
				
				l1 = cut_line(l, lp1)
				l2 = cut_line(l, lp2)
				
				lines.append(l1[0])
				lines.append(l2[1])
			else:
				lines.append(l)
			
			X1=X2
			Y1=Y2

		ml = linemerge(lines)
		
		lines = []
		
		if ml.geom_type == 'MultiLineString':
			for ls in ml:
				lines.append(ls)
		else:
			lines.append(ml)
		
		return lines

	def generate_paths(self, shapes, tool_d):
		tool_r = tool_d / 2.0
		toolpath = []
		for shp in shapes:
			toolpath.append( shp.buffer(tool_r) )

		result = cascaded_union(toolpath)
		
		if result.geom_type == 'Polygon':
			opt_obj = result.simplify(tolerance=0.01, preserve_topology=False)
			result = self.add_holders(opt_obj.exterior, self.holder_size + tool_d, self.min_len)
			if type(result) == list:
				return result
			else:
				return [result]
			
		elif result.geom_type == 'MultiPolygon':
			tmp = []
			for f in result:
				opt_obj = f.simplify(tolerance=0.01, preserve_topology=False)
				result = self.add_holders(opt_obj.exterior, self.holder_size + tool_d, self.min_len)
				if type(result) == list:
					for item in result:
						tmp.append(item)
				else:
					tmp.append( result )
			return tmp
