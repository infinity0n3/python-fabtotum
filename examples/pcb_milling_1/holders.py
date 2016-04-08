#!/bin/env python
from matplotlib import pyplot

from fabtotum import gerber
from fabtotum.gerber.render import *
from fabtotum.toolpath import *
from fabtotum.gcode import *

from shapely.geometry import Point, Polygon, LineString
from shapely.ops import linemerge

from shapely import speedups
if speedups.available:
	speedups.enable()

BLUE = '#6699cc'
RED =  '#ff0000'
GREEN =  '#00cc00'
GRAY = '#999999'

colors = ['#ff0000','#00cc00', '#0000cc', '#cccc00', '#cc00cc', '#00cccc']

def plot_rect(ax, x,y,w,h, color=GRAY, width=0.5, mirror_x=0):
    if mirror_x:
        x = [x,x-w,x-w,x,x]
        y = [y,y,y+h,y+h,y]
    else:
        x = [x,x+w,x+w,x,x]
        y = [y,y,y+h,y+h,y]
    ax.plot(x, y, color=color, linewidth=width, solid_capstyle='round', zorder=1)

def plot_points(ax, pts, color=GRAY, style='o'):
    x = []
    y = []
    for p in pts:
        x.append( p[0] )
        y.append( p[1] )
    ax.plot(x, y, style, color=color, zorder=1)
    
def plot_line(ax, ob, color=GRAY, width=0.5):
    x, y = ob.xy
    ax.plot(x, y, color=color, linewidth=width, solid_capstyle='round', zorder=1)

def plot_line_xy(ax, x, y, color=GRAY, width=0.5):
    ax.plot(x, y, color=color, linewidth=width, solid_capstyle='round', zorder=1)

def plot_coords(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, 'o', color='#999999', zorder=1)
    
########################################################################

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

#~ front = gerber.read('milling/router_board_v1-F.Cu.gtl')
#~ back  = gerber.read('milling/router_board_v1-Edge.Cuts.gm1')
#~ edge  = gerber.read('milling/router_board_v1-B.Cu.gbl')
#~ drill = gerber.read('milling/router_board_v1.drl')

# 2----3
# |    |
# |    |
# 1----4
# (x,y), (1,2,3,4)

markers = ( (70,23),    #1
            (70,177),   #2
            (164,177),  #3
            (164,23) )  #4

marker_mid = ( (markers[0][0] + markers[2][0])/2.0, 
               (markers[0][1] + markers[1][1])/2.0)

fig = pyplot.figure(1, figsize=(8,8), dpi=90)
ax = fig.add_subplot(111)

bed_bounds = (214,234)

#~ xrange = [-5,bed_bounds[0]+5]
xrange = [-5,bed_bounds[0]+5]
yrange = [-5,bed_bounds[1]+5]

ax.set_xlim(*xrange)
ax.set_ylim(*yrange)
ax.set_aspect(1)

plot_rect(ax, 0, 0, bed_bounds[0], bed_bounds[1], color=GRAY)
plot_rect(ax, markers[0][0]-3, markers[0][1]-3, 100, 160, color=GRAY)
plot_line_xy(ax, (marker_mid[0],marker_mid[0]), (bed_bounds[1],0), color=RED )
plot_points(ax, markers, color=RED, style='+')

########################################################################

pcb = gerber.PCB.from_directory('./milling', verbose=False)

origin = (70,23)
bounds = (pcb.board_bounds[0][1],pcb.board_bounds[1][1])
#plot_rect(ax, origin[0], origin[1], bounds[0], bounds[1], color=GRAY)

# mirror_x
origin_mirror_x = (2* marker_mid[0] - origin[0], origin[1])
#plot_rect(ax, origin_mirror_x[0], origin_mirror_x[1], bounds[0], bounds[1], color=GRAY, mirror_x=1)

#~ shapes = {}
#~ 
#~ for layer in pcb.layers:
    #~ shp = ShapelyContext()
    #~ layer.cam_source.render( shp )
    #~ shapes[layer.layer_class] = shp
    #~ 
    #~ if layer.layer_class == 'bottom':
        #~ shp.mirror_x()
        #~ shp.translete(origin_mirror_x[0], origin_mirror_x[1])
    #~ else:
        #~ shp.translete(origin[0], origin[1])
    #~ print "origin",layer.layer_class,shp.origin    
    #~ 
    #~ for f in shp.figs:
        #~ line = f.exterior
        #~ plot_line(ax, line)

shape = ShapelyContext(ignore_width=True)
pcb.outline_layers[0].cam_source.render( shape )

for shp in shape.figs:
	plot_line(ax, shp, color=BLUE)

toolpath = IsolationToolpath()
toolpath.add_tool(2)
paths = toolpath.generate(shape.figs)

for tpl in paths:
	print type(tpl)
	plot_line(ax, tpl, color=GREEN, width=10)

toolpath = HoldersToolpath(holder_size=2, min_len=10)
toolpath.add_tool(2)
paths = toolpath.generate(shape.figs)

for tpl in paths:
	print type(tpl)
	#plot_line(ax, tpl, color=RED)
	
	brd = LineString(tpl)
	b = brd.buffer(2/2, cap_style=1, join_style=1, resolution=8)
	plot_line(ax, b.exterior, color=BLUE)

#~ obj1 = shape.figs[0]
#~ obj = obj1
#~ 
#~ plot_line(ax, obj, color=RED)
#~ 
#~ opt_obj = obj.simplify(tolerance=0.01, preserve_topology=False)
#~ 
#~ print opt_obj.xy
#~ 
#~ plot_line(ax, obj, color=GREEN)
#~ 
#~ min_len = 10
#~ holder_length = 3
#~ 
#~ x = opt_obj.xy[0]
#~ y = opt_obj.xy[1]
#~ X1 = x[0]
#~ Y1 = y[0]
#~ 
#~ lines = []
#~ 
#~ for i in range(1,len(x)):
	#~ X2 = x[i]
	#~ Y2 = y[i]
	#~ 
	#~ l = LineString( [(X1,Y1),(X2,Y2)] )
	#~ 
	#~ if l.length >= min_len:
		#~ lp1 = (l.length/2.0) - (holder_length/2.0)
		#~ lp2 = (l.length/2.0) + (holder_length/2.0)
		#~ 
		#~ hp1 = l.interpolate(lp1)
		#~ hp2 = l.interpolate(lp2)
		#~ 
		#~ plot_points(ax, [ (hp1.x, hp1.y), (hp2.x, hp2.y) ], color=RED, style='x')
		#~ 
		#~ l1 = cut_line(l, lp1)
		#~ l2 = cut_line(l, lp2)
		#~ 
		#~ plot_line(ax, l1[0], color=RED, width=2)
		#~ plot_line(ax, l2[1], color=RED, width=2)
		#~ 
		#~ lines.append(l1[0])
		#~ lines.append(l2[1])
	#~ else:
		#~ lines.append(l)
	#~ 
	#~ X1=X2
	#~ Y1=Y2
#~ 
#~ ml = linemerge(lines)
#~ 
#~ print len(ml)


pyplot.show()

#######################################
