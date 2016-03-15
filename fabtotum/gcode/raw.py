class RAW(object):
    """
    RAW GCodes for Marlin/FABtotum version.
    GCode list take from:
    http://forum.fabtotum.cc/showthread.php?1364-Supported-Gcodes
    """
    def __init__(self, output):
        self.output = output
    
    def COMMENT(self, comment):
        self.output.write('; ' + comment)
    
    #~ Implemented Codes
    #~ -------------------
    #~ G0  -> G1
    #~ G1  - Coordinated Movement X Y Z E F, S?
    def G0(self, X = None, Y = None, Z = None, E = None, F = None):
        code = 'G0'
        if X != None:
            code += ' X' + str(X)
        if Y != None:
            code += ' Y' + str(Y)
        if Z != None:
            code += ' Z' + str(Z)
        if E != None:
            code += ' E' + str(E)
        if F != None:
            code += ' F' + str(F)
        
        self.output.write(code)
        
    def G1(self, X = None, Y = None, Z = None, E = None, F = None):
        self.G0(X, Y, Z, E, F)
        
    #~ G2  - CW ARC
    # Example: G2 X90.6 Y13.8 I5 J10 E22.4, Move in a CW arc starting from current point to point (X,Y) with center at (X+I, Y+J), extruding 22.4mm of material
    def G2(self, X = None, Y = None, I = None, J = None, E = None, F = None):
        code = 'G2'
        if X != None:
            code += ' X' + str(X)
        if Y != None:
            code += ' Y' + str(Y)
        if Z != None:
            code += ' I' + str(I)
        if E != None:
            code += ' J' + str(J)
        if F != None:
            code += ' F' + str(F)
        
        self.output.write(code)

    #~ G3  - CCW ARC
    def G3(self, X = None, Y = None, I = None, J = None, E = None, F = None):
        code = 'G3'
        if X != None:
            code += ' X' + str(X)
        if Y != None:
            code += ' Y' + str(Y)
        if Z != None:
            code += ' I' + str(I)
        if E != None:
            code += ' J' + str(J)
        if F != None:
            code += ' F' + str(F)
        
        self.output.write(code)

    #~ G4  - Dwell S<seconds> or P<milliseconds>
    def G4(self, S = None, P = None):
        code = 'G4'
        if S != None:
            code += ' S' + str(S)
        if P != None:
            code += ' P' + str(P)
        
        self.output.write(code)

    #~ G10 S<0..1> - retract filament according to settings of M207
    def G10(self):
        pass

    #~ G11 - retract recover filament according to settings of M208
    def G11(self):
        pass

    #~ G27 - Home Z axis max (no plane needed)
    def G27(self):
        code = 'G27'
        self.output.write(code)
        
    #~ G28 - Home all Axis
    def G28(self, X = None, Y = None, Z = None):
        code = 'G28'
        if X != None:
            code += ' X'
        if Y != None:
            code += ' Y'
        if Z != None:
            code += ' Z'
        
        self.output.write(code)

    #~ G29 - Detailed Z-Probe, probes the bed at 3 or more points.  Will fail if you haven't homed yet.
    def G29(self):
        code = 'G29'
        self.output.write(code)

    #~ G30 U<up_speed>, D<down-speed> - Single Z Probe, probes bed at current XY location S<mm> searching Z length
    def G30(self, U = None, D = None):
        code = 'G28'
        if U != None:
            code += ' U' + str(U)
        if D != None:
            code += ' D' + str(U)
        
        self.output.write(code)
        
    #~ G38 S<feedrate> - External Z Conductive Probe, feedrate defaults to 120 mm/sec, feedrate limited to 200 mm/sec maximum
    #~                   Use M746 to activate and deactivate (see Factotum custom M codes below)
    def G38(self, S = None):
        code = 'G38'
        if S != None:
            code += ' S' + str(S)
        
        self.output.write(code)

    #~ G90 - Use Absolute Coordinates
    def G90(self):
        code = 'G90'
        self.output.write(code)

    #~ G91 - Use Relative Coordinates
    def G91(self):
        code = 'G91'
        self.output.write(code)

    #~ G92 - Set current position to coordinates given
    #        Without coordinates will reset all axes to zero
    def G92(self, X = None, Y = None, Z = None, E = None):
        code = 'G92'
        if X != None:
            code += ' X' + str(X)
        if Y != None:
            code += ' Y' + str(Y)
        if Z != None:
            code += ' Z' + str(Z)
        if E != None:
            code += ' E' + str(E)
        
        self.output.write(code)

    #~ 
    #~ M Codes
    #~ 
    #~ M0   - Unconditional stop - Wait for user to press a button on the LCD (Only if ULTRA_LCD is enabled)
    def M0(self, P = None, S = None):
        pass
        
    #~ M1   - Same as M0
    def M1(self, P = None, S = None):
        self.M0(P, S)
        
    #~ M17  - Enable/Power all stepper motors
    def M17(self):
        code = 'M17'
        self.output.write(code)

    #~ M18  - Disable all stepper motors; same as M84
    def M18(self):
        code = 'M18'
        self.output.write(code)
            
    #~ M20  - List SD card
    #~ M21  - Init SD card
    #~ M22  - Release SD card
    #~ M23  - Select SD file (M23 filename.g)
    #~ M24  - Start/resume SD print
    #~ M25  - Pause SD print
    #~ M26  - Set SD position in bytes (M26 S12345)
    #~ M27  - Report SD print status
    #~ M28  - Start SD write (M28 filename.g)
    #~ M29  - Stop SD write
    #~ M30  - Delete file from SD (M30 filename.g)
    #~ M31  - Output time since last M109 or SD card start to serial
    #~ M32  - Select file and start SD print (Can be used _while_ printing from SD card files):
           #~ syntax "M32 /path/filename#", or "M32 S<startpos bytes> !filename#"
           #~ Call gcode file : "M32 P !filename#" and return to caller file after finishing (similar to #include).
           #~ The '#' is necessary when calling from within sd files, as it stops buffer prereading

    #~ M42  - Change pin status via gcode Use M42 Px Sy to set pin x to value y, when omitting Px the onboard led will be used.
    def M42(self, P = None, S = None):
        pass
        
    #~ M80  - Turn on Power Supply
    #~ M81  - Turn off Power Supply
    
    #~ M82  - Set E codes absolute (default)
    def M82(self):
        pass
    #~ M83  - Set E codes relative while in Absolute Coordinates (G90) mode
    #~ M84  - Disable steppers until next move,
            #~ or use S<seconds> to specify an inactivity timeout, after which the steppers will be disabled.  S0 to disable the timeout.
    #~ M85  - Set inactivity shutdown timer with parameter S<seconds>. To disable set zero (default)
    #~ M92  - Set axis_steps_per_unit - same syntax as G92
    
    #~ M104 S<temperatur> - Set extruder target temp
    def M104(self, S = None):
        pass
        
    #~ M105 - Read current temp
    def M105(self):
        pass
            
    #~ M106 S<0..255>- Fan on
    def M106(self, S = None):
        code = 'M106'
        if S != None:
            code += ' S' + str(S)

        self.output.write(code)
        
    #~ M107 - Fan off
    def M107(self):
        code = 'M107'
        self.output.write(code)
        
    #~ M109 - Sxxx Wait for extruder current temp to reach target temp. Waits only when heating
           #~ Rxxx Wait for extruder current temp to reach target temp. Waits when heating and cooling
           #~ IF AUTOTEMP is enabled, S<mintemp> B<maxtemp> F<factor>. Exit autotemp by any M109 without F
           # T<0> - Extruder number
    def M109(self, S = None, R = None, T = 0):
        pass

    #~ M114 - Output current position to serial port
    def M114(self):
        code = 'M114'
        self.output.write(code)
            
    #~ M115 - Capabilities string
    def M119(self):
        code = 'M119'
        self.output.write(code)
            
    #~ M117 - display message
    
    #~ M119 - Output Endstop status to serial port
    def M119(self):
        code = 'M119'
        self.output.write(code)
        
    #~ M126 - Solenoid Air Valve Open (BariCUDA support by jmil)
    #~ M127 - Solenoid Air Valve Closed (BariCUDA vent to atmospheric pressure by jmil)
    #~ M128 - EtoP Open (BariCUDA EtoP = electricity to air pressure transducer by jmil)
    #~ M129 - EtoP Closed (BariCUDA EtoP = electricity to air pressure transducer by jmil)
    
    #~ M140 - Set bed target temp
    def M140(self, S = None):
        pass
            
    #~ M150 - Set BlinkM Color Output R: Red<0-255> U(!): Green<0-255> B: Blue<0-255> over i2c, G for green does not work.
    def M140(self, R = None, U = None, B = None):
        pass
    
    #~ M190 - Sxxx Wait for bed current temp to reach target temp. Waits only when heating
           #~ Rxxx Wait for bed current temp to reach target temp. Waits when heating and cooling
    def M190(self, S = None, R = None):
        pass    
    
    #~ M200 D<millimeters>- set filament diameter and set E axis units to cubic millimeters (use S0 to set back to millimeters).
    #~ M201 - Set max acceleration in units/s^2 for print moves (M201 X1000 Y1000)
    #~ M202 - Set max acceleration in units/s^2 for travel moves (M202 X1000 Y1000) Unused in Marlin!!
    #~ M203 - Set maximum feedrate that your machine can sustain (M203 X200 Y200 Z300 E10000) in mm/sec
    #~ M204 - Set default acceleration: S normal moves T filament only moves (M204 S3000 T7000) in mm/sec^2  also sets minimum segment time in ms (B20000) to prevent buffer under-runs and M20 minimum feedrate
    #~ M205 -  advanced settings:  minimum travel speed S=while printing T=travel only,  B=minimum segment time X= maximum xy jerk, Z=maximum Z jerk, E=maximum E jerk
    #~ 
    #~ M206 - set additional homing offset
    #~ M207 - set retract length S[positive mm] F[feedrate mm/min] Z[additional zlift/hop], stays in mm regardless of M200 setting
    #~ M208 - set recover=unretract length S[positive mm surplus to the M207 S*] F[feedrate mm/sec]
    #~ M209 - S<1=true/0=false> enable automatic retract detect if the slicer did not support G10/11: every normal extrude-only move will be classified as retract depending on the direction.
    #~ 
    #~ M218 - set hotend offset (in mm): T<extruder_number> X<offset_on_X> Y<offset_on_Y>
    #~ M220 S<factor in percent>- set speed factor override percentage
    #~ M221 S<factor in percent>- set extrude factor override percentage
    #~ M226 P<pin number> S<pin state>- Wait until the specified pin reaches the state required
    #~ M240 - Trigger a camera to take a photograph
    #~ M250 - Set LCD contrast C<contrast value> (value 0..63)
    #~ M280 - set servo position absolute. P: servo index, S: angle or microseconds
    
    #~ M300 - Play beep sound S<frequency Hz> P<duration ms>
    def M300(self):
        code = 'M300'
        self.output.write(code)
    
    #~ M301 - Set PID parameters P I and D
    #~ M302 - Allow cold extrudes, or set the minimum extrude S<temperature>.
    #~ M303 - PID relay autotune S<temperature> sets the target temperature. (default target temperature = 150C)
    #~ M304 - Set bed PID parameters P I and D
    
    #~ M400 - Finish all moves
    def M400(self):
        code = 'M400'
        self.output.write(code)

    #~ M401 - Lower z-probe if present
    def M401(self):
        code = 'M401'
        self.output.write(code)
        
    #~ M402 - Raise z-probe if present
    def M402(self):
        code = 'M402'
        self.output.write(code)

    #~ M500 - stores parameters in EEPROM
    #~ M501 - reads parameters from EEPROM (if you need reset them after you changed them temporarily).
    #~ M502 - reverts to the default "factory settings".  You still need to store them in EEPROM afterwards if you want to.
    #~ M503 - print the current settings (from memory not from EEPROM)
    #~ M540 - Use S[0|1] to enable or disable the stop SD card print on endstop hit (requires ABORT_ON_ENDSTOP_HIT_FEATURE_ENABLED)
    #~ M600 - Pause for filament change X[pos] Y[pos] Z[relative lift] E[initial retract] L[later retract distance for removal]
    #~ M665 - set delta configurations
    #~ M666 - set delta endstop adjustment
    #~ M605 - Set dual x-carriage movement mode: S<mode> [ X<duplication x-offset> R<duplication temp offset> ]
    #~ M907 - Set digital trimpot motor current using axis codes.
    #~ M908 - Control digital trimpot directly.
    #~ M350 - Set microstepping mode.
    #~ M351 - Toggle MS1 MS2 pins directly.
    
    #~ M928 - Start SD logging (M928 filename.g) - ended by M29
    
    #~ M999 - Restart after being stopped by error
    def M999(self):
        code = 'M999'
        self.output.write(code)
    #~ 
     #~ FABtotum custom M code
    #~ 
    #~ M3 S[RPM] SPINDLE ON - Clockwise , tries to mantain RPM costant min: 6500, max: 15000
    def M3(self, S):
        code = 'M3'
        # TODO: raise Exception if out of range
        if S != None:
            code += ' S' + str(S)
        self.output.write(code)

    #~ M4 S[RPM] SPINDLE ON - CounterClockwise, tries to mantain RPM costant min: 6500, max: 15000
    def M4(self, S):
        code = 'M4'
        # TODO: raise Exception if out of range
        if S != None:
            code += ' S' + str(S)
        self.output.write(code)
        
    #~ M5        SPINDLE OFF
    def M5(self):
        code = 'M5'
        self.output.write(code)
        
    #~ M700 S<0-255> - Laser Power Control
    def M700(self, S):
        code = 'M700'
        # TODO: raise Exception if out of range
        if S != None:
            code += ' S' + str(S)
        self.output.write(code)
        
    #~ M701 S<0-255> - Ambient Light, Set Red
    def M701(self, S):
        code = 'M701'
        # TODO: raise Exception if out of range
        if S != None:
            code += ' S' + str(S)
        self.output.write(code)
            
    #~ M702 S<0-255> - Ambient Light, Set Green
    def M702(self, S):
        code = 'M702'
        # TODO: raise Exception if out of range
        if S != None:
            code += ' S' + str(S)
        self.output.write(code)
        
    #~ M703 S<0-255> - Ambient Light, Set Blue
    def M703(self, S):
        code = 'M703'
        # TODO: raise Exception if out of range
        if S != None:
            code += ' S' + str(S)
        self.output.write(code)
        
    #~ M704 - Signalling Light ON (same colors of Ambient Light)
    def M704(self):
        code = 'M704'
        self.output.write(code)
        
    #~ M705 - Signalling Light OFF
    def M705(self):
        code = 'M704'
        self.output.write(code)
        
    #~ M706 S<0-255> - Head Light
    def M706(self, S):
        code = 'M706'
        # TODO: raise Exception if out of range
        if S != None:
            code += ' S' + str(S)
        self.output.write(code)
        
    #~ M710 S<VAL> - write and store in eeprom calibrated z_probe offset length
    #~ M711 - write and store in eeprom calibrated zprobe extended angle
    #~ M712 - write and store in eeprom calibrated zprobe retacted angle
    #~ M713 - autocalibration of z-probe length and store in eeprom
    #~ M720 - 24VDC head power ON
    #~ M721 - 24VDC head power OFF
    #~ M722 - 5VDC SERVO_1 power ON
    #~ M723 - 5VDC SERVO_1 power OFF
    #~ M724 - 5VDC SERVO_2 power ON
    #~ M725 - 5VDC SERVO_2 power OFF
    #~ M726 - 5VDC RASPBERRY PI power ON
    #~ M727 - 5VDC RASPBERRY PI power OFF
    #~ M728 - RASPBERRY Alive/awake Command
    #~ M729 - RASPBERRY Sleep                    //wait for the complete shutdown of raspberryPI
    #~ M730 - Read last error code
    #~ M731 - Disable kill on Door Open
    #~ M740 - read WIRE_END sensor
    #~ M741 - read DOOR_OPEN sensor
    #~ M742 - read REEL_LENS_OPEN sensor
    #~ M743 - read SECURE_SWITCH sensor
    #~ M744 - read HOT_BED placed in place
    #~ M745 - read Head placed in place
    
    # M746 - turn off or on external z probing (S0= disable , S1 enable, Default: show setting status)
    def M746(self, S = None):
        code = 'M746'
        # TODO: raise Exception if out of range
        if S != None:
            code += ' S' + str(S)
        self.output.write(code)
        
    #~ 
    #~ M750 - read PRESSURE sensor (ANALOG 0-1023)
    #~ M751 - read voltage monitor 24VDC input supply (ANALOG V)
    #~ M752 - read voltage monitor 5VDC input supply (ANALOG V)
    #~ M753 - read current monitor input supply (ANALOG A)
    #~ M754 - read tempearture raw values (10bit ADC output)
    #~ M760 - read FABtotum Personal Fabricator Main Controller serial ID
    #~ M761 - read FABtotum Personal Fabricator Main Controller control code of serial ID
    #~ M762 - read FABtotum Personal Fabricator Main Controller board version number
    #~ M763 - read FABtotum Personal Fabricator Main Controller production batch number
    #~ M764 - read FABtotum Personal Fabricator Main Controller control code of production batch number
    #~ M765 - read FABtotum Personal Fabricator Firmware Version
    #~ M766 - read FABtotum Personal Fabricator Firmware Build Date and Time
    #~ M767 - read FABtotum Personal Fabricator Firmware Update Author
    #~ 
    #~ M780 - read Head Product Name
    #~ M781 - read Head Vendor Name
    #~ M782 - read Head product ID
    #~ 
    #~ M783 - read Head vendor ID
    #~ M784 - read Head Serial ID
    #~ M785 - read Head firmware version
    #~ M786 - read needed firmware version of FABtotum Personal Fabricator Main Controller
    #~ M787 - read Head capability: type0 (passive, active)
    #~ M788 - read Head capability: type1 (additive, milling, syringe, laser etc..)
    #~ M789 - read Head capability: purpose (single purpose, multipurpose)
    #~ M790 - read Head capability: wattage (0-200W)
    #~ M791 - read Head capability: axis (number of axis)
    #~ M792 - read Head capability: servo (number of axis)
