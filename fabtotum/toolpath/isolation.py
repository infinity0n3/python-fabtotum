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

from .toolpath import ToolpathContext

class IsolationToolpath(ToolpathContext):
    
    def __init__(self, use_exterior=True, use_interior=True):
        super(IsolationToolpath, self).__init__()
        self.use_exterior = use_exterior
        self.use_interior = use_interior

    def generate_paths(self, shapes, tool_d):
        tool_r = tool_d / 2.0
        toolpath = []
        for shp in shapes:
            toolpath.append( shp.buffer(tool_r) )

        result = cascaded_union(toolpath)
        
        tmp = []
        
        if result.geom_type == 'Polygon':
            if self.use_exterior:
                tmp = [result.exterior]
            
            if self.use_interior:
                for i in result.interiors:
                    poly = Polygon(i)
                    tmp.append( poly.exterior )
            
        elif result.geom_type == 'MultiPolygon':
            if self.use_exterior:
                for f in result:
                    tmp.append( f.exterior )

            if self.use_interior:
                for i in f.interiors:
                    poly = Polygon(i)
                    tmp.append( poly.exterior )
                
        return tmp
            
