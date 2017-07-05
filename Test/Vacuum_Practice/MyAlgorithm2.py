import numpy as np
import threading
import time
from datetime import datetime
import jderobot
import math
import cv2
from math import pi as pi
import random

time_cycle = 80
        

class MyAlgorithm2(threading.Thread):

    def __init__(self, pose3d, motors, laser, bumper):
        self.pose3d = pose3d
        self.motors = motors
        self.laser = laser
        self.bumper = bumper
        
        self.map = cv2.imread("resources/images/mapgrannyannie.png", cv2.IMREAD_GRAYSCALE)
        self.map = cv2.resize(self.map, (500, 500))
        
        self.grid = np.ones([500, 500], float)
        
        #self.numCrash = 0
        self.yaw = 0
        self.turn = False
        self.turnFound = True
        self.crash = False
        self.horizontal = True
        self.numIteracion = 0
        self.time = 0

        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)

    
    def parse_laser_data(self,laser_data):
        laser = []
        for i in range(laser_data.numLaser):
            dist = laser_data.distanceData[i]/1000.0
            angle = math.radians(i)
            laser += [(dist, angle)]
        return laser
    
    def laser_vector(self,laser_array):
        laser_vectorized = []
        for d,a in laser_array:
            x = d * math.cos(a) * -1
            y = d * math.sin(a) * -1 
            v = (x, y)
            laser_vectorized += [v]
        return laser_vectorized
        
        
    def RTy(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), 0, math.sin(angle), tx], [0, 1, 0, ty], [-math.sin(angle), 0, math.cos(angle), tz], [0,0,0,1]])
        return RT

    def RTVacuum(self):
        RTy = self.RTy(pi, 5.6, 4, 0)
        return RTy
        
    def reduceValueSquare(self, numRow, numColumn):
        scale = 50
        for i in range((numColumn * scale), (numColumn*scale + scale)):
            for i in range((numRow * scale), (numRow*scale + scale)):
                if self.grid[numColumn][numRow] != 0:
                    self.grid[numColumn][numRow] = self.grid[numColumn][numRow] - 1
        
    def reduceValueTime(self):
        # number of rows is 10 and number of columns is 10
        numRowsColumns = 10
        for i in range(0, numRowsColumns):
            for j in range(0, numRowsColumns):
                self.reduceValueSquare(i, j)
            
        
    def changeValuesGrid(self):
        x = self.pose3d.getX()
        y = self.pose3d.getY()
        scale = 50

        final_poses = self.RTVacuum() * np.matrix([[x], [y], [1], [1]]) * scale
        self.grid[int(final_poses.flat[0])][int(final_poses.flat[1])] = 0
        print final_poses.flat[0], final_poses.flat[1]
        numX = int(final_poses.flat[0] / scale)
        numY = int(final_poses.flat[1] / scale)
        
        for i in range((numX * scale), (numX*scale + scale)):
            for j in range((numY * scale), (numY*scale + scale)):
                self.grid[j][i] = self.grid[j][i] + 10.0
        
        
    def showGrid(self):
		maxVal = np.amax(self.grid)
		if maxVal != 0:
			nCopy = np.dot(self.grid, (1/maxVal))
		else:
			 nCopy = self.grid
		cv2.imshow("Grid ", nCopy)
		

    def run (self):
        while (not self.kill_event.is_set()):
           
            start_time = datetime.now()

            if not self.stop_event.is_set():
                self.execute()

            finish_Time = datetime.now()


            dt = finish_Time - start_time
            ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
            #print (ms)
            if (ms < time_cycle):
                time.sleep((time_cycle - ms) / 1000.0)

    def stop (self):
        self.stop_event.set()

    def play (self):
        if self.is_alive():
            self.stop_event.clear()
        else:
            self.start()

    def kill (self):
        self.kill_event.set()
        
        
    def checkCrash(self):
        for i in range(0, 350):
            # Returns 1 if it collides, and 0 if it doesn't collide
            crash = self.bumper.getBumperData().state
            if crash == 1:
                self.motors.sendW(0)
                self.motors.sendV(0)
                break
        return crash
        

    def turn90(self, angle1, angle2, yawNow):
        turn = True
        if (-0.4 <= self.yaw <= 0.4 or (-pi/2-0.4) <= self.yaw <= (-pi/2+0.4)) and (yawNow <= (angle1-0.115) or yawNow >= (angle1+0.115)):
            self.motors.sendV(0)
            self.motors.sendW(0.2)
        elif ((pi/2-0.4) <= self.yaw <= (pi/2+0.4) or (-pi+0.4) >= self.yaw or self.yaw >= (pi - 0.4)) and (yawNow <= (angle2-0.115) or yawNow >= (angle2+0.115)):
            self.motors.sendV(0)
            self.motors.sendW(-0.2)
        else:
            turn = False
        return turn
        

    def execute(self):

        print ('Execute')
        # TODO
        # Map is self.map
        #cv2.imshow('map',self.map)
        
        # Time
        self.numIteracion = self.numIteracion + 1
        if self.numIteracion % 5 == 0:
            self.time = self.time + 1
        
        if self.time % 5 == 0:
            # If 5 seconds have elapsed we reduce the value of the squares of the grid
            self.reduceValueTime()
        
        # Show grid
        self.changeValuesGrid()
        self.showGrid()
                
        # Vacuum's poses
        x = self.pose3d.getX()
        y = self.pose3d.getY()
        yaw = self.pose3d.getYaw()
        
        # Check crash
        crash = self.checkCrash()
        
        print (crash)
        
        if crash == 1:
            print "CRAAASH"
            # Stop
            self.motors.sendW(0)
            self.motors.sendV(0)
            time.sleep(1)
            # Go backwards
            self.motors.sendV(-0.1)
            time.sleep(1)
            
            # Yaw 
            self.yaw = self.pose3d.getYaw()
            self.turn = False
            self.crash = True
            
        if self.turn == False and self.crash == True:
            print "PRIMER GIRO"
            # Yaw
            yawNow = self.pose3d.getYaw()
            # Turn 90
            giro = self.turn90(pi/2, pi/2, yawNow)
                
            if giro == False:
                print "GIRO HECHO"
                self.turn = True
                # Go backwards
                self.motors.sendW(0)
                time.sleep(2)
                self.motors.sendV(0.32)                                        
                time.sleep(1)
                self.turnFound = False
                
                
        elif self.turnFound == False and self.crash == True:
            print "SEGUNDO GIRO"
            # Yaw
            yawNow = self.pose3d.getYaw()
            giro = self.turn90(pi, 0, yawNow)
            
            if giro == False:
                self.turnFound = True
        
        else:
            print "AVANZAR"
            # Go forward
            self.motors.sendW(0.0)
            time.sleep(1)
            self.motors.sendV(0.5)
            self.crash = False
            self.turn == True
            
            


