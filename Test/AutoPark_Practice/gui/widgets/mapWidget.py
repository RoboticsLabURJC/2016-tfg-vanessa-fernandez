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
        self.drawLaser(1, painter, colorLaser1, 0, -50, self.laser1)
        self.drawLaser(2, painter, colorLaser2, 0, 50, self.laser2)
        self.drawLaser(3, painter, colorLaser3, -25, 0, self.laser3)


        # Draw car
        self.drawCar(painter)


    def drawCar(self, painter):
        carsize = 50

        pen = QPen(Qt.black, 1)
        painter.setPen(pen)

        # Chassis
        painter.fillRect(-carsize/2, -carsize,carsize,2*carsize,Qt.yellow)

        # Tires
        painter.fillRect(-carsize/2,-carsize,carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(carsize/2,-carsize,-carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(-carsize/2,carsize-2*carsize/5,carsize/5,2*carsize/5,Qt.black)
        painter.fillRect(carsize/2,carsize-2*carsize/5,-carsize/5,2*carsize/5,Qt.black)


    def RTLaser(self, num):
        if num == 1:
            RT = np.matrix([[math.cos(0), -math.sin(0), 0, 0], [math.sin(0), math.cos(0), 0, -2.79], [0, 0, 1, 0.772], [0, 0, 0, 1]])
        elif num == 2:
            RT = np.matrix([[math.cos(180), -math.sin(180), 0, 0], [math.sin(180), math.cos(180), 0, 2.79], [0, 0, 1, 0.772], [0, 0, 0, 1]])
        elif num == 3:
            RT = np.matrix([[math.cos(90), -math.sin(90), 0, 1.5], [math.sin(90), math.cos(90), 0, 0], [0, 0, 1, 0.772], [0, 0, 0, 1]])
        return RT

    #def RTLaser2(self, angle):
    #    RT = np.matrix([[-math.cos(angle), 0, 0], [math.sin(angle), 0, 0], [0, 0, 1]])
    #    return RT

    #def RTLaser3(self, angle):
    #    RT = np.matrix([[-math.sin(angle), 0, 0], [-math.cos(angle), 0, 0], [0, 0, 1]])
    #    return RT

    def coordLaser(self, dist, angle):
        coord = [0, 0]
        coord[0] = dist * math.cos(angle)
        coord[1] = dist * math.sin(angle) 
        return coord

    def drawLaser(self, num, painter, color, xTraslate, yTraslate, laser):
        pen = QPen(color, 2)
        painter.setPen(pen)
        RT = self.RTLaser(num)
        for d in laser:
            dist = d[0]
            angle = d[1]
            coord = self.coordLaser(dist, angle)
            orig_poses = np.matrix([[coord[0]], [coord[1]], [1], [1]]) * self.scale
            final_poses = RT * orig_poses
            #painter.drawLine(QPointF(xTraslate,yTraslate),QPointF(final_poses.flat[0] + xTraslate, final_poses.flat[1]+yTraslate))
            painter.drawLine(QPointF(0,0),QPointF(final_poses.flat[0], final_poses.flat[1]))


    def setLaserValues(self, laser, num):
        # Init laser array
        if num == 1:
             laserX = self.laser1
        elif num == 2:
             laserX = self.laser2
        elif num == 3:
             laserX = self.laser3
        if len(laserX) == 0:
            for i in range(laser.numLaser):
                laserX.append((0,0))

        for i in range(laser.numLaser):
            dist = laser.distanceData[i]/1000.0
            angle = math.radians(i)
            laserX[i] = (dist, angle)

