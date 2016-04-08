#!/bin/env python2

from fabtotum import gerber
from fabtotum.gerber.render import *
from fabtotum.toolpath import *
from fabtotum.gcode import *

import os,sys
import argparse
import json

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
	
	app_args = parser.parse_args()

	config = {
		# Z tuning
		'travel-height'	:	2.0, 	# Height used for travel moves
		'cut-depth'		:	1.65, 	# Cutting depth
		'cut-step'		:	0.2, 	# Cutting is done in steps if Z
		# V bit
		'plunge-depth' 	: 	0.25,
		'mill-bit-diameter'	: 0.4,	# Milling tool diameter at plunge-depth
		# Endcut bit
		'cut-bit-diameter'	: 2.1,	# Cutting tool diameter
		# Milling speed
		'spindle-speed'		: 15000,	# Spindle speed (CW)
		'milling-xy-speed'	: 80,		# XY speed during milling moves
		'cutting-xy-speed'		: 150,		# XY speed during cutting moves
		'drilling-z-speed'		: 50,		# Z speed during drilling moves
		'travel-xy-speed'	: 5000,		# XY speed during travel moves (at travel height)
		'travel-z-speed'	: 1000,		# Z speed for getting to travel height
		# Probe
		'use-continuity-probe'	:	True,
		# Holders
		'use-holders'	: True,	# Skip cutting PCB at some places to keep it in place
		'holder-size'	: 2.0,  # Single holder size
		'holder-height'	: 0.8,	# Thickness of the holders
		# Array (TODO)
		# Rotation (TODO)
		# Markers
		'markers' : [(70,23), (70,177), (164,177), (164,23)],
		# PCB
		'pcb-thickness' : 1.6
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
		layer.cam_source.render( shp )
		layer_shape[layer.layer_class] = shp
		
		if layer.layer_class == 'bottom':
			shp.mirror_x()
		elif layer.layer_class == 'outline':
			shp.set_ignore_width(True)
			shp_m = ShapelyContext()
			shp_m.set_ignore_width(True)
			layer.cam_source.render( shp_m )
			layer_shape[layer.layer_class+'_mirror'] = shp_m

	# Prepare copper layer milling
	for layer in pcb.copper_layers:
		if not os.path.exists(app_args.output):
			os.mkdir(app_args.output, 0755)
		
		out = GCodeOutput(app_args.output+'/'+layer.layer_class+'.gcode')
		toolpath = IsolationToolpath()
		toolpath.add_tool( config['mill-bit-diameter'] )
		paths = toolpath.generate(layer_shape[layer.layer_class].figs)

		cnc = MillingPCB(out)

		# Start code
		cnc.setTravelSpeed	(	XY= config['travel-xy-speed'],
								Z = config['travel-z-speed'])
		cnc.setMillingSpeed		( config['milling-xy-speed'] )
		cnc.setDrillSpeed		( config['drilling-z-speed'] )
		cnc.setTravelDistance	( config['travel-height'] )
		cnc.setPlungeDepth		( config['plunge-depth'] )
		cnc.setSpindleSpeed		( config['spindle-speed'] )

		if config['use-continuity-probe']:
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
			out = GCodeOutput(app_args.output+'/'+layer.layer_class+'_'+str(drill)+'.gcode')
			
			cnc = MillingPCB(out)

			# Start code
			cnc.setTravelSpeed	(	XY= config['travel-xy-speed'],
									Z = config['travel-z-speed'])
			cnc.setMillingSpeed		( config['milling-xy-speed'] )
			cnc.setDrillSpeed		( config['drilling-z-speed'] )
			cnc.setTravelDistance	( config['travel-height'] )
			cnc.setPlungeDepth		( config['plunge-depth'] )
			cnc.setSpindleSpeed		( config['spindle-speed'] )

			if config['use-continuity-probe']:
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
		out = GCodeOutput(app_args.output+'/'+layer.layer_class+'.gcode')
		
		toolpath = IsolationToolpath()
		toolpath.add_tool( config['cut-bit-diameter'] )
		paths = toolpath.generate(layer_shape[layer.layer_class].figs)

		toolpath2 = HoldersToolpath()
		toolpath2.set_holder_params(holder_size = config['holder-size'],
									 min_len = 10 )  # TODO: make a configuration
		toolpath2.add_tool( config['cut-bit-diameter'] )
		paths2 = toolpath2.generate(layer_shape[layer.layer_class].figs)

		cnc = MillingPCB(out)

		# Start code
		cnc.setTravelSpeed	(	XY= config['travel-xy-speed'],
								Z = config['travel-z-speed'])
		cnc.setMillingSpeed		( config['milling-xy-speed'] )
		cnc.setDrillSpeed		( config['drilling-z-speed'] )
		cnc.setTravelDistance	( config['travel-height'] )
		cnc.setPlungeDepth		( config['plunge-depth'] )
		cnc.setSpindleSpeed		( config['spindle-speed'] )
		
		cut_start_depth = 0
		cut_end_depth = config['pcb-thickness'] + 0.1 #config['cut-depth']
		
		if config['use-holders']:
			#cnc.setCutDepth( config['cut-depth'] - config['holder-height'])
			holder_cut_start_depth = config['pcb-thickness'] - config['holder-height']
			holder_cut_end_depth = cut_end_depth
			cut_end_depth = holder_cut_start_depth

		cnc.setCutStep( config['cut-step'] )

		# TODO: cut Z control

		if config['use-continuity-probe']:
			cnc.zeroZtoTool()
		
		cnc.setRelative()
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
		cnc.addComment('Cutting Holders')
		if paths:
			i = 1
			for tlp in paths:
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
