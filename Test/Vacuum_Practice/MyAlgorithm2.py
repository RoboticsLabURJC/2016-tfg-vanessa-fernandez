#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        
        self.orientation = 'left'
        
        self.secondTurn = True
        self.horizontal = True
        self.crash = False
        self.firstTurn = False
        self.crashObstacle = False
        self.saturation = False
        self.obstacleRight = False
        self.noObstRight = False
        self.corner = False
        self.sizeVacuum = False
        
        self.startTime = 0
        self.time = 0
        self.timeSat = 0
        self.yaw = 0
        self.numIteracion = 0
        self.DIST_TO_OBST_RIGHT = 30
        self.DIST_MIN_TO_OBST_RIGHT = 15
        self.DIST_TO_OBST_FRONT = 15

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
        
        
    def RTy(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), 0, math.sin(angle), tx], [0, 1, 0, ty], [-math.sin(angle), 0, math.cos(angle), tz], [0,0,0,1]])
        return RT

    def RTVacuum(self):
        RTy = self.RTy(pi, 5.6, 4, 0)
        return RTy
        
    def reduceValueSquare(self, numRow, numColumn):
        # Reduce the value of a particular square
        scale = 50
        for i in range((numColumn * scale), (numColumn*scale + scale)):
            for j in range((numRow * scale), (numRow*scale + scale)):
                if self.grid[i][j] != 0:
                    self.grid[i][j] = self.grid[i][j] - 1
        
    def reduceValueTime(self):
        # Number of rows is 10 and number of columns is 10
        numRowsColumns = 10
        # Scrolls the entire image
        for i in range(0, numRowsColumns):
            for j in range(0, numRowsColumns):
                self.reduceValueSquare(i, j)
            
        
    def changeValuesGrid(self):
        # Change the value of the grid depending on where the vacuum goes
        x = self.pose3d.getX()
        y = self.pose3d.getY()
        scale = 50

        final_poses = self.RTVacuum() * np.matrix([[x], [y], [1], [1]]) * scale

        # Grid 500 x 500 and we want a grid of 10 x 10
        # We keep the whole section of the division to know in which square this is
        numX = int(final_poses.flat[0] / scale)
        numY = int(final_poses.flat[1] / scale)
        
        for i in range((numX * scale), (numX*scale + scale)):
            for j in range((numY * scale), (numY*scale + scale)):
                self.grid[j][i] = self.grid[j][i] + 10.0
        
        
    def showGrid(self):
        # To show the grid well
        # Maximum value of the pixels
		maxVal = np.amax(self.grid)
		if maxVal != 0:
		    # Saves a copy of the image but divided by the maximum value so that it is not saturated
			nCopy = np.dot(self.grid, (1/maxVal))
		else:
			 nCopy = self.grid
		cv2.imshow("Grid ", nCopy)
		
		
    def checkSaturation(self):
        saturation = False
        numRowsColumns = 10
        scale = 50
        numSquaresVisited = 0
        for i in range(0, numRowsColumns):
            for j in range(0, numRowsColumns):
                # I check the first pixel of the square because they all have the same value
                valuePos = self.grid[j*scale][i*scale]
                if valuePos != 0:
                    numSquaresVisited = numSquaresVisited + 1
                    
        if numSquaresVisited < 3:
            saturation = True
        return saturation
        
        
    def checkCrash(self):
        for i in range(0, 350):
            # Returns 1 if it collides, and 0 if it doesn't collide
            crash = self.bumper.getBumperData().state
            if crash == 1:
                self.motors.sendW(0)
                self.motors.sendV(0)
                break
        return crash
        
        
    def returnOrientation(self, yaw):
        if -pi/2 <= yaw <= pi/2:
            orientation = 'left'
        elif pi/2 <= yaw <= pi or -pi <= yaw <= -pi/2:
            orientation = 'right'
        return orientation
        
    def turn90(self, angle1, angle2, yawNow):
        # angle1: orientacion a la que tiene que llegar si la orientacion es izq
        # angle2: orientacion a la que tiene que llegar si la orientacion es derecha
        turn = True
        rangeDegrees = 0.125
        
        if angle1 == pi or angle2 == 0:
            rangeDegrees = 0.145
            
        if angle2 == pi and yawNow < 0:
            angle2 = -angle2
            
        if (self.orientation == 'left') and (yawNow <= (angle1-rangeDegrees) or yawNow >= (angle1+rangeDegrees)):
            # Look left and turn left
            self.motors.sendV(0)
            self.motors.sendW(0.2)
        elif (self.orientation == 'right') and (yawNow <= (angle2-rangeDegrees) or yawNow >= (angle2+rangeDegrees)):
            # Look right and turn right
            self.motors.sendV(0)
            self.motors.sendW(-0.2)
        else:
            turn = False
        return turn
        
    def calculateSideTriangle(self, a, b, angle):
        c = math.sqrt(pow(a,2) + pow(b,2) - 2*a*b*math.cos(angle))
        return c
        
    def calculateAngleTriangle(self, a, b, c):
        numer = pow(a,2) + pow(b,2) - pow(c,2)
        deno = 2 * a * b
        angleC = math.acos(numer/deno)
        return angleC

    def execute(self):

        print ('Execute')
        # TODO

        # Time     
        if self.time == 0:
            self.time = time.time()
        if self.timeSat == 0:
            self.timeSat = time.time()
            
        timeNow = time.time()
        if self.saturation == False:
            #print('TIME', abs(self.time - timeNow))
            #print('TIME SATURATION', abs(self.timeSat - timeNow))
            
            if abs(self.time - timeNow) >= 5:
                # If 5 seconds have elapsed we reduce the value of the squares of the grid
                #print ('REDUCIR VALORES DEL GRID')
                self.reduceValueTime()
                self.time = 0
                
            if abs(self.timeSat - timeNow) >= 20:
                self.saturation = self.checkSaturation()
                if self.saturation == True:
                    # Stop
                    self.motors.sendW(0)
                    self.motors.sendV(0)
                self.timeSat = 0
            
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
        self.saturation = True
        
        if self.saturation == False:
            if crash == 1:
                print ("CRAAASH")
                # Stop
                self.motors.sendW(0)
                self.motors.sendV(0)
                time.sleep(1)
                # Go backwards
                self.motors.sendV(-0.1)
                time.sleep(1)
                
                # Yaw 
                self.yaw = self.pose3d.getYaw()
                self.firstTurn = False
                self.crash = True
                
            if self.firstTurn == False and self.crash == True:
                print ("PRIMER GIRO")
                # Yaw
                yawNow = self.pose3d.getYaw()
                # Orientation
                self.orientation = self.returnOrientation(self.yaw)
                # Turn 90
                giro = self.turn90(pi/2, pi/2, yawNow)
                    
                if giro == False:
                    print ("GIRO HECHO")
                    self.firstTurn = True
                    # Go forwards
                    self.motors.sendW(0)
                    time.sleep(2)
                    self.motors.sendV(0.22)                                        
                    time.sleep(1)
                    self.secondTurn = False
                    
                    
            elif self.secondTurn == False and self.crash == True:
                print ("SEGUNDO GIRO")
                # Yaw
                yawNow = self.pose3d.getYaw()
                giro = self.turn90(pi, 0, yawNow)
                
                if giro == False:
                    self.secondTurn = True
            
            else:
                print ("AVANZAR")
                # Go forward
                self.motors.sendW(0.0)
                time.sleep(1)
                self.motors.sendV(0.5)
                self.crash = False
                self.firstTurn = True
                
        else:
            # There is saturation
            print ("RECORRER PERIMETRO")
            
            # Get the data of the laser sensor, which consists of 180 pairs of values
            laser_data = self.laser.getLaserData()
            
            # Distance in millimeters, we change to cm
            laserRight = laser_data.distanceData[0]/10
            laserCenter = laser_data.distanceData[90]/10
            laser45 = laser_data.distanceData[45]/10
            
            # Calculate the angle of triangle
            a = self.calculateSideTriangle(laserRight, laser45, 45)
            angleC = self.calculateAngleTriangle(a, laserRight, laser45)
            
            # Initialize start time
            if self.startTime == 0:
                self.startTime = time.time()
            timeNow = time.time()
            
            # Only walks the wall for a while
            if self.startTime - timeNow < 60:
                if crash == 0 and self.crashObstacle == False:             
                    # I go forward until I find an obstacle
                    self.motors.sendV(0.5)
                    print("SOLO AVANZO POR NO CRASH")
                elif crash == 1 and self.crashObstacle == False:
                    self.crashObstacle = True
                    print("NUEVO CRASH")
                    # Stop
                    self.motors.sendW(0)
                    self.motors.sendV(0)    
                    time.sleep(1)
                    # Go backwards
                    self.motors.sendV(-0.1)
                    time.sleep(1)
                    print("HACIA ATRAS ")
                    
                    
                if self.crashObstacle == True:
                    print laserRight
                    # Turn until the obstacle is to the right
                    #if laserRight > distToObstacleRight and self.obstacleRight == False:
                    if (angleC >= pi/2 + 0.1 or angleC <= pi/2 - 0.1) and self.obstacleRight == False:
                        self.motors.sendV(0)
                        self.motors.sendW(0.2)
                        print("GIRO HASTA QUE ESTE LA PARED A LA DERECHA")
                    else:
                        self.obstacleRight = True
                        self.motors.sendW(0)
                        
                    if self.obstacleRight == True:
                        # The obstacle is on the right
                        
                        if laserCenter < self.DIST_TO_OBST_FRONT or self.corner == True:
                            # Está en una esquina
                            print (' ESTOY EN UNA ESQUINA ')
                            self.corner = True
                            
                            # Stop
                            self.motors.sendV(0)
                            
                            # Gira 90 grados a la izq
                            if self.yaw <= (pi + 0.2) and self.yaw >= (pi - 0.2):
                                self.yaw = -pi

                            # Gira 90 grados a la izq
                            self.orientation = 'left'
                            giro = self.turn90(self.yaw + pi/2, pi/2, yaw)
                            print('Girando a la izquierda...')
                            if giro == False:
                                self.motors.sendW(0)
                                self.corner = False
                                print('GIRO A LA IZQUIERDA HECHO')

                        else:
                            # Avanza
                            #if laserRight >= self.DIST_TO_OBST_RIGHT:
                            if laserRight <= self.DIST_MIN_TO_OBST_RIGHT:
                                print('Girooo')
                                self.motors.sendV(0)
                                self.motors.sendW(0.1)
                            elif laserRight >= self.DIST_TO_OBST_RIGHT:
                                # Giro
                                print('Girando...')
                                self.motors.sendV(0) 
                                self.motors.sendW(-0.1)
                            else:
                                print (' Avanzando... ')
                                self.motors.sendW(0)
                                self.motors.sendV(0.1)
                            self.yaw = yaw
                        
            else:
                # Restart all global variables
                self.startTime = 0
                self.crashObstacle = False
                self.obstacleRight = False
                self.noObstRight = False
                self.corner = False
                self.sizeVacuum = False


