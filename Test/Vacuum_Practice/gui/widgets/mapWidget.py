#
#  Copyright (C) 1997-2016 JDE Developers Team
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/.
#  Authors :
#       Irene Lope Rodríguez<irene.lope236@gmail.com>
#       Vanessa Fernández Matínez<vanessa_1895@msn.com>


#import resources_rc
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtGui import QPen, QPainter
from PyQt5.QtCore import QPoint, QPointF, pyqtSignal, Qt
import numpy as np
import math
from math import pi as pi

class MapWidget(QWidget):

    stopSIG=pyqtSignal()
    
    def __init__(self,winParent):    
        super(MapWidget, self).__init__()
        self.winParent=winParent
        self.initUI()
        self.scale = 15.0
        self.laser = []
        
    
    def initUI(self):
        layout=QGridLayout() 
        self.setLayout(layout)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.resize(300,300)
        self.setMinimumSize(500,500)
        
    
    def paintEvent(self, e):
        _width = self.width()
        _height = self.height()
    
        painter=QPainter(self)
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
    
        #Widget center
        painter.translate(QPoint(_width/2, _height/2))

        # Draw laser
        self.drawLaser(1, painter, Qt.blue, self.laser)

        # Draw vacuum
        self.drawVacuum(painter)

        # Draw obstacles
        self.drawObstacles(painter)

        # Draw axis
        self.drawAxis(painter)


    def drawAxis(self, painter):
        pi = math.pi
        RTx = self.RTx(pi, 0, 0, 0)
        RTz = self.RTz(pi/2, 0, 0, 0)
        RT1 = np.matrix([[0],[0],[0],[1]])
        RT2 = np.matrix([[200],[0],[0],[1]])
        RT3 = np.matrix([[0],[200],[0],[1]])
        
        RT4 = RTx  * RTz * RT1
        RT5 = RTx  * RTz * RT2
        RT6 = RTx  * RTz * RT3
        
        pen = QPen(Qt.red, 2)
        painter.setPen(pen)
        painter.drawLine(QPointF(RT4.flat[0],RT4.flat[1]),QPointF(RT5.flat[0],RT5.flat[1]))
        pen = QPen(Qt.green, 2)
        painter.setPen(pen)
        painter.drawLine(QPointF(RT4.flat[0],RT4.flat[1]),QPointF(RT6.flat[0],RT6.flat[1]))


    def drawVacuum(self, painter):
        pose = self.winParent.getPose3D()
        x = pose.getX()
        y = pose.getY()
        yaw = pose.getYaw()

        orig_poses = np.matrix([[x], [y], [1], [1]]) * self.scale
        final_poses = self.RTVacuum() * orig_poses

        carsize = 30
        painter.translate(QPoint(final_poses[0],final_poses[1]))
        painter.rotate(-180*yaw/pi)
        
        # Chassis
        #painter.fillRect(-carsize/2, -carsize,carsize,2*carsize,Qt.yellow)
        painter.drawEllipse (0, 0, carsize/2, carsize/2)

        # Tires
        #painter.fillRect(-carsize/2,-carsize,carsize/5,2*carsize/5,Qt.black)
        #painter.fillRect(carsize/2,-carsize,-carsize/5,2*carsize/5,Qt.black)
        #painter.fillRect(-carsize/2,carsize-2*carsize/5,carsize/5,2*carsize/5,Qt.black)
        #painter.fillRect(carsize/2,carsize-2*carsize/5,-carsize/5,2*carsize/5,Qt.black)
    
    
    def RTx(self, angle, tx, ty, tz):
        RT = np.matrix([[1, 0, 0, tx], [0, math.cos(angle), -math.sin(angle), ty], [0, math.sin(angle), math.cos(angle), tz], [0,0,0,1]])
        return RT
        
    
    def RTy(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), 0, math.sin(angle), tx], [0, 1, 0, ty], [-math.sin(angle), 0, math.cos(angle), tz], [0,0,0,1]])
        return RT
    
    
    def RTz(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), -math.sin(angle), 0, tx], [math.sin(angle), math.cos(angle),0, ty], [0, 0, 1, tz], [0,0,0,1]])
        return RT   

    
    def RTLaser(self, num):
        if num == 1:
            #Rotación en Z / Traslación en X
            RT = self.RTz(0, 2.79, 0, 0)
        elif num == 2:
            #Rotación en Z / Traslación en X
            RT = self.RTz(pi, -2.79, 0, 0)
        else:
            #Rotación en Z / Traslación en Y
            RT = self.RTz(pi/2, 0, 1.5, 0)
        return RT    
    
    
    def coordLaser(self, dist, angle):
        coord = [0,0] 
        coord[0] = dist * math.cos(angle)
        coord[1] = dist * math.sin(angle)
        return coord

    
    def RTVacuum(self):
        RTx = self.RTx(pi, 0, 0, 0)
        RTz = self.RTz(pi/2, 0, 0, 0)
        return RTx*RTz

    
    def drawLaser(self, num, painter, color, laser):
        pen = QPen(color, 2)
        painter.setPen(pen)
        RT = self.RTLaser(num)
        RTOrigLaser = np.matrix([[0],[0],[0],[1]]) * self.scale
        RTFinalLaser1 = RT * RTOrigLaser
        RTFinalLaser = self.RTVacuum() * RTFinalLaser1
        for d in laser:
            dist = d[0]
            angle = d[1]
            coord = self.coordLaser(dist,angle)
            orig_poses = np.matrix([[coord[0]], [coord[1]], [1], [1]]) * self.scale
            final_poses1 = RT * orig_poses
            final_poses = self.RTVacuum() * final_poses1
            painter.drawLine(QPointF(RTFinalLaser.flat[0],RTFinalLaser.flat[1]),QPointF(final_poses.flat[0], final_poses.flat[1]))


    def drawObstacles(self, painter):
        carsize = 30

        # Walls
        #orig_poses1 = np.matrix([[4.7266], [0], [1], [1]]) * self.scale
        #final_poses1 = self.RTVacuum() * orig_poses1
        #painter.fillRect(-carsize/2+final_poses1.flat[0], -carsize+final_poses1.flat[1], carsize, 2*carsize, Qt.black)
        painter.fillRect(-self.width()/2, -self.height()/2, 25, 500, Qt.black)
        # Obstacle 2
        orig_poses2 = np.matrix([[-7], [3], [1], [1]]) * self.scale
        final_poses2 = self.RTVacuum() * orig_poses2
        painter.fillRect(-carsize/2+final_poses2.flat[0], -carsize+final_poses2.flat[1], carsize, 2*carsize, Qt.black)
        # Obstacle 3
        orig_poses3 = np.matrix([[0.5], [3], [1], [1]]) * self.scale
        final_poses3 = self.RTVacuum() * orig_poses3
        painter.fillRect(-carsize/2+final_poses3.flat[0], -carsize+final_poses3.flat[1], carsize, 2*carsize, Qt.black)
        # Obstacle 4
        orig_poses4 = np.matrix([[14], [3], [1], [1]]) * self.scale
        final_poses4 = self.RTVacuum() * orig_poses4
        painter.fillRect(-carsize/2+final_poses4.flat[0], -carsize+final_poses4.flat[1], carsize, 2*carsize, Qt.black)


   
    def setLaserValues(self, laser):
        # Init laser array
        if len(self.laser) == 0:
            for i in range(laser.numLaser):
                self.laser.append((0,0))

        for i in range(laser.numLaser):
            dist = laser.distanceData[i]/1000.0
            angle = -math.pi/2 + math.radians(i)
            self.laser[i] = (dist, angle)
            
            
