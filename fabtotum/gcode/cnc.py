"""
CNC module used to abstract calling RAW GCodes.
"""

from .raw import RAW

class CNC(object):
	"""
	CNC class abstracting RAW GCode usage.
	"""
	
	"""Absolute coordinates."""
	eABSOLUTE = 1
	"""Relative coordinates."""
	eRELATIVE = 2
	"""Clock wise movement."""
	eCW  = 0
	"""Counter clock wise movement."""		
	eCCW = 1
	
	def __init__(self, output):
		"""
		Construct a new CNC object.
		
		Parameters
		----------
		output: Output
			Output object used to write gcodes to.
			
		Attributes
		----------
		raw : RAW
			RAW gcode access.
		curX : int
			Current X coordinate.

		curY : int
			Current Y coordinate.
			
		curZ : int
			Current Z coordinate.
			
		curE : int
			Current E coordinate.
			
		curF : int
			Current Feed rate.
			
		spindle_on : bool
			Spindle state.
			
		spindle_direction : (eCW,eCCW)
			Spindle spin direction.
			
		spindle_speed: int
			Spindle speed.
			
		mvType: (eABSOLUTE,eRELATIVE)
			Movement type.
		"""
		self.raw = RAW(output)
		self.curX = 0
		self.curY = 0
		self.curZ = 0
		self.curE = 0
		self.curF = 0
		self.spindle_on = False
		self.spindle_direction = CNC.eCW
		self.spindle_speed = 10000
		self.mvType = CNC.eABSOLUTE
		self.stType = None
		self.upType = True
		self.decimals = 5

	def __update(self):
		if self.upType:
			if self.mvType == CNC.eABSOLUTE:
				self.setAbsolute()
			else:
				self.setRelative()
				
			self.upType = False

	def addComment(self, comment):
		"""Add comment."""
		self.raw.COMMENT(comment)

	def zeroAll(self):
		"""Zero all axes."""
		self.raw.G92(X=0, Y=0, Z=0)
		self.curX = 0
		self.curY = 0
		self.curZ = 0
		self.curE = 0
		
	def zeroZ(self):
		"""Zero only Z axes."""
		self.raw.G92(Z=0)
		self.curZ = 0

	def homeAll(self):
		"""Home all axes."""
		self.raw.G28()
		self.curX = 0
		self.curY = 0
		self.curZ = 0
		
	def homeXY(self):
		"""Home only X and Y axis."""
		self.raw.G28(X = True, Y = True)
		self.curX = 0
		self.curY = 0
		self.curF = 0
		
	def homeZ(self):
		"""Home only Z axis"""
		self.raw.G27()
		self.curZ = 0
		self.curF = 0
	
	def getCurrentPosition(self):
		"""
		Return current position.
		
		Returns:
			tuple (<float>,<float>,<float>): current X,Y,Z position
		"""
		return (self.curX,self.curY,self.curZ)
	
	def convertToRelative(self, absX = None, absY = None, absZ = None):
		"""
		Converts absolute coordinate to relative 
		based on current position.
		
		Args:
			absX (float): absolute X coordinate
			absY (float): absolute Y coordinate
			absZ (float): absolute Z coordinate
		
		Returns:
			tuple (<float>,<float>,<float>): relative X,Y,Z coordinats.
		"""
		if self.mvType == CNC.eABSOLUTE:
			return (absX, absY, absZ)
		
		relX = None
		relY = None
		relZ = None
		
		if absX != None:
			relX = absX - self.curX
			
		if absY != None:
			relY = absY - self.curY
			
		if absZ != None:
			relZ = absZ - self.curZ
		
		return (relX, relY, relZ)

	def isAbsolute(self):
		"""Check whether current movement is of absolute type."""
		return (self.mvType == CNC.eABSOLUTE)
		
	def isRelative(self):
		"""Check whether current movement is of relative type."""
		return (self.mvType == CNC.eRELATIVE)

	def setAbsolute(self):
		"""Set absolute movement type."""
		if (self.mvType != CNC.eABSOLUTE) or self.upType:
			self.mvType = CNC.eABSOLUTE
			self.raw.G90()
			self.upType = False
	
	def setRelative(self):
		"""Set relative movement type."""
		if (self.mvType != CNC.eRELATIVE) or self.upType:
			self.mvType = CNC.eRELATIVE
			self.raw.G91()
			self.upType = False

	def storeSettings(self):
		self.stType = self.mvType
		
	def restoreSettings(self):
		if self.mvType != self.stType:
			self.upType = True
		self.mvType = self.stType
		self.__update()
		
	def setSpindleSpeed(self, speed):
		"""
		Set spindle speed to ``speed``.
		
		Args:
			speed (int): Spindle speed in RPM.
		"""
		self.spindle_speed = speed
		
	def turnSpindleOn(self):
		"""Turn spindle on."""
		self.addComment('Finish all moves')
		self.raw.M400()
		self.addComment('Turning spindle on')
		# turn spindle on
		if self.spindle_direction == CNC.eCW:
			self.raw.M3(S=self.spindle_speed)
		else:
			self.raw.M4(S=self.spindle_speed)
		# wait 3 seconds
		self.raw.G4(S=3)
		self.addComment('Spindle is on @ '+str(self.spindle_speed)+' rpm')
		
	def turnSpindleOff(self):
		"""Turn spindle off."""
		self.addComment('Finish all moves')
		self.raw.M400()
		self.addComment('Turning spindle off')
		# turn spindle off
		self.raw.M5()
		# wait 3 seconds
		self.raw.G4(S=3)
		self.addComment('Spindle is off')
		
	def moveToXYZ(self, X = None, Y = None, Z = None, F = None):
		"""
		Execute movement to `X`,`Y`,`Z` coordinates with speed of `F`.
		
		Args:
			X (float): X coordinate [mm]
			Y (float): Y coordinate [mm]
			Z (float): Z coordinate [mm]
			F (float): Feedrate [mm/min]
			
			Example:
				>>> cnc.moveToXYZ(X=10, Y=10, Z=-0.1, F=100)
		"""
		self.__update()
		
		if X != None:
			X = round(X, self.decimals)
		if Y != None:
			Y = round(Y, self.decimals)
		if Z != None:
			Z = round(Z, self.decimals)
		
		if self.mvType == CNC.eABSOLUTE:
			self.curX = X
			self.curY = Y
			self.curZ = Z
		else:
			self.curX += X
			self.curY += Y
			self.curZ += Z
		
		if self.curF == F:
			F = None
		else:
			self.curF = F
		
		self.raw.G0(X=X, Y=Y, Z=Z, F=F)		

	def moveToXY(self, X = None, Y = None, F = None):
		"""
		Execute movement to `X`,`Y` coordinates with speed of `F`.
		Z coordinate is not affected.
		
		Args:
			X (float): X coordinate [mm]
			Y (float): Y coordinate [mm]
			F (float): Feedrate [mm/min]
			
			Example:
				>>> cnc.moveToXY(X=10, Y=10, F=1000)
		"""
		X = round(X, self.decimals)
		Y = round(Y, self.decimals)
		
		self.__update()
		if self.mvType == CNC.eABSOLUTE:
			self.curX = X
			self.curY = Y
		else:
			self.curX += X
			self.curY += Y

		if self.curF == F:
			F = None
		else:
			self.curF = F
					
		self.raw.G0(X=X, Y=Y, F=F)
		
	def moveToZ(self, Z = None, F = None):
		"""
		Execute movement to `Z` coordinates with speed of `F`.
		X,Y coordinates are not affected.
		
		Args:
			X (float): X coordinate [mm]
			F (float): Feedrate [mm/min]
			
			Example:
				>>> cnc.moveToZ(Z=2, F=150)
		"""
		self.__update()
		
		Z = round(Z, self.decimals)
		
		if self.mvType == CNC.eABSOLUTE:
			self.curZ = rount(Z, self.decimals)
		else:
			self.curZ += Z
			
		print "curZ", self.curZ
			
		self.raw.G0(Z=Z, F=F)
