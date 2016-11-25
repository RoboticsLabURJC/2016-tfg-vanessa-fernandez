from sensors import sensor
import numpy as np
import cv2
import cv
import math
class MyAlgorithm():

    def __init__(self, sensor, grid):
        self.sensor = sensor
        self.grid = grid
        sensor.getPathSig.connect(self.generatePath)

    """ Write in this method the code necessary for looking for the shorter
        path to the desired destiny.
        The destiny is chosen in the GUI, making double click in the map.
        This method will be call when you press the Generate Path button. 
        Call to grid.setPath(path) mathod for setting the path. """


    def findStopExpansion(self, dest, posRobot, margin, i, j, fin):
        # Cases of the margins
        if ((dest[0] <= posRobot[0]) and (dest[1] <= posRobot[1])):
            if((i > (posRobot[0] + margin)) and (j > (posRobot[1] + margin))):
                fin = "true"
        elif ((dest[0] >= posRobot[0]) and (dest[1] <= posRobot[1])):
            if((i < (posRobot[0] - margin)) and (j > (posRobot[1] + margin))):
                fin = "true"
        elif ((dest[0] >= posRobot[0]) and (dest[1] >= posRobot[1])):
            if((i < (posRobot[0] - margin)) and (j < (posRobot[1] - margin))):
                fin = "true"
        elif ((dest[0] <= posRobot[0]) and (dest[1] >= posRobot[1])):
            if((i > (posRobot[0] + margin)) and (j < (posRobot[1] - margin))):
                fin = "true"
        return fin


    def penaltiesObstacles(self, i, j, dest0, dest1):
        mapIm = self.grid.getMap()
        found = "false"
        pos = []
        if ((i == (dest0-1)) or (i == (dest0+1)) or (j == (dest1-1)) or (j == (dest1+1))):
            penaltie = 10.0
        elif ((i == (dest0-2)) or (i == (dest0+2)) or (j == (dest1-2)) or (j == (dest1+2))):
            penaltie = 5.0
        elif ((i == (dest0-3)) or (i == (dest0+3)) or (j == (dest1-3)) or (j == (dest1+3))):
            penaltie = 2.0

        for l in range(0, len(self.posPenalties)):
           if (self.posPenalties[l] == [i, j]):
                found = "true"
                pos.append(l)
        if (found == "false"):
            self.grid.setVal(i, j, (self.grid.getVal(i, j)+penaltie))
            self.posPenalties.append([i, j])
            self.valPenalties.append(penaltie)
        else:
            if (penaltie > self.valPenalties[pos[0]]):
                self.grid.setVal(i, j, (self.grid.getVal(i, j)-self.valPenalties[pos[0]]+penaltie))
                self.valPenalties[pos[0]] = penaltie
            


    #def penaltiesObstacles(self, i, j, dest0, dest1):
    #    mapIm = self.grid.getMap()
    #    if (((i == dest0) and (j != dest1)) or ((i != dest0) and (j == dest1))):
    #        #if (self.grid.getVal(i, j) < 0.0):
    #        #    self.grid.setVal(i, j, 1000.0)
    #        #else:
    #        self.grid.setVal(i, j, (self.grid.getVal(i, j)+10.0))
    #        #if (self.grid.getVal(i, j) >= 0.0):
    #        #    self.grid.setVal(i, j, self.grid.getVal(i, j)+10.0)
    #        if ((i == dest0) and (j < dest1)):
    #            posx = [i, i]
    #            posy = [j-1, j-2]
    #        if ((i == dest0) and (j > dest1)):
    #            posx = [i, i]
    #            posy = [j+1, j+2]
    #        if ((i < dest0) and (j == dest1)):
    #            posx = [i-1, i-2]
    #            posy = [j, j]
    #        if ((i > dest0) and (j == dest1)):
    #            posx = [i+1, i+2]
    #            posy = [j, j]
    #        if ((posx[0] >= 0) and (posx[0] < 400) and (posy[0] >= 0) and (posy[0] < 400) and (mapIm[posy[0]][posx[0]] == 255)):
    #            #if (self.grid.getVal(posx[0], posy[0]) < 0.0):
    #            #    self.grid.setVal(posx[0], posy[0], 1000.0)
    #            #else:
    #            #if (self.grid.getVal(posx[0], posy[0]) >= 0.0):
    #            #    self.grid.setVal(posx[0], posy[0], (self.grid.getVal(posx[0], posy[0]) + 5.0))
    #            #mapIm[j, i] = 128
    #            #mapIm[posy[0]][posx[0]] = 128
    #            self.grid.setVal(posx[0], posy[0], (self.grid.getVal(posx[0], posy[0]) + 5.0))
    #        if ((posx[1] >= 0) and (posx[1] < 400) and (posy[1] >= 0) and (posy[1] < 400) and (mapIm[posy[1]][posx[1]] == 225)):
    #            #if (self.grid.getVal(posx[1], posy[1]) < 0.0):
    #            #    self.grid.setVal(posx[1], posy[1], 1000.0)
    #            #else:
    #            #if (self.grid.getVal(posx[1], posy[1]) >= 0.0):
    #            #    self.grid.setVal(posx[1], posy[1], (self.grid.getVal(posx[1], posy[1]) + 2.0))
    #            #mapIm[posy[1]][posx[1]] = 128
    #            self.grid.setVal(posx[1], posy[1], (self.grid.getVal(posx[1], posy[1]) + 2.0))
    #    if ((i != dest0) and (j != dest1)):
    #        num_obstacles = 0
    #        for t in range(i-1, i+2):
    #            for p in range(j-1, j+2):
    #                if ((t >= 0) and (t < 400) and (p >= 0) and (p < 400)):
    #                    if (mapIm[p][t] == 0):
    #                        num_obstacles = num_obstacles + 1
    #        if (num_obstacles == 1):
    #            #if (self.grid.getVal(i, j) < 0.0):
    #            #    self.grid.setVal(i, j, 1000.0)
    #            #else:
    #            #if (self.grid.getVal(i, j) >= 0.0):
    #            self.grid.setVal(i, j, self.grid.getVal(i, j)+10.0)
    #            #mapIm[j][i] = 128
    #            if ((i < dest0) and (j < dest1)):
    #                posx = [i, i-1, i-1, i, i-1, i-2, i-2, i-2]
    #                posy = [j-1, j, j-1, j-2, j-2, j-2, j-1, j]
    #            if ((i < dest0) and (j > dest1)):
    #                posx = [i, i-1, i-1, i, i-1, i-2, i-2, i-2]
    #                posy = [j+1, j, j+1, j+2, j+2, j+2, j+1, j]
    #            if ((i > dest0) and (j < dest1)):
    #                posx = [i, i+1, i+1, i, i+1, i+2, i+2, i+2]
    #                posy = [j-1, j, j-1, j-2, j-2, j-2, j-1, j]
    #            if ((i > dest0) and (j > dest1)):
    #                posx = [i, i+1, i+1, i, i+1, i+2, i+2, i+2]
    #                posy = [j+1, j, j+1, j+2, j+2, j+2, j+1, j]
    #            for u in range(0, len(posx)):
    #                if (u < 3):
    #                    if ((posx[u] >= 0) and (posx[u] < 400) and (posy[u] >= 0) and (posy[u] < 400) and (mapIm[posy[u]][posx[u]] == 255)):
    #                        #if (self.grid.getVal(posx[u], posy[u]) < 0.0):
    #                        #    self.grid.setVal(posx[u], posy[u], 1000.0)
    #                        #else:
    #                        #if (self.grid.getVal(posx[u], posy[u]) >= 0.0):
    #                        #    self.grid.setVal(posx[u], posy[u], (self.grid.getVal(posx[u], posy[u]) + 5.0))
    #                        #mapIm[posy[u]][posx[u]] = 128
    #                        self.grid.setVal(posx[u], posy[u], (self.grid.getVal(posx[u], posy[u]) + 5.0))
    #                else:
    #                    if ((posx[u] >= 0) and (posx[u] < 400) and (posy[u] >= 0) and (posy[u] < 400) and (mapIm[posy[u]][posx[u]] == 255)):
    #                        #if (self.grid.getVal(posx[u], posy[u]) < 0.0):
    #                        #    self.grid.setVal(posx[u], posy[u], 1000.0)
    #                        #else:
    #                        #if (self.grid.getVal(posx[u], posy[u]) >= 0.0):
    #                        #    self.grid.setVal(posx[u], posy[u], (self.grid.getVal(posx[u], posy[u]) + 2.0))
    #                        #mapIm[posy[u]][posx[u]] = 128
    #                        self.grid.setVal(posx[u], posy[u], (self.grid.getVal(posx[u], posy[u]) + 2.0)) 
  

    def generatePath(self):
        print "LOOKING FOR SHORTER PATH"
        # mapIm is the image of the map
        mapIm = self.grid.getMap()
        # dest is the selected destination, and is a tuple such that (x, y)      
        dest = self.grid.getDestiny()
        # griPose is the position on the map, (x, y)
        gridPos = self.grid.getPose()


        #TODO

        # Position of the robot
        world_robotX = self.sensor.getRobotX()
        world_robotY = self.sensor.getRobotY()
        posRobot = self.grid.worldToGrid(world_robotX, world_robotY)

        # We need some variables in the loop while
        fin = "false"
        square = 0
        margin = 30


        # Evaluating the value of the field on position (dest[0], dest[1])
        if (mapIm[dest[1]][dest[0]] == 255):
            self.grid.setVal(dest[0], dest[1], 0.0)
        else:
            self.grid.setVal(dest[0], dest[1], 20000.0)

        # Expansion of the field
        #while (fin == "false"):
        #    for i in range(dest[0]-square, dest[0]+square+1):
        #        for j in range(dest[1]-square, dest[1]+square+1):
        #            if ((i >= 0) and (i < 400) and (j >= 0) and (j < 400)):
        #               for k in range(i-1, i+2):
        #                   for l in range(j-1, j+2):
        #                       if ((k >= 0) and (k < 400) and (l >= 0) and (l < 400)):
        #                           val = self.grid.getVal(k, l)
        #                           val_init = self.grid.getVal(i, j)
        #                           if ((k == dest[0]) and (l == dest[1])):
        #                               self.grid.setVal(k, l, self.grid.getVal(k, l))
        #                           elif ((k == i) and (l == j)):
        #                               self.grid.setVal(k, l, val_init+0.0)
        #                           else:
        #                               if ((k != i) and (l != j)):
        #                                   if ((math.isnan(val)) or ((val_init + math.sqrt(2.0)) < val) or (val <= 0)):
        #                                       self.grid.setVal(k, l, val_init+math.sqrt(2.0))
        #                               else:
        #                                   if ((math.isnan(val)) or ((val_init + 1.0) < val) or (val <= 0)):
        #                                       self.grid.setVal(k, l, val_init+1.0)
        #                               if (mapIm[l][k] == 0):
        #                                   val_pos = self.grid.getVal(k, l)
        #                                   self.grid.setVal(k, l, (val_pos+20000.0))
        #                                   #if (self.grid.getVal(k, l) < 40000.0):
        #                                   #    print "hi"
        #                                   #    pos_obstacles_border.append([k, l])
        #            # Cases of the margins
        #            fin = self.findStopExpansion(dest, posRobot, margin, i, j, fin)
        #    square = square + 1



        # Expansion of the field
        while (fin == "false"):
            for i in range(dest[0]-square, dest[0]+square+1):
                for j in range(dest[1]-square, dest[1]+square+1):
                    if ((i >= 0) and (i < 400) and (j >= 0) and (j < 400)):
                       for k in range(i-1, i+2):
                           for l in range(j-1, j+2):
                               if ((k >= 0) and (k < 400) and (l >= 0) and (l < 400)):
                                   val = self.grid.getVal(k, l)
                                   val_init = self.grid.getVal(i, j)
                                   if ((k == dest[0]) and (l == dest[1])):
                                       self.grid.setVal(k, l, self.grid.getVal(k, l))
                                   elif ((k == i) and (l == j)):
                                       self.grid.setVal(k, l, val_init+0.0)
                                   else:
                                       if ((k != i) and (l != j)):
                                           if ((math.isnan(val)) or ((val_init + math.sqrt(2.0)) < val) or (val <= 0)):
                                               self.grid.setVal(k, l, val_init+math.sqrt(2.0))
                                       else:
                                           if ((math.isnan(val)) or ((val_init + 1.0) < val) or (val <= 0)):
                                               self.grid.setVal(k, l, val_init+1.0)
                                       if (mapIm[l][k] == 0):
                                           val_pos = self.grid.getVal(k, l)
                                           self.grid.setVal(k, l, (val_pos+20000.0))
                       if (((i < dest[0]-square+1) or (i > dest[0]+square-1)) or ((i >= dest[0]-square+1) and (i <= dest[0]+square-1) and ((j < dest[1]-square+1) or (j > dest[1]+square-1)))):
                           if (mapIm[j][i] == 0):
                               pos_obstacles_border.append([i,j])
                    # Cases of the margins
                    fin = self.findStopExpansion(dest, posRobot, margin, i, j, fin)
            square = square + 1

        print len(pos_obstacles_border)


        # Obstacles penalties
        for i in range(0, len(pos_obstacles_border)):
            if (mapIm[pos_obstacles_border[i][1]][pos_obstacles_border[i][0]] == 0):
                for k in range(pos_obstacles_border[i][0]-3, pos_obstacles_border[i][0]+4):
                    for l in range(pos_obstacles_border[i][1]-3, pos_obstacles_border[i][1]+4):
                        if ((k >= 0) and (k < 400) and (l >= 0) and (l < 400)):
                            if (mapIm[l][k] == 255):
                                self.penaltiesObstacles(k, l, pos_obstacles_border[i][0], pos_obstacles_border[i][1])
                                #print "k, l, i, j", k, l, pos_obstacles_border[i][0], pos_obstacles_border[i][1]

        # MIRAR
        # Obstacles penalties
        #for i in range(0, 400):
        #    for j in range(0, 400):
        #        #if ((i >= 0) and (i < 400) and (j >= 0) and (j < 400)):
        #        if (mapIm[j][i] == 0):
        #            for k in range(i-3, i+4):
        #                for l in range(j-3, j+4):
        #                    if ((k >= 0) and (k < 400) and (l >= 0) and (l < 400)):
        #                        if (mapIm[l][k] == 255):
        #                            self.penaltiesObstacles(k, l, i, j)
        #                            print "k, l, i, j", k, l, i, j#



        # Obstacles penalties
        #fin_obstacles = "false"
        #squareO = 0
        #while (fin_obstacles == "false"):
        #    for i in range(dest[0]-squareO, dest[0]+squareO+1):
        #        for j in range(dest[1]-squareO, dest[1]+squareO+1):
        #            if ((i >= 0) and (i < 400) and (j >= 0) and (j < 400)):
        #                if (mapIm[j][i] == 0):
        #                    #if (((i< dest[0]-squareO+1) or (i > dest[0]+squareO-1)) or ((i>= dest[0]-squareO+1) and (i<= dest[0]+squareO-1) and ((j< dest[1]-squareO+1) or (j> dest[1]+squareO-1)))):
        #                    for k in range(i-3, i+4):
        #                        for l in range(j-3, j+4):
        #                            if ((k >= 0) and (k < 400) and (l >= 0) and (l < 400)):
        #                                if (mapIm[l][k] == 255):
        #                                    self.penaltiesObstacles(k, l, i, j)
        #                                    print "k, l, i, j", k, l, i, j
        #                                    #print "hi"
        #            # Cases of the margins
        #            fin_obstacles = self.findStopExpansion(dest, posRobot, margin, i, j, fin_obstacles)
        #    squareO = squareO + 1


        # Find the path
        pixelCentral = [posRobot[0], posRobot[1]]
        valMin = self.grid.getVal(posRobot[0], posRobot[1])
        posMin = pixelCentral
        self.grid.setPathVal(posRobot[0], posRobot[1], valMin)
        found = "false"
        while (found == "false"):
            FoundNeighbour = "false"
            for i in range(pixelCentral[0]-1, pixelCentral[0]+2):
                for j in range(pixelCentral[1]-1, pixelCentral[1]+2):
                    if ((i >= 0) and (i < 400) and (j >= 0) and (j < 400)):
                        if (FoundNeighbour == "false"):
                            valMinNeighbour = self.grid.getVal(i, j)
                            posMinNeighbour = [i, j]
                            FoundNeighbour = "true"
                        val = self.grid.getVal(i, j)
                        if ((val <= valMin) and (val >=  0.0)):
                            if (((val == 0.0) and (i == dest[0]) and (j == dest[1])) or (val > 0.0)):
                                valMin = val
                                posMin = [i, j]
                                valMinNeighbour = valMin
                                posMinNeighbour = posMin
                        elif (val < valMinNeighbour):
                            valMinNeighbour = val
                            posMinNeighbour = [i, j]
                        #print("posactual",i, j, "posMin", posMin,"dest", dest, "posnei", posMinNeighbour)
                        #print("valMin", valMin, "val pos actual", val, "val dest", self.grid.getVal(dest[0], dest[1]), "val neig", valMinNeighbour)
            self.grid.setPathVal(posMinNeighbour[0], posMinNeighbour[1], valMinNeighbour)
            pixelCentral = posMinNeighbour
            if ((valMinNeighbour == 0.0) and (posMinNeighbour[0] == dest[0]) and (posMinNeighbour[1] == dest[1])):
                found = "true"
                self.grid.setPathFinded()


        #Represent the Gradient Field in a window using cv2.imshow
        self.grid.showGrid()


    """ Write in this mehtod the code necessary for going to the desired place,
        once you have generated the shorter path.
        This method will be periodically called after you press the GO! button. """
    def execute(self):
        # Add your code here
        print "GOING TO DESTINATION"
        # dest is the selected destination    
        dest = self.grid.getDestiny()
        # Position of the robot
        posRobotX = self.sensor.getRobotX()
        posRobotY = self.sensor.getRobotY()
        orientationRobot = self.sensor.getRobotTheta()
        print (posRobotX, posRobotY, orientationRobot)