class MapWidget1(QWidget):

    stopSIG=pyqtSignal()
    
    def __init__(self,winParent):    
        super(MapWidget1, self).__init__()
        self.winParent=winParent
        self.initUI()
        self.scale = 12.0
        self.trail = []
        
        
    def initUI(self):
        layout=QGridLayout() 
        self.setLayout(layout)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.resize(300,300)
        self.setMinimumSize(500,500)
        
        
    def paintEvent(self, e):
        _width = self.width()
        _height = self.height()
        
        painter2=QPainter(self)
        pen = QPen(Qt.green, 2)
        painter2.setPen(pen)

        # Widget center
        painter2.translate(QPoint(_width/2, _height/2))
        
        # Draw obstacles
        self.drawObstacles(painter2)
    
        painter=QPainter(self)
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
    
        # Widget center
        painter.translate(QPoint(_width/2, _height/2))

        # Draw vacuum
        self.drawVacuum(painter)

        painter1=QPainter(self)
        pen = QPen(Qt.red, 2)
        painter1.setPen(pen) 
               
        # Widget center
        painter1.translate(QPoint(_width/2, _height/2))

        # Draw the car's way
        self.drawTrail(painter1)
        

    def RTCar(self):
        RTx = self.RTx(pi, 0, 0, 0)
        RTz = self.RTz(pi/2, 0, 0, 0)
        return RTx*RTz     
        

    def drawVacuum(self, painter):
        pose = self.winParent.getPose3D()
        x = pose.getX()
        y = pose.getY()
        yaw = pose.getYaw()

        orig_poses = np.matrix([[x], [y], [1], [1]]) * self.scale
        final_poses = self.RTCar() * orig_poses

        carsize = 30
        painter.translate(QPoint(final_poses[0],final_poses[1]))
        painter.rotate(-180*yaw/pi)
        
        # Chassis
        painter.fillRect(-carsize/2, -carsize,carsize,2*carsize,Qt.yellow)

        # Tires
        painter.fillRect(-carsize/2,-carsize,carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(carsize/2,-carsize,-carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(-carsize/2,carsize-2*carsize/5,carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(carsize/2,carsize-2*carsize/5,-carsize/5,2*carsize/5,Qt.black)


    def drawTrail(self, painter):
        pose = self.winParent.getPose3D()
        x = pose.getX()
        y = pose.getY()
        yaw = pose.getYaw()

        orig_poses = np.matrix([[x], [y], [1], [1]]) * self.scale
        final_poses = self.RTCar() * orig_poses
        
        if len(self.trail) < 300:
            self.trail.append([final_poses.flat[0], final_poses.flat[1]])
        else:
            for i in range(1, len(self.trail)):
                self.trail[i-1] = self.trail[i]
            self.trail[len(self.trail)-1] = [final_poses.flat[0], final_poses.flat[1]]

        for i in range(0, len(self.trail)):
            painter.drawPoint(self.trail[i][0], self.trail[i][1])
            

    def drawObstacles(self, painter):
        carsize = 30

        # Obstacle 1
        orig_poses1 = np.matrix([[-13.5], [3], [1], [1]]) * self.scale
        final_poses1 = self.RTCar() * orig_poses1
        painter.fillRect(-carsize/2+final_poses1.flat[0], -carsize+final_poses1.flat[1], carsize, 2*carsize, Qt.black)
        # Obstacle 2
        orig_poses2 = np.matrix([[-7], [3], [1], [1]]) * self.scale
        final_poses2 = self.RTCar() * orig_poses2
        painter.fillRect(-carsize/2+final_poses2.flat[0], -carsize+final_poses2.flat[1], carsize, 2*carsize, Qt.black)
        # Obstacle 3
        orig_poses3 = np.matrix([[0.5], [3], [1], [1]]) * self.scale
        final_poses3 = self.RTCar() * orig_poses3
        painter.fillRect(-carsize/2+final_poses3.flat[0], -carsize+final_poses3.flat[1], carsize, 2*carsize, Qt.black)
        # Obstacle 4
        orig_poses4 = np.matrix([[14], [3], [1], [1]]) * self.scale
        final_poses4 = self.RTCar() * orig_poses4
        painter.fillRect(-carsize/2+final_poses4.flat[0], -carsize+final_poses4.flat[1], carsize, 2*carsize, Qt.black)
        
        # Sidewalk 1
        orig_poses5 = np.matrix([[5], [9], [1], [1]]) * self.scale
        final_poses5 = self.RTCar() * orig_poses5
        painter.fillRect(-5*carsize+final_poses5.flat[0], -6*carsize+final_poses5.flat[1], 6.75*carsize, 16*carsize, Qt.black)
        # Sidewalk 2
        orig_poses6 = np.matrix([[5], [-9], [1], [1]]) * self.scale
        final_poses6 = self.RTCar() * orig_poses6
        painter.fillRect(-2*carsize+final_poses6.flat[0], -6*carsize+final_poses6.flat[1], 6.75*carsize, 16*carsize, Qt.black)


    def RTx(self, angle, tx, ty, tz):
        RT = np.matrix([[1, 0, 0, tx], [0, math.cos(angle), -math.sin(angle), ty], [0, math.sin(angle), math.cos(angle), tz], [0,0,0,1]])
        return RT
        
    def RTy(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), 0, math.sin(angle), tx], [0, 1, 0, ty], [-math.sin(angle), 0, math.cos(angle), tz], [0,0,0,1]])
        return RT
    
    def RTz(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), -math.sin(angle), 0, tx], [math.sin(angle), math.cos(angle),0, ty], [0, 0, 1, tz], [0,0,0,1]])
        return RT   

