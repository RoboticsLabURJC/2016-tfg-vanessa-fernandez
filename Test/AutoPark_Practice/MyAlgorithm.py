import numpy as np
import threading
import time
from datetime import datetime
import jderobot
import math
import cv2
from ompl import base as ob
from ompl import geometric as og
from ompl import control as oc
from ompl import app as oa

from math import pi as pi

time_cycle = 80


class MyAlgorithm(threading.Thread):

    def __init__(self, pose3d, laser1, laser2, laser3, motors):
        self.pose3d = pose3d
        self.laser1 = laser1
        self.laser2 = laser2
        self.laser3 = laser3
        self.motors = motors
        
        self.path = 0
        
        self.THX = 0.1
        self.THY = 0.1
        self.THYAW = 0.01

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
            # (4.2.1) laser into GUI reference system
            x = d * math.cos(a) * -1
            y = d * math.sin(a) * -1
            v = (x,y)
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

    def absolutas2relativas(self, x, y, rx, ry, rt):
        # Convert to relatives
        dx = x - rx
        dy = y - ry

        # Rotate with current angle
        x = dx*math.cos(-rt) - dy*math.sin(-rt)
        y = dx*math.sin(-rt) + dy*math.cos(-rt)

        return x,y

    def setPose(self, x, y, rot):
        state = ob.State(ob.SE2StateSpace())
        state().setX(x)
        state().setY(y)
        state().setYaw(rot * pi / 180)
        return state


    def configPlan(self):
        # Type of robot
        robotType = 'GKinematicCarPlanning'
        omplSetup = eval('oa.%s()' % robotType)
        
        # Open environment
        environmentFile = "/home/vanejessi/Escritorio/Vanessa/2016-tfg-vanessa-fernandez/Test/AutoPark_Practice/omplAutopark/autopark_sin_taxi3.dae"
        omplSetup.setEnvironmentMesh(environmentFile)
        
        # Open robot
        robotFile = "/home/vanejessi/Escritorio/Vanessa/2016-tfg-vanessa-fernandez/Test/AutoPark_Practice/omplAutopark/taxicopia.dae"
        omplSetup.setRobotMesh(robotFile)
        omplSetup.inferEnvironmentBounds()
        
        # Start and goal
        startPose = self.setPose(-7, 2.5, 0)
        goalPose = self.setPose(7, -2.5, 0)
        
        # set the start & goal states
        omplSetup.setStartAndGoalStates(startPose, goalPose, .1)

        # set the planner
        planner = oc.RRT(omplSetup.getSpaceInformation())
        omplSetup.setPlanner(planner)

        # try to solve the problem
        if omplSetup.solve(20):
            # print the (approximate) solution path: print states along the path
            # and controls required to get from one state to the next
            path = omplSetup.getSolutionPath().asGeometric()
            #path.interpolate(); # uncomment if you want to plot the path
            if not omplSetup.haveExactSolutionPath():
                print("Solution is approximate. Distance to actual goal is %g" %
                    omplSetup.getProblemDefinition().getSolutionDifference())
                    
        return path.printAsMatrix()
      
        
    def parsePath(self):
        path = []
        if self.path == 0:
            self.path = self.configPlan()
            self.path = self.path.split("\n")
            for target in self.path:
                if target != "":
                    targetSplit = target.split(" ")
                    tuplaTarget =(float(targetSplit[0]), float(targetSplit[1]), float(targetSplit[2]))
                    path.append(tuplaTarget)            
        return path
        
        
    def getTarget(self):
        if len(self.path) != 0:
            nextTarget = self.path[0]
        else:
            nextTarget = None
        return nextTarget
        
        
    def goTarget(self,target):
        xTar = target[0]
        yTar = target[1]
        yawTar = target[2]
        
        xCar = self.pose3d.getX()
        yCar = self.pose3d.getY()
        yawCar = self.pose3d.getYaw()
        
        difXCar, difYCar = self.absolutas2relativas(xTar,yTar,xCar,yCar,yawCar)
        angle = math.atan((difYCar/difXCar))
        print("angle", angle)
        
        self.motors.sendV(50)
        if angle >= 0.1:
           self.motors.sendW(0.2)
        
    def checkTarget(self, target):
        difX = abs(target[0] - self.pose3d.getX())
        difY = abs(target[1] - self.pose3d.getY())
        difYaw = abs(target[2] - self.pose3d.getYaw())
        
        if difX  <= self.THX and difY <= self.THY and difYaw <= self.THYAW:
            # Si cumple las restricciones, ha llegao al objetivo
            return True
        else:
            return False
            
         
    def execute(self):

        # TODO      
       
        if self.path == 0:
            self.path = self.parsePath()
        else:
            target = self.getTarget()
            if self.checkTarget(target):
                # Si ha llegado al objetivo lo elimino del camino
                self.path.pop(0)
            else: 
                self.goTarget(target)

