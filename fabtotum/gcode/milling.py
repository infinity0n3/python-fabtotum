from .cnc import CNC

import math

eZERO    = 0
eSAFE    = 1
eTRAVEL  = 2
eMILLING = 3

class Milling(CNC):

    def __init__(self, output):
        super(Milling, self).__init__(output)
        # Travel XY speed
        self.travel_speed_xy = 1000
        # Travel Z speed
        self.travel_speed_z = 1000
        # Milling XY speed
        self.milling_speed_xy = 100
        # Travel Up distance
        self.travel_distance_z = 5
        # Plunge distance
        self.plunge_depth = 0.1
        # Plunge speed
        self.plunge_speed = 50
        # Minimal xy step
        self.min_xy_step = 0.01
        
        self.absTravelZ  = self.travel_distance_z
        self.absMillingZ = -self.plunge_depth
        
    def __update_z_levels(self):
        self.absTravelZ  = self.travel_distance_z
        self.absMillingZ = -self.plunge_depth
        
    def __isAtMillingZ(self):
        return self.isAt(Z = self.absMillingZ)
        
    def __isAtTravelZ(self):
        return self.isAt(Z = self.absTravelZ)
        
    def setMinimalXYStep(self, step):
        self.min_xy_step = step
        
    def setTravelSpeed(self, XY, Z = None):
        self.travel_speed_xy = XY
        if not Z:
            Z = XY
        self.travel_speed_z = Z
        
    def setMillingSpeed(self, speed):
        self.milling_speed_xy = speed
        
    def setPlungeSpeed(self, S):
        self.plunge_speed = S
        
    def setTravelHeight(self, U):
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

    def moveToDrillZ(self, drill_z = None):
        if self.isAbsolute():
            self.moveToZ(Z=self.absDrillZ, F=self.plunge_speed, use_tool=True)
        else:
            x,y,z = self.convertToRelative(absZ=self.absDrillZ)
            #print "relative travel z =", z
            self.moveToZ(Z=z, F=self.plunge_speed, use_tool=True)

    def moveToTravelZ(self, feedrate = None):
        if feedrate == None:
            feedrate = self.travel_speed_z
            
        if not self.__isAtTravelZ():
            if self.isAbsolute():
                self.moveToZ(Z=self.absTravelZ, F=feedrate)
            else:
                x,y,z = self.convertToRelative(absZ=self.absTravelZ)
                #print "relative travel z =", z
                self.moveToZ(Z=z, F=self.feedrate)

    def moveToCutZ(self, cut_depth, feedrate=None):
        if feedrate == None:
            feedrate = self.plunge_speed
        #new_z = -self.cut_step * step
        new_z = -cut_depth
        if not self.isAt(Z=new_z):
            if self.isAbsolute():
                self.moveToZ(Z=new_z, F=feedrate, use_tool=True)
            else:
                x,y,z = self.convertToRelative(absZ=new_z)
                #print "relative milling z =", z
                self.moveToZ(Z=z, F=self.feedrate, use_tool=True)

    def moveToMillingZ(self, feedrate=None):
        if feedrate == None:
            feedrate = self.plunge_speed
            
        if not self.__isAtMillingZ():
            if self.isAbsolute():
                self.moveToZ(Z=self.absMillingZ, F=feedrate, use_tool=True)
            else:
                x,y,z = self.convertToRelative(absZ=self.absMillingZ)
                #print "relative milling z =", z
                self.moveToZ(Z=z, F=feedrate, use_tool=True)

    def travelTo(self, X, Y):
        """
        Travel to ``X``,``Y`` coordinates without milling.
        """
        if not self.isAt(X, Y):
            self.moveToTravelZ()
            self.moveToXY(X, Y, F=self.travel_speed_xy)
        
    def millTo(self, X, Y):
        self.moveToMillingZ()
        self.moveToXY(X, Y, F=self.milling_speed_xy, use_tool=True)
    
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
    
    def millPolyline(self, points, reverse = False):        
        if not points:
            return
            
        if reverse:                
            p0 = points[-1]
            x0 = p0[0]
            y0 = p0[1]
            
            self.travelTo(x0,y0)
            for pt in reversed(points[:-1]):
                self.millTo( pt[0], pt[1] )
        else:                
            p0 = points[0]
            x0 = p0[0]
            y0 = p0[1]
            
            self.travelTo(x0,y0)
            for pt in points[1:]:
                self.millTo( pt[0], pt[1] )
    
    def __optimize(self, obj):
        opt_obj = obj.simplify(tolerance=self.min_xy_step, preserve_topology=True)
        return opt_obj
    
    #~ def millPath(self, path):
        #~ # TODO: check if path is shapely object
        #~ op = self.__optimize(path)
        #~ x = op.xy[0]
        #~ y = op.xy[1]
        
        #~ for i in range(len(x)):
            #~ X = x[i]
            #~ Y = y[i]

            #~ if i == 0:
                #~ if self.isAbsolute():
                    #~ self.travelTo(X,Y)
                #~ else:
                    #~ (rx,ry,rz) = self.convertToRelative(X,Y)
                    #~ self.travelTo(rx,ry)
            #~ else:
                #~ if self.isAbsolute():
                    #~ self.millTo(X,Y)
                #~ else:
                    #~ (rx,ry,rz) = self.convertToRelative(X,Y)
                    #~ self.millTo(rx,ry)

    #~ def cutPath(self, path, cut_start_depth = None, cut_end_depth = None, cut_step = None):
        #~ # TODO: check if path is shapely object
        #~ op = self.__optimize(path)
        #~ x = list(op.xy[0])
        #~ y = list(op.xy[1])
        #~ need_to_travel = True
        
        #~ if cut_start_depth == None:
            #~ cut_start_depth = self.cut_start_depth
            
        #~ if cut_end_depth == None:
            #~ cut_end_depth = self.cut_depth
            
        #~ if cut_step == None:
            #~ cut_step = self.cut_step
        
        #~ print "cut_start_depth,cut_end_depth",cut_start_depth,cut_end_depth
        
        #~ num_of_steps = int(math.ceil( (cut_end_depth - cut_start_depth) / cut_step))
        #~ print "num_of_steps",num_of_steps
        #~ for step in range(1,num_of_steps+1):
            #~ cut_depth = cut_start_depth + (self.cut_step * step)
            
            #~ if cut_depth > cut_end_depth:
                #~ cut_depth = cut_end_depth
            
            #~ print "cut_depth",cut_depth,"[",cut_step,"]"
            #~ self.addComment('Cut-Depth: ' + str(cut_depth) )
            
            #~ for i in range(len(x)):
                #~ X = x[i]
                #~ Y = y[i]
                
                #~ if i == 0 and need_to_travel:
                    #~ need_to_travel = False
                    #~ if self.isAbsolute():
                        #~ self.travelTo(X,Y)
                    #~ else:
                        #~ (rx,ry,rz) = self.convertToRelative(X,Y)
                        #~ self.travelTo(rx,ry)

                #~ if self.isAbsolute():
                    #~ self.cutTo(X,Y, cut_depth)
                #~ else:
                    #~ (rx,ry,rz) = self.convertToRelative(X,Y)
                    #~ self.cutTo(rx,ry, cut_depth)
            
                    #~ if X != x[0] or Y != y[0]:
                        #~ self.addComment('Reversing movement')
                        #~ print "reversing"
                        #~ # Reverse the direction for next step
                        #~ x.reverse()
                        #~ y.reverse()

    #~ def millContures(self, objs):
        #~ pass

    def stopMilling(self):
        self.moveToTravelZ()
