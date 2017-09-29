#!/usr/bin/env python2

from fabtotum.loaders import gerber
from fabtotum.loaders.gerber.render import *
from fabtotum.toolpath import *
from fabtotum.gcode import *

import os,sys
import argparse
import json

import shapely.geometry as sg
from shapely import affinity


################################ DEBUG #########################################
try:
    from matplotlib import pyplot
    use_matplot = True
except:
    use_matplot = False

BLUE = '#6699cc'
RED =  '#ff0000'
GREEN =  '#00cc00'
GRAY = '#999999'

colors = ['#ff0000','#00cc00', '#0000cc', '#cccc00', '#cc00cc', '#00cccc']

def plot_line(ax, ob, color=GRAY, width=0.5):
    x, y = ob.xy
    ax.plot(x, y, color=color, linewidth=width, solid_capstyle='round', zorder=1)

def plot_line_xy(ax, x, y, color=GRAY, width=0.5):
    ax.plot(x, y, color=color, linewidth=width, solid_capstyle='round', zorder=1)

def plot_coords(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, 'o', color='#999999', zorder=1)
    
if use_matplot:
    fig = pyplot.figure(1, figsize=(8,8), dpi=90)
    ax = fig.add_subplot(111)
################################################################################

def load_config_from_file(filename):
    content = open(filename)
    config = json.loads( content.read() )
    content.close()
    return config
    
########################################################################

