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
#       Eduardo Perdices <eperdices@gsyc.es>
#

#import resources_rc
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtGui import QPen, QPainter
from PyQt5.QtCore import QPoint, QPointF, pyqtSignal, Qt
import numpy as np
import math

class MapWidget(QWidget):

    stopSIG=pyqtSignal()
    
    def __init__(self,winParent):    
        super(MapWidget, self).__init__()
        self.winParent=winParent
        self.initUI()

        self.carx = 0.0
        self.cary = 0.0
        self.obsx = 0.0
        self.obsy = 0.0
        self.avgx = 0.0
        self.avgy = 0.0
        self.targetx = 0.0
        self.targety = 0.0
        self.scale = 20.0
        self.laser1 = []
        self.laser2 = []
        self.laser3 = []
        
    def initUI(self):
        layout=QGridLayout()  
        self.setLayout(layout)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.resize(300,300)
        self.setMinimumSize(700,500)
        
    def paintEvent(self, e):
        _width = self.width()
        _height = self.height()
    
        painter=QPainter(self)
        pen = QPen(Qt.blue, 2)
        painter.setPen(pen)
    
        #Widget center
        painter.translate(QPoint(_width/2, _height/2))

        # Draw laser
        colorLaser1 = Qt.blue
        colorLaser2 = Qt.green
        colorLaser3 = Qt.red
        self.drawLaser1(painter, colorLaser1,-50)
        self.drawLaser2(painter, colorLaser2)
        self.drawLaser3(painter, colorLaser3)


        # Draw car
        self.drawCar(painter)


    def drawCar(self, painter):
        carsize = 50

        pen = QPen(Qt.black, 1)
        painter.setPen(pen)

        # Connectors
        #painter.drawLine(QPointF(-carsize/5,carsize/5),QPointF(carsize/5, carsize/5))

        # Chassis
        painter.fillRect(-carsize/2, -carsize,carsize,2*carsize,Qt.yellow)

        # Tires
        painter.fillRect(-carsize/2,-carsize,carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(carsize/2,-carsize,-carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(-carsize/2,carsize-2*carsize/5,carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(carsize/2,carsize-2*carsize/5,-carsize/5,2*carsize/5,Qt.black)


    def RT1(self, d0, d1):
        RT = np.array([[math.cos(d1), 0, 0], [math.sin(d1), 0, 0], [0, 0, 1]])
        return RT

    def drawLaser1(self, painter, color, traslate):
        pen = QPen(color, 2)
        painter.setPen(pen)
        for d in self.laser1:
            #px = d[0]*math.cos(d[1])*self.scale
            #py = -d[0]*math.sin(d[1])*self.scale
            #poses = np.array([[math.cos(d[1]), 0, 0], [math.sin(d[1]), 0, 0], [0, 0, 1]])*np.array([[d[0]], [-d[0]], [1]]) *self.scale
            RT = self.RT1(d[0], d[1])
            poses = RT*np.array([[d[0]], [-d[0]], [1]]) *self.scale
            painter.drawLine(QPointF(0,traslate),QPointF(poses[0][0], poses[1][0]+traslate))


    def drawLaser2(self, painter, color):
        pen = QPen(color, 2)
        painter.setPen(pen)
        for d in self.laser2:
            px = -d[0]*math.cos(d[1])*self.scale
            py = d[0]*math.sin(d[1])*self.scale
            painter.drawLine(QPointF(0,50),QPointF(px, py+50))
            

    def drawLaser3(self, painter, color):
        pen = QPen(color, 2)
        painter.setPen(pen)
        for d in self.laser3:
            px = -d[0]*math.sin(d[1])*self.scale
            py = -d[0]*math.cos(d[1])*self.scale
            painter.drawLine(QPointF(-25,0),QPointF(px-25, py))
            

    def setCarArrow(self, x, y):
        self.carx = x
        self.cary = y

    def setObstaclesArrow(self, x, y):
        self.obsx = x
        self.obsy = y

    def setAverageArrow(self, x, y):
        self.avgx = x
        self.avgy = y

    def setTarget(self, x, y, rx, ry, rt):
        # Convert to relatives
        dx = x - rx
        dy = y - ry

        # Rotate with current angle
        self.targetx = dx*math.cos(-rt) - dy*math.sin(-rt)
        self.targety = dx*math.sin(-rt) + dy*math.cos(-rt)

    def setLaserValues1(self, laser):
        # Init laser array
        if len(self.laser1) == 0:
            for i in range(laser.numLaser):
                self.laser1.append((0,0))

        for i in range(laser.numLaser):
            dist = laser.distanceData[i]/1000.0
            angle = math.radians(i)
            self.laser1[i] = (dist, angle)



    def setLaserValues2(self, laser):
        if len(self.laser2) == 0:
            for i in range(laser.numLaser):
                self.laser2.append((0,0))

        for i in range(laser.numLaser):
            dist = laser.distanceData[i]/1000.0
            angle = math.radians(i)
            self.laser2[i] = (dist, angle)

 
    def setLaserValues3(self, laser):
        if len(self.laser3) == 0:
            for i in range(laser.numLaser):
                self.laser3.append((0,0))

        for i in range(laser.numLaser):
            dist = laser.distanceData[i]/1000.0
            angle = math.radians(i)
            self.laser3[i] = (dist, angle)


