#!/bin/env python
from matplotlib import pyplot

from fabtotum import gerber
from fabtotum.gerber.render import *
from fabtotum.toolpath import *
from fabtotum.gcode import *

from shapely.geometry import Point

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

config = {

}

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

pcb = gerber.PCB.from_directory('../common/pcb_1', verbose=False)

origin = (70,23)
bounds = (pcb.board_bounds[0][1],pcb.board_bounds[1][1])
plot_rect(ax, origin[0], origin[1], bounds[0], bounds[1], color=GRAY)

# mirror_x
origin_mirror_x = (2* marker_mid[0] - origin[0], origin[1])
plot_rect(ax, origin_mirror_x[0], origin_mirror_x[1], bounds[0], bounds[1], color=GRAY, mirror_x=1)

# Drill holes
for d in pcb.drill_layers[0].primitives:
    p = d.position
    
    
    p = (p[0] + origin[0], p[1] + origin[1])
    
    pt = Point(p).buffer(d.radius, cap_style=1, join_style=1)
    line = pt.exterior
    plot_line(ax, line, color=BLUE)

shapes = {}

for layer in pcb.layers:
    shp = ShapelyContext()
    layer.cam_source.render( shp )
    shapes[layer.layer_class] = shp
    
    if layer.layer_class == 'bottom':
        shp.mirror_x()
    elif layer.layer_class == 'outline':
		shp.set_ignore_width(True)
        #~ shp.translete(origin_mirror_x[0], origin_mirror_x[1])
    #~ else:
        #~ shp.translete(origin[0], origin[1])
    #~ print "origin",layer.layer_class,shp.origin    
    
    for f in shp.figs:
        line = f.exterior
        plot_line(ax, line)

#pyplot.show() 

#######################################

class Output(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.fd = open(filename, 'w')
    
    def write(self, v):
        self.fd.write(v + '\r\n')

# Prepare copper layer milling
for layer in pcb.copper_layers:
    out = Output('output/'+layer.layer_class+'.gcode')

    toolpath = IsolationToolpath()
    toolpath.add_tool(0.4)
    paths = toolpath.generate(shapes[layer.layer_class].figs)

    cnc = MillingPCB(out)

    # Start code
    cnc.setTravelSpeed(XY=5000, Z=1000)
    cnc.setMillingSpeed(150)
    cnc.setDrillSpeed(80)
    cnc.setTravelDistance(2)
    cnc.setPlungeDepth(0.35)
    cnc.setSpindleSpeed(15000)

    cnc.zeroZtoTool()
    
    cnc.setRelative()
    cnc.spindleON()

    # Milling code
    if paths:
        i = 1
        for tlp in paths:
            cnc.addComment('Path #' + str(i) )
            i += 1
            cnc.millPath(tlp)

    # End code
    cnc.stopMilling()
    cnc.spindleOFF()

# Prepare drilling
for layer in pcb.drill_layers:
    for drill in layer.drills:
        out = Output('output/'+layer.layer_class+'_'+str(drill)+'.gcode')
        
        cnc = MillingPCB(out)

        # Start code
        cnc.setTravelSpeed(XY=5000, Z=1000)
        cnc.setMillingSpeed(150)
        cnc.setDrillSpeed(50)
        cnc.setTravelDistance(2)
        cnc.setPlungeDepth(2)
        cnc.setSpindleSpeed(15000)

        cnc.zeroZtoTool()
        
        cnc.setRelative()
        cnc.spindleON()
        
        # Drilling
        cnc.addComment('Drill ' + str(drill) + 'mm' )
        for hole in layer.primitives:
            if hole.diameter == drill:
                p = hole.position
                cnc.drillAt(X=p[0], Y=p[1])
        
        # End code
        cnc.stopMilling()
        cnc.spindleOFF()

# Prepare cutting
for layer in pcb.outline_layers:
	out = Output('output/'+layer.layer_class+'.gcode')

	toolpath = IsolationToolpath()
	toolpath.add_tool(2)
	paths = toolpath.generate(shapes[layer.layer_class].figs)
	
	cnc = MillingPCB(out)

	# Start code
	cnc.setTravelSpeed(XY=5000, Z=1000)
	cnc.setMillingSpeed(150)
	cnc.setDrillSpeed(50)
	cnc.setTravelDistance(2)
	cnc.setDrillDepth(2)
	cnc.setSpindleSpeed(15000)

	cnc.zeroZtoTool()
	
	cnc.setRelative()
	cnc.spindleON()
	
	# Cutting
	cnc.addComment('Cutting')
	if paths:
		i = 1
		for tlp in paths:
			cnc.addComment('Path #' + str(i) )
			i += 1
			cnc.cutPath(tlp)
	
	# End code
	cnc.stopMilling()
	cnc.spindleOFF()

for layer in pcb.layers:
	print layer.layer_class