class GCodeOutput(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.fd = open(filename, 'w')
    
    def write(self, v):
        self.fd.write(v + '\r\n')

def main():
    parser = argparse.ArgumentParser(description='-=[[ PCB2GCODE ]]=-')
    parser.add_argument('--version', action='version', version="pcb2gcode 0.01")

    parser.add_argument('-i','--input', 
                        metavar='<directory>', 
                        dest='input', 
                        default='input',
                        type=str,
                        help='Directory containing gerber files')

    parser.add_argument('-o','--output',
                        metavar='<directory>', 
                        dest='output', 
                        default='output', 
                        type=str,
                        help='Place the generated gcode files into <directory>')

    parser.add_argument('-g','--generate',
                        dest='generate_config',
                        action='store_true',
                        help='Generate configuration file with default values.')

    parser.add_argument('-C', metavar='<file>', dest='config_file',
                        default="config.json",
                        help='Load configuration from file.')
                        
    parser.add_argument('-d', dest='debug',
                        action='store_true',
                        help='Show debug info.')
    
    app_args = parser.parse_args()

    config = {
        # Z tuning
        'travel-height'     : 2.0,     # Height used for travel moves
        'cut-depth'         : 1.65,     # Cutting depth
        'cut-step'          : 0.2,     # Cutting is done in steps if Z
        # V bit
        'plunge-depth'      : 0.25,
        'mill-bit-diameter' : 0.4,    # Milling tool diameter at plunge-depth
        # Endcut bit
        'cut-bit-diameter'  : 2.1,    # Cutting tool diameter
        # Milling speed
        'spindle-speed'     : 15000,    # Spindle speed (CW)
        'milling-xy-speed'  : 300,        # XY speed during milling moves
        'milling-xy-speed1'  : 150,        # XY speed during milling moves
        'cutting-xy-speed'  : 150,        # XY speed during cutting moves
        'drilling-z-speed'  : 50,        # Z speed during drilling moves
        'travel-xy-speed'   : 5000,        # XY speed during travel moves (at travel height)
        'travel-z-speed'    : 1000,        # Z speed for getting to travel height
        'milling-start-pause' : 1000,       # Pause after plunging the milling bit into the material
        'number-of-passes'  : 2,        # Number of milling passes for each conture
        # Probe
        'use-continuity-probe'    :    True,
        # Holders
        'use-holders'    : True,    # Skip cutting PCB at some places to keep it in place
        'holder-size'    : 2.0,     # Single holder size
        'holder-height'  : 0.8,     # Thickness of the holders
        'holder-min-length' : 5,   # Path must be at least this long to include a holder. Use this to avoid putting holders on short segments.
        # Array (TODO)
        # Rotation (TODO)
        'rotation'      : 0.0,      # Board rotation in degrees
        # Markers
        'markers' : [(70,23), (70,177), (164,177), (164,23)],
        # PCB
        'pcb-thickness' : 1.6,
        'flip-top-bottom' : False
    }

    # Generate default config file
    if app_args.generate_config:
        content = json.dumps(config, indent=4)
        fd = open('default.json', 'w')
        fd.write(content)
        sys.exit(0)

    config = load_config_from_file(app_args.config_file)
    
    #~ markers = config['markers']
    #~ marker_mid = ( (markers[0][0] + markers[2][0])/2.0, 
                   #~ (markers[0][1] + markers[1][1])/2.0)

    pcb = gerber.PCB.from_directory(app_args.input, verbose=True)

    layer_shape = {}
    
    # Convert gerber to shapely objects
    for layer in pcb.layers:
        shp = ShapelyContext()
        
        if layer.layer_class == 'outline':
            shp.set_ignore_width(True)
            
        layer.cam_source.render( shp )
        print layer
        if layer.mirrored:
            print "- mirroring"
            layer_shape[layer.layer_class+'_mirrored'] = shp
            shp.mirror_x()
        else:
            layer_shape[layer.layer_class] = shp
        
        
        
        if (layer.layer_class == 'bottom' and config['flip-top-bottom'] == False) or (layer.layer_class == 'top' and config['flip-top-bottom'] == True):
            shp.mirror_x()
                
        shp.rotate( float(config['rotation']) )
    
    #~ print "layers", layer_shape
    
    # Prepare copper layer milling
    idx=0
    for layer in pcb.copper_layers:
        if not os.path.exists(app_args.output):
            os.mkdir(app_args.output, 0755)
        
        out = GCodeOutput(app_args.output+'/'+layer.layer_class+'.gcode')
        toolpath = IsolationToolpath()
        toolpath.add_tool( config['mill-bit-diameter'] )
        paths = toolpath.generate(layer_shape[layer.layer_class].figs)

        cnc = MillingPCB(out)

        # Start code
        cnc.setTravelSpeed    ( XY= config['travel-xy-speed'], Z = config['travel-z-speed'])
        cnc.setMillingSpeed   ( config['milling-xy-speed'] )
        cnc.setDrillSpeed     ( config['drilling-z-speed'] )
        cnc.setTravelHeight ( config['travel-height'] )
        cnc.setPlungeDepth    ( config['plunge-depth'] )
        cnc.setSpindleSpeed   ( config['spindle-speed'] )
        cnc.setMillingStartPause ( config['milling-start-pause'] )

        if config['use-continuity-probe']:
            cnc.zeroZtoTool()
        
        cnc.zeroAll()
        cnc.setAbsolute()
        cnc.spindleON()

        np = config['number-of-passes']
        # Milling code
        if paths:
            i = 1
            for tlp in paths:
                cnc.addComment('Path #' + str(i) )
                i += 1
                is_first = True
                for p in xrange(np):
                    if is_first:
                        cnc.millPath(tlp, feedrate=config['milling-xy-speed1'])
                        is_first = False
                    else:
                        cnc.millPath(tlp)
                
                if use_matplot:
                    plot_line(ax, tlp, color=colors[idx])
                    #~ plot_coords(ax, tlp)

        # End code
        cnc.stopMilling()
        cnc.spindleOFF()
        
        idx += 1

    if use_matplot:
        #~ xrange = [shapes.bounds[1][0],shapes.bounds[0][0]]
        #~ yrange = [shapes.bounds[1][1],shapes.bounds[0][1]]
        #~ ax.set_xlim(*xrange)
        #~ ax.set_xticks(range(*xrange) + [xrange[-1]])
        #~ ax.set_ylim(*yrange)
        #~ ax.set_yticks(range(*yrange) + [yrange[-1]])
        pass
        #~ ax.set_aspect(1)
        #~ pyplot.show()

    # Prepare drilling
    for layer in pcb.drill_layers:
        for drill in layer.drills:
            suffix = ''
            if layer.mirrored in ['x', 'y']:
                out = GCodeOutput(app_args.output+'/'+layer.layer_class+'_'+str(drill)+'_bottom.gcode')
                suffix = '_mirrored'
            else:
                out = GCodeOutput(app_args.output+'/'+layer.layer_class+'_'+str(drill)+'.gcode')
            
            cnc = MillingPCB(out)

            # Start code
            cnc.setTravelSpeed    (    XY= config['travel-xy-speed'],
                                    Z = config['travel-z-speed'])
            cnc.setMillingSpeed        ( config['milling-xy-speed'] )
            cnc.setDrillSpeed        ( config['drilling-z-speed'] )
            cnc.setTravelHeight    ( config['travel-height'] )
            cnc.setPlungeDepth        ( config['plunge-depth'] )
            cnc.setSpindleSpeed        ( config['spindle-speed'] )

            if config['use-continuity-probe']:
                cnc.zeroZtoTool()
            
            cnc.zeroAll()
            cnc.setAbsolute()
            cnc.spindleON()
            
            # Drilling
            cnc.addComment('Drill ' + str(drill) + 'mm' )
            for hole in layer.primitives:
                if hole.diameter == drill:
                    p = sg.Point(hole.position)
                                        
                    if layer.mirrored == 'x':
                        center=(0,0,0)
                        p = affinity.scale(p, xfact=-1, yfact=1, origin=center)
                    elif layer.mirrored == 'y':
                        raise NotImplementedError("drill mirror-y not implemented")
                    p = affinity.rotate(p, config['rotation'], origin=(0,0))
                        
                    cnc.drillAt(X=p.x, Y=p.y)
            
            # End code
            cnc.stopMilling()
            cnc.spindleOFF()

    # Prepare cutting
    
    for layer in pcb.outline_layers:
        suffix = ''
        if layer.mirrored in ['x', 'y']:
            out = GCodeOutput(app_args.output+'/'+layer.layer_class+'_bottom.gcode')
            suffix = '_mirrored'
        else:
            out = GCodeOutput(app_args.output+'/'+layer.layer_class+'.gcode')
        
        layer_class = layer.layer_class+suffix
        
        figs = []
        
        for fig in layer_shape[layer_class].figs:
            figs.append( list(fig.coords) )
            
        with open('figs.json', 'w') as f:
            f.write( json.dumps(figs) )
        
        toolpath = IsolationToolpath(use_interior=False)
        toolpath.add_tool( config['cut-bit-diameter'] )
        paths = toolpath.generate(layer_shape[layer_class].figs)

        toolpath2 = HoldersToolpath()
        toolpath2.set_holder_params(holder_size = config['holder-size'],
                                     min_len = config['holder-min-length'] )
        toolpath2.add_tool( config['cut-bit-diameter'] )
        paths2 = toolpath2.generate(layer_shape[layer_class].figs)

        print "TOOLPATHS", len(paths2)

        cnc = MillingPCB(out)

        # Start code
        cnc.setTravelSpeed  (XY= config['travel-xy-speed'], Z = config['travel-z-speed'])
        cnc.setMillingSpeed ( config['cutting-xy-speed'] )
        cnc.setDrillSpeed   ( config['drilling-z-speed'] )
        cnc.setTravelHeight ( config['travel-height'] )
        cnc.setPlungeDepth  ( config['plunge-depth'] )
        cnc.setSpindleSpeed ( config['spindle-speed'] )
        
        cut_start_depth = 0
        #~ cut_end_depth = config['pcb-thickness'] + 0.1 #config['cut-depth']
        cut_end_depth = config['cut-depth']
        
        if config['use-holders']:
            #cnc.setCutDepth( config['cut-depth'] - config['holder-height'])
            holder_cut_start_depth = config['pcb-thickness'] - config['holder-height']
            holder_cut_end_depth = cut_end_depth
            cut_end_depth = holder_cut_start_depth

        cnc.setCutStep( config['cut-step'] )

        # TODO: cut Z control

        if config['use-continuity-probe']:
            cnc.zeroZtoTool()
        
        cnc.zeroAll()
        cnc.setAbsolute()
        cnc.spindleON()
        
        # Cutting
        cnc.addComment('Cutting')
        if paths2:
            i = 1
            for tlp in paths:
                cnc.addComment('Path #' + str(i) )
                i += 1
                cnc.cutPath(tlp, cut_end_depth=cut_end_depth)

        # Cutting holders
        if config['use-holders']:
            cnc.addComment('Cutting Holders')
            if paths2:
                i = 1
                for tlp in paths2:
                    cnc.addComment('Path #' + str(i) )
                    i += 1
                    cnc.cutPath(tlp, 
                        cut_start_depth=holder_cut_start_depth,
                        cut_end_depth=holder_cut_end_depth)
        
        # End code
        cnc.stopMilling()
        cnc.spindleOFF()


if __name__ == '__main__':
    main()
