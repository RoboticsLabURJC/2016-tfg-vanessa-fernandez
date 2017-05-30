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
        

class MyAlgorithm(threading.Thread):

    def __init__(self, pose3d, motors, laser, bumper):
        self.pose3d = pose3d
        self.motors = motors
        self.laser = laser
        self.bumper = bumper
        self.grid = np.empty([300,300],float)
        self.radiusInitial = 0.1
        self.constant = 0.01
        self.numCrash = 0
        self.turn = False
        self.yaw = 0


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

    def execute(self):

        print ('Execute')
        # TODO

        # Devuelve 1 si choca y 0 si no choca
        crash = self.bumper.getBumperData().state

        if crash == 1:
            self.numCrash = 1

        print(self.numCrash)
        self.yaw = self.pose3d.getYaw()

        if self.numCrash == 0:
            self.motors.sendW(0.5)
            self.motors.sendV(self.radiusInitial*self.constant)
            self.constant += 0.012
        else:
            numAngle = random.random() * pi
            print("angle random", numAngle)
            while self.turn == False and crash == 1:
                angle = abs(self.yaw - self.pose3d.getYaw())
                print("giro hecho ",angle)
                if angle <= (numAngle-0.1) or angle >= (numAngle+0.1):
                    print("ENTRAAAANDOOOOOOOO!!")
                    self.motors.sendW(numAngle)
                    self.motors.sendV(0)
                else:
                    self.turn = True
            self.turn = False
            self.motors.sendV(0.5)
            self.motors.sendW(0)
            

        # www.sr.echu.es/sbweb/fisica/celeste/espiral/espiral.html
        # proyectodescartes.org/descartescms/blog/itemlist/tag/espirales
        # http://www2.famaf.unc.edu.ar/rev_edu/documents/vol_23/prop_11_La_espiral_de_Arquimedes.pdf
        
