#!/usr/bin/env python2

from fabtotum.loaders import gerber
from fabtotum.loaders.gerber.render import *
from fabtotum.toolpath import *
from fabtotum.gcode import *
from fabtotum.common import *
import fabtotum.loaders.librecadfont1 as lff

import numpy as np

import os,sys
import argparse
import json

from shapely.geometry import Point,LineString,Polygon,box
#from shapely.geometry import LinearRing,MultiPolygon
#from shapely.geometry.polygon import orient
from shapely.ops import cascaded_union
from shapely.ops import linemerge
from shapely import affinity
from shapely import speedups

if speedups.available:
    speedups.enable()

#~ pcb = gerber.PCB.from_directory('../common/pcb_1/', verbose=True)
#~ dxf = dxfgrabber.readfile('../common/dxf/dxf_default.dxf')
#~ font = lff.readfile('/usr/share/librecad/fonts/iso.lff')
drawing = Drawing2D()
#~ drawing.add_layer('Default')
#~ drawing.add_text( (0,0), Drawing2D.TOP_LEFT, 9, (0,0,0), 'iso', "Q" )

#~ drawing.load_from_dxf('../common/dxf/dxf_default.dxf')
#~ drawing.load_from_dxf('/mnt/projects/external/FABTotum/img2gcode/dxf_sample_laser.dxf')
#~ drawing.load_from_dxf('/mnt/projects/external/FABTotum/gcode-utils/examples/mtext_fonts.dxf')
#~ drawing.load_from_dxf('/mnt/projects/external/FABTotum/gcode-utils/examples/mtext_45deg.dxf')
drawing.load_from_dxf('/mnt/projects/external/FABTotum/gcode-utils/examples/mtext_center.dxf')
drawing.normalize()

def __sort_elements(elements, sort_list = [], reverse_list = [], use_reverse = False):
    
    if len(elements) == 0:
        return [], []
    
    if len(sort_list) == 0:
        cur_x = 0.0
        cur_y = 0.0
    else:
        last = sort_list[-1]
        if last in reverse_list:
            p0 = elements[last]['points'][0]
        else:
            p0 = elements[last]['points'][-1]
        cur_x = p0[0]
        cur_y = p0[1]
    
    closest = None
    reverse = None
    dist = 1e20
    
    for i in xrange( len(elements) ):
        #~ print elements[i]
        if i not in sort_list:
            e = elements[i]
            p0 = e['points'][0]
            dx = p0[0] - cur_x
            dy = p0[1] - cur_y
            d0 = np.sqrt(dx*dx + dy*dy)
            
            d1 = d0
            if use_reverse:
                p0 = e['points'][-1]
                dx = p0[0] - cur_x
                dy = p0[1] - cur_y
                d1 = np.sqrt(dx*dx + dy*dy)

            if d0 < dist:
                dist = d0
                closest = i
            elif d1 < dist and use_reverse:
                dist = d1
                closest = i
                reverse = i

    if reverse is not None:
        reverse_list.append(reverse)

    if closest is None:
        return sort_list, reverse_list
    else:
        #~ print "added" , closest
        sort_list.append(closest)
        
    if len(sort_list) == len(elements):
        return sort_list, reverse_list
    else:
        return __sort_elements(elements, sort_list, reverse_list)

class GCodeOutput(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.fd = open(filename, 'w')
    
    def write(self, v):
        self.fd.write(v + '\r\n')
        
    def finish(self):
        self.fd.close()

out = GCodeOutput('output.gcode')
cnc = Milling(out)

cnc.zeroAll()
cnc.setAbsolute()
cnc.spindleON()

elements = drawing.layers[0].primitives
idx_list, rev_list = __sort_elements(drawing.layers[0].primitives, use_reverse=True)
#~ idx_list = range(len(elements))
#~ rev_list = []

#for p in drawing.layers[0].primitives:
for i in idx_list:
    p = elements[i]
    #print p['type']
    if 'points' in p:
        cnc.millPolyline( p['points'], i in rev_list )


cnc.spindleOFF()

out.finish()


os.system('LC_NUMERIC=C camotics output.gcode')