'''
        print ('Execute')
        # TODO
        # Map is self.map
        #cv2.imshow('map',self.map)
                
        # Vacuum's poses
        x = self.pose3d.getX()
        y = self.pose3d.getY()
        yaw = self.pose3d.getYaw()
        
        for i in range(0, 350):
            # Devuelve 1 si choca y 0 si no choca
            crash = self.bumper.getBumperData().state
            if crash == 1:
                self.motors.sendW(0)
                self.motors.sendV(0)
                break
                
        print(crash)
        
        turn = False
        
        if crash == 1:
            self.numCrash = self.numCrash + 1
            
            self.motors.sendW(0)
            self.motors.sendV(0)
            time.sleep(1)
            self.motors.sendV(-0.1)
            time.sleep(1)
            
            while turn == False:
                yawNow = self.pose3d.getYaw()
                if self.horizontal == True:                    
                    giro = self.turn90(pi/2, pi/2, yawNow)
                else:
                    giro = self.turn90(0, 0, yawNow)
                
                if giro == False:
                    self.motors.sendW(0)
                    time.sleep(2)
                    self.motors.sendV(0.32)
                    #newCrash = self.bumper.getBumperData().state
                    for i in range(0, 350):
                        # Devuelve 1 si choca y 0 si no choca
                        newCrash = self.bumper.getBumperData().state
                        if newCrash == 1:
                            self.motors.sendW(0)
                            self.motors.sendV(0)
                            break
                    print "newCrash", newCrash
                    if newCrash == 1 and self.horizontal == True:
                        # No se puede avanzar en horizontal
                        self.horizontal = False
                        self.motors.sendW(0)
                        self.motors.sendV(0)
                        time.sleep(1)
                        self.motors.sendV(-0.1)
                        time.sleep(1)
                        print "choque horizontal"
                    elif newCrash == 1 and self.horizontal == False:
                        self.horizontal == True
                        self.motors.sendW(0)
                        self.motors.sendV(0)
                        time.sleep(1)
                        self.motors.sendV(-0.1)
                        time.sleep(1)
                        print "choque vertical"
                    else:
                        time.sleep(1)
                        yaw = self.pose3d.getYaw()
                        
                        while turn == False:
                            yawNow = self.pose3d.getYaw()
                            if self.horizontal == True:
                                giro = self.turn90(pi, 0, yawNow)
                            else:
                                giro = self.turn90(-pi/2, pi/2, yawNow)
                                
                            if giro == False:
                                turn = True
        else:
            self.motors.sendW(0.0)
            time.sleep(1)
            self.motors.sendV(0.5)
        
        '''
