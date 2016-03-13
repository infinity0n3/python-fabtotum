from .cnc import CNC

eZERO	= 0
eSAFE	= 1
eTRAVEL  = 2
eMILLING = 3

class Milling2D(CNC):

	def __init__(self, output):
		super(Milling2D, self).__init__(output)
		# Travel XY speed
		self.travel_speed_xy = 1000
		# Travel Z speed
		self.travel_speed_z = 1000
		# Milling XY speed
		self.milling_speed_xy = 100
		# Drilling Z speed
		self.drill_speed_z = 50;
		# Travel Up distance
		self.travel_distance_z = 5
		# Plunge distance
		self.plunge_depth = 0.1
		# Minimal xy step
		self.min_xy_step = 0.01
		
		self.absTravelZ  = self.travel_distance_z
		self.absMillingZ = -self.plunge_depth
		
	def __update_z_levels(self):
		self.absTravelZ  = self.travel_distance_z
		self.absMillingZ = -self.plunge_depth
		
	def __isAtMillingZ(self):
		return (self.curZ - self.absMillingZ) < 1e-8
		
	def __isAtTravelZ(self):
		return (self.curZ == self.absTravelZ)
		
	def setMinimalXYStep(self, step):
		self.min_xy_step = step
		
	def setTravelSpeed(self, XY, Z = None):
		self.travel_speed_xy = XY
		if not Z:
			Z = XY
		self.travel_speed_z = Z
		
	def setMillingSpeed(self, speed):
		self.milling_speed_xy = speed
		
	def setDrillSpeed(self, speed):
		self.drill_speed_z = speed
		
	def setTravelDistance(self, U):
		self.travel_distance_z = U
		self.__update_z_levels()
		
	def setPlungeDepth(self, P):
		self.plunge_depth = P
		self.__update_z_levels()

	def spindleON(self):
		self.moveToTravelZ()
		self.turnSpindleOn()
		
	def spindleOFF(self):
		self.stopMilling()
		self.turnSpindleOff()

	def zeroZtoTool(self):
		self.addComment('Enable continuity probe')
		self.raw.M746(S=1)
		self.raw.G38()
		self.addComment('Set zero Z to current position')
		self.raw.G92(Z=0)
		self.raw.M746(S=0)
		self.addComment('Disable continuity probe')

	def moveToTravelZ(self):
		if not self.__isAtTravelZ():
			if self.isAbsolute():
				self.moveToZ(Z=self.absTravelZ, F=self.travel_speed_z)
			else:
				x,y,z = self.convertToRelative(absZ=self.absTravelZ)
				print "relative travel z =", z
				self.moveToZ(Z=z, F=self.travel_speed_z)

	def moveToMillingZ(self):
		if not self.__isAtMillingZ():
			if self.isAbsolute():
				self.moveToZ(Z=self.absTravelZ, F=self.drill_speed_z)
			else:
				x,y,z = self.convertToRelative(absZ=self.absMillingZ)
				print "relative milling z =", z
				self.moveToZ(Z=z, F=self.drill_speed_z)

	def travelTo(self, X, Y):
		"""
		Travel to ``X``,``Y`` coordinates without milling.
		"""
		#~ if not self.__isAtTravelZ():
			#~ self.storeSettings()
			#~ self.setAbsolute()
			#~ self.moveToZ(Z=self.absTravelZ, F=self.drill_speed_z)
			#~ self.restoreSettings()
		self.moveToTravelZ()
			
		self.moveToXY(X, Y, F=self.travel_speed_xy)
		
	def millTo(self, X, Y):
		#~ if not self.__isAtMillingZ():
			#~ self.storeSettings()
			#~ self.setAbsolute()
			#~ self.moveToZ(Z=self.absMillingZ, F=self.drill_speed_z)
			#~ self.restoreSettings()
		self.moveToMillingZ()
			
		self.moveToXY(X, Y, F=self.milling_speed_xy)
	
	def millRect(self, X, Y, W, H):
		self.travelTo(X,Y)
		if self.isAbsolute():
			self.millTo(X+W, Y)
			self.millTo(X+W, Y-H)
			self.millTo(X, Y+H)
			self.millTo(X, Y)
		else:
			self.millTo(+W, 0)
			self.millTo(0, -H)
			self.millTo(-W, 0)
			self.millTo(0, +H)
		self.stopMilling()
	
	def __optimize(self, obj):
		opt_obj = obj.simplify(tolerance=self.min_xy_step, preserve_topology=True)
		return opt_obj
	
	def millPath(self, path):
		# TODO: check if path is shapely object
		op = self.__optimize(path)
		x = op.xy[0]
		y = op.xy[1]
		
		for i in range(len(x)):
			X = x[i]
			Y = y[i]

			if i == 0:
				if self.isAbsolute():
					self.travelTo(X,Y)
				else:
					(rx,ry,rz) = self.convertToRelative(X,Y)
					self.travelTo(X,Y)
			else:
				if self.isAbsolute():
					self.millTo(X,Y)
				else:
					(rx,ry,rz) = self.convertToRelative(X,Y)
					self.millTo(rx,ry)

	def millContures(self, objs):
		pass

	def stopMilling(self):
		self.moveToTravelZ()
