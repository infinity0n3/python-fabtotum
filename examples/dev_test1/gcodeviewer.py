#!/bin/env python
from matplotlib import pyplot

from fabtotum import gerber
from fabtotum.gerber.render import *
from fabtotum.toolpath import *
from fabtotum.gcode import *

from shapely.geometry import Point,LineString,Polygon,box
#from shapely.geometry import LinearRing,MultiPolygon
#from shapely.geometry.polygon import orient
from shapely.ops import cascaded_union
from shapely.ops import linemerge
from shapely import affinity

front = gerber.read('manufacturing/getting_used_to-B.Cu.gbl')
edges = gerber.read('manufacturing/getting_used_to-Edge.Cuts.gm1')
#front = gerber.read('milling_test1/milling_test1-B.Cu.gbl')
shapes_f = ShapelyContext()
shapes_e = ShapelyContext()

front.render(shapes_f)
edges.render(shapes_e)

print "shapes_f.origin:",shapes_f.origin
print "shapes_e.origin:",shapes_e.origin

#shapes_f.translete(-shapes_e.origin[0], -shapes_e.origin[1])
#shapes_e.translete(-shapes_e.origin[0], -shapes_e.origin[1])

tp = IsolationToolpath()
tp.add_tool(0.4)
tpr = tp.generate(shapes_f.figs)

#~ 
	#~ pyplot.xlabel(unit)
	#~ pyplot.ylabel(unit)
	#~ pyplot.show()

BLUE = '#6699cc'
RED =  '#ff0000'
GREEN =  '#00cc00'
GRAY = '#999999'

colors = ['#ff0000','#00cc00', '#0000cc', '#cccc00', '#cc00cc', '#00cccc']

def plot_rect(ax, x,y,w,h, color=GRAY, width=0.5):
    x = [x,x+w,x+w,x,x]
    y = [y,y,y+h,y+h,y]
    ax.plot(x, y, color=color, linewidth=width, solid_capstyle='round', zorder=1)

def plot_line(ax, ob, color=GRAY, width=0.5):
    x, y = ob.xy
    ax.plot(x, y, color=color, linewidth=width, solid_capstyle='round', zorder=1)

def plot_line_xy(ax, x, y, color=GRAY, width=0.5):
    ax.plot(x, y, color=color, linewidth=width, solid_capstyle='round', zorder=1)

def plot_coords(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, 'o', color='#999999', zorder=1)

#line = LineString([(0, 0), (1, 1), (0, 2), (2, 2), (3, 1), (1, 0)])
#~ line = LineString([(0, 0), (0, 1), (1, 2), (2, 2), (6, 2)])

#ax.add_patch(patch1)
#~ 
#~ c1 = Point(6,2).buffer(1,resolution=45)
#~ patch1 = PolygonPatch(c1, fc=BLUE, ec=BLUE, alpha=0.5, zorder=2)
#~ ax.add_patch(patch1)

fig = pyplot.figure(1, figsize=(8,8), dpi=90)
ax = fig.add_subplot(111)

#~ for f in shapes.figs:
    #~ line = f.exterior
    #~ plot_line(ax, line)
#~ 
#~ if tpr:
    #~ for tlp in tpr:
        #~ plot_line(ax, tlp, color=RED)
        #~ plot_coords(ax, tlp)
        #~ #object.simplify(tolerance, preserve_topology=True)
        #~ smpl = tlp.simplify(tolerance=0.01, preserve_topology=True)
        #~ plot_line(ax, smpl, color=GREEN)
        #~ 
        #~ #plot_coords(ax, smpl)
        #~ #x = tlp.xy[0]
        #~ #y = tlp.xy[1]
        #~ #plot_line_xy(ax, x, y, color=GREEN)

#~ xrange = [shapes.bounds[1][0],shapes.bounds[0][0]]
#~ yrange = [shapes.bounds[1][1],shapes.bounds[0][1]]

#~ print shapes_f.bounds[1][0], shapes_f.bounds[0][0]
#~ print shapes_f.bounds[1][1], shapes_f.bounds[0][1]

xrange = [-5,240]
yrange = [-5,240]

ax.set_xlim(*xrange)
#ax.set_xticks(range(*xrange) + [xrange[-1]])
ax.set_ylim(*yrange)
#ax.set_yticks(range(*yrange) + [yrange[-1]])

ax.set_aspect(1)


class Output(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.fd = open(filename, 'w')
    
    def write(self, v):
        self.fd.write(v + '\r\n')

out = Output('output.gcode')
cnc = MillingPCB(out)

cnc.setTravelSpeed(XY=5000, Z=1000)
cnc.setMillingSpeed(150)
cnc.setDrillSpeed(80)
cnc.setTravelDistance(2)
cnc.setPlungeDepth(0.35)
cnc.setSpindleSpeed(15000)

#cnc.zeroAll()
#cnc.zeroZ()
cnc.zeroZtoTool()

#cnc.setAbsolute()
#cnc.travelTo(70, 177)

cnc.setRelative()
cnc.spindleON()

#cnc.millRect(0, 0, 3, 3)

plot_rect(ax, 0, 0, shapes_f.size[0],shapes_f.size[1], color=BLUE)
plot_rect(ax, 0, 0, shapes_e.size[0],shapes_e.size[1], color=BLUE)

print shapes_e.size

if tpr:
    i = 1
    for tlp in tpr:
        cnc.addComment('Path #' + str(i) )
        i += 1
        cnc.millPath(tlp)
        plot_line(ax, tlp, color=GREEN)
        break

#~ for f in shapes_f.figs:
    #~ line = f.exterior
    #~ plot_line(ax, line, color=RED)

cnc.stopMilling()
cnc.spindleOFF()

pyplot.show()
