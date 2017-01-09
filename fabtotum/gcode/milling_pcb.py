from .cnc import CNC

import math
from shapely.geometry import Point,LineString,Polygon,box

eZERO    = 0
eSAFE    = 1
eTRAVEL  = 2
eMILLING = 3

class MillingPCB(CNC):

    def __init__(self, output):
        super(MillingPCB, self).__init__(output)
        # Travel XY speed
        self.travel_speed_xy = 1000
        # Travel Z speed
        self.travel_speed_z = 1000
        # Milling XY speed
        self.milling_speed_xy = 100
        # Cutting XY speed
        self.cutting_speed_xy = 100
        # Drilling Z speed
        self.drill_speed_z = 50;
        # Travel Up distance
        self.travel_distance_z = 5
        # Plunge distance
        self.plunge_depth = 0.1
        # Drill depth
        self.drill_depth = 2
        # Cut depth
        self.cut_depth = 2
        # Cut step
        self.cut_step = 0.25
        self.cut_start_depth = 0
        # Minimal xy step
        self.min_xy_step = 0.01
        
        # Pauses
        self.mill_start_pause = 1000
        
        self.absTravelZ  = self.travel_distance_z
        self.absMillingZ = -self.plunge_depth
        self.absDrillZ = -self.drill_depth
        self.absCutZ = -self.cut_depth
        
    def __update_z_levels(self):
        self.absTravelZ  = self.travel_distance_z
        self.absMillingZ = -self.plunge_depth
        self.absDrillZ      = -self.drill_depth
        self.absCutZ     = -self.cut_depth
        
    def __isAtMillingZ(self):
        #return (self.curZ - self.absMillingZ) < 1e-8
        #return self.__isAtZ(self.absMillingZ)
        return self.isAt(Z = self.absMillingZ)
        
    def __isAtTravelZ(self):
        #return (self.curZ == self.absTravelZ)
        #return self.__isAtZ(self.absTravelZ)
        return self.isAt(Z = self.absTravelZ)
    
    def setMillingStartPause(self, value):
        self.mill_start_pause = value
    
    def setMinimalXYStep(self, step):
        self.min_xy_step = step
        
    def setTravelSpeed(self, XY, Z = None):
        self.travel_speed_xy = XY
        if not Z:
            Z = XY
        self.travel_speed_z = Z
        
    def setMillingSpeed(self, speed):
        self.milling_speed_xy = speed
        # For now they are same
        self.cutting_speed_xy = speed
        
    def setDrillSpeed(self, speed):
        self.drill_speed_z = speed
        # For now they are same
        self.cut_speed_z = speed
    
    #~ def setCutSpeed(self, speed):
        #~ self.cut_speed_z = speed
        
    def setTravelHeight(self, U):
        self.travel_distance_z = U
        self.__update_z_levels()
        
    def setPlungeDepth(self, P):
        self.plunge_depth = P
        self.__update_z_levels()
        
    def setDrillDepth(self, P):
        self.drill_depth = P
        self.__update_z_levels()
        
    def setCutDepth(self, P):
        self.cut_depth = P
        self.__update_z_levels()
        
    def setCutStep(self, S):
        self.cut_step = S

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
        self.addComment('Set zero all to current position')
        self.raw.G92(Z=0)
        self.raw.M746(S=0)
        self.addComment('Disable continuity probe')

    def moveToDrillZ(self, drill_z = None):
        if self.isAbsolute():
            self.moveToZ(Z=self.absDrillZ, F=self.drill_speed_z, use_tool=True)
        else:
            x,y,z = self.convertToRelative(absZ=self.absDrillZ)
            #print "relative travel z =", z
            self.moveToZ(Z=z, F=self.drill_speed_z, use_tool=True)

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
            feedrate = self.drill_speed_z
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
            feedrate = self.drill_speed_z
            
        if not self.__isAtMillingZ():
            if self.isAbsolute():
                self.moveToZ(Z=self.absMillingZ, F=feedrate, use_tool=True)
                if self.mill_start_pause > 0:
                    self.sync()
                    self.wait(M=self.mill_start_pause)
            else:
                x,y,z = self.convertToRelative(absZ=self.absMillingZ)
                #print "relative milling z =", z
                self.moveToZ(Z=z, F=feedrate, use_tool=True)
                if self.mill_start_pause > 0:
                    self.sync()
                    self.wait(M=self.mill_start_pause)

    def travelTo(self, X, Y):
        """
        Travel to ``X``,``Y`` coordinates without milling.
        """
        if not self.isAt(X=X, Y=Y):
            self.moveToTravelZ()
            self.moveToXY(X, Y, F=self.travel_speed_xy)
        
    def millTo(self, X, Y, feedrate=None):
        
        if feedrate == None:
            feedrate = self.milling_speed_xy
        
        self.moveToMillingZ()
        self.moveToXY(X, Y, F=feedrate, use_tool=True)
        
    def cutTo(self, X, Y, cut_depth, feedrate=None):
        if feedrate == None:
            feedrate = self.cutting_speed_xy
        self.moveToCutZ(cut_depth)
        self.moveToXY(X, Y, F=feedrate, use_tool=True)
        
    def drillAt(self, X, Y, drill_depth = None):
        if drill_depth == None:
            drill_depth = self.drill_depth
        
        self.travelTo(X,Y)
        self.moveToDrillZ(drill_depth)
        self.moveToTravelZ()
    
    def millRect(self, X, Y, W, H, feedrate=None):
        self.travelTo(X,Y)
        if self.isAbsolute():
            self.millTo(X+W, Y, feedrate)
            self.millTo(X+W, Y-H, feedrate)
            self.millTo(X, Y+H, feedrate)
            self.millTo(X, Y, feedrate)
        else:
            self.millTo(+W, 0, feedrate)
            self.millTo(0, -H, feedrate)
            self.millTo(-W, 0, feedrate)
            self.millTo(0, +H, feedrate)
        self.stopMilling()
    
    def __optimize(self, obj):
        opt_obj = obj.simplify(tolerance=self.min_xy_step, preserve_topology=True)
        return opt_obj
    
    def __reverse(self, obj):
        obj_cpy = LineString(obj)
        obj_cpy.coords = list(obj_cpy.coords)[::-1]
        return obj_cpy
    
    def millPath(self, path, feedrate=None, reverse=False):
        # TODO: check if path is shapely object
        op = self.__optimize(path)
        
        if reverse:
            op = self.__reverse(op)
        
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
                    self.travelTo(rx,ry)
            else:
                if self.isAbsolute():
                    self.millTo(X,Y, feedrate=feedrate)
                else:
                    (rx,ry,rz) = self.convertToRelative(X,Y)
                    self.millTo(rx,ry, feedrate=feedrate)

    def cutPath(self, path, feedrate=None, cut_start_depth = None, cut_end_depth = None, cut_step = None):
        # TODO: check if path is shapely object
        op = self.__optimize(path)
        x = list(op.xy[0])
        y = list(op.xy[1])
        need_to_travel = True
        
        if cut_start_depth == None:
            cut_start_depth = self.cut_start_depth
            
        if cut_end_depth == None:
            cut_end_depth = self.cut_depth
            
        if cut_step == None:
            cut_step = self.cut_step
        
        #~ print "cut_start_depth,cut_end_depth", cut_start_depth,cut_end_depth
        
        num_of_steps = int(math.ceil( (cut_end_depth - cut_start_depth) / cut_step))
        #~ print "num_of_steps",num_of_steps
        for step in range(1,num_of_steps+1):
            cut_depth = cut_start_depth + (self.cut_step * step)
            
            #~ print "target_cut_depth",cut_depth,"[",cut_step,"]",cut_end_depth
            
            if cut_depth > cut_end_depth:
                cut_depth = cut_end_depth
            
            #~ print "cut_depth",cut_depth,"[",cut_step,"]"
            self.addComment('Cut-Depth: ' + str(cut_depth) )
            
            for i in range(len(x)):
                X = x[i]
                Y = y[i]
                
                if i == 0 and need_to_travel:
                    need_to_travel = False
                    if self.isAbsolute():
                        self.travelTo(X,Y)
                    else:
                        (rx,ry,rz) = self.convertToRelative(X,Y)
                        self.travelTo(rx,ry)

                if self.isAbsolute():
                    self.cutTo(X,Y, cut_depth)
                else:
                    (rx,ry,rz) = self.convertToRelative(X,Y)
                    self.cutTo(rx,ry, cut_depth)
            

            if X != x[0] or Y != y[0]:
                self.addComment('Reversing movement')
                #~ print "reversing"
                # Reverse the direction for next step
                x.reverse()
                y.reverse()  
                

    def millContures(self, objs):
        pass

    def stopMilling(self):
        self.moveToTravelZ()
