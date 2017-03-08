from sensors import sensor
import numpy as np
import cv2
import math
import threading
import time
from datetime import datetime
from matplotlib import pyplot as plt

time_cycle = 80

class MyAlgorithm(threading.Thread):

    def __init__(self, grid, sensor, vel):
        self.sensor = sensor
        self.grid = grid
        self.vel = vel
        self.posPenalties = []
        self.valPenalties = []
        sensor.getPathSig.connect(self.generatePath)

        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)


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


    def incorporateNode(self, pos0, pos1, nodos):
        found = False
        for i in range(0, len(nodos)):
            if self.grid.getVal(pos0, pos1) == self.grid.getVal(nodos[i][0][0], nodos[i][0][1]):
                nodos[i].append([pos0, pos1])
                found = True
        if found == False:
            nodos.append([[pos0, pos1]])
        return nodos


    def penaltiesObstacles(self, i, j, dest0, dest1):
        found = "false"
        pos = []
        if ((((i == (dest0-1)) or (i == (dest0+1))) and (dest1-1 <= j <= dest1+1)) or (((j == (dest1-1)) or (j == (dest1+1))) and (i == dest0))):
            penaltie = 25.0
        elif ((((i == (dest0-2)) or (i == (dest0+2)) and (dest1-2 <= j <= dest1+2)) or (((j == (dest1-2)) or (j == (dest1+2))) and (dest0-1 <= i <= dest0+1)))):
            penaltie = 15.0
        elif ((((i == (dest0-3)) or (i == (dest0+3)) and (dest1-3 <= j <= dest1+3)) or (((j == (dest1-3)) or (j == (dest1+3))) and (dest0-2 <= i <= dest0+2)))):
            penaltie = 10.0

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



    """ Write in this method the code necessary for looking for the shorter
        path to the desired destiny.
        The destiny is chosen in the GUI, making double click in the map.
        This method will be call when you press the Generate Path button. 
        Call to grid.setPath(path) mathod for setting the path. """
    def generatePath(self):

        print("LOOKING FOR SHORTER PATH")
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
        margin = 20
        pos_obstacles_border = []
        #fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
        #out = cv2.VideoWriter('Penalización.avi', fourcc, 30, (400, 400),False)

        # Evaluating the value of the field on position (dest[0], dest[1])
        if (mapIm[dest[1]][dest[0]] == 255):
            self.grid.setVal(dest[0], dest[1], 0.0)
            nodo = [[dest[0], dest[1]]]


        imagen = np.zeros((400, 400),np.uint8)
        x=1
        o=1

        # Expansion of the field
        #while (fin == "false"):
        #    for i in range(dest[0]-square, dest[0]+square+1):
        #        for j in range(dest[1]-square, dest[1]+square+1):
        #            if ((i >= 0) and (i < 400) and (j >= 0) and (j < 400) and (mapIm[j][i])):
        #               border = 0
        #               for k in range(i-1, i+2):
        #                   for l in range(j-1, j+2):
        #                       if ((k >= 0) and (k < 400) and (l >= 0) and (l < 400) and (mapIm[j][i] == 255)):
        #                           val = self.grid.getVal(k, l)
        #                           val_init = self.grid.getVal(i, j)
        #                           if(mapIm[l][k] == 0):
        #                               border = border + 1
        #                           elif (mapIm[j][i] == 255):
        #                               if ((k == dest[0]) and (l == dest[1])):
        #                                   self.grid.setVal(k, l, self.grid.getVal(k, l))
        #                               elif ((k == i) and (l == j)):
        #                                   self.grid.setVal(k, l, val_init+0.0)
        #                               else:
        #                                   if ((k != i) and (l != j) and (mapIm[l][k] == 255)):
        #                                       if ((math.isnan(val)) or ((val_init + math.sqrt(2.0)) < val) or (val <= 0)):
        #                                           self.grid.setVal(k, l, val_init+math.sqrt(2.0))
        #                                   else:
        #                                       if ((math.isnan(val)) or ((val_init + 1.0) < val) or (val <= 0)) and (mapIm[l][k] == 255):
        #                                           self.grid.setVal(k, l, val_init+1.0)
        #                       imagen[l][k] = self.grid.getVal(k, l)
        #                       #plt.imshow(imagen,'gray')
        #                       #plt.show()
        #                       #img = cv2.cvtColor(imagen, cv2.COLOR_GRAY2RGB)
        #                       if (x/o) == 200:
        #                           out.write((imagen))
        #                           o = o+1
        #               if (((i < dest[0]-square+1) or (i > dest[0]+square-1)) or ((i >= dest[0]-square+1) and (i <= dest[0]+square-1) and ((j < dest[1]-square+1) or (j > dest[1]+square-1)))):
        #                   if ((i >= 0) and (i < 400) and (j >= 0) and (j < 400)):
        #                       if (border != 9 and mapIm[j][i] == 0):
        #                           pos_obstacles_border.append([i,j])                    
        #            # Cases of the margins
        #            fin = self.findStopExpansion(dest, posRobot, margin, i, j, fin)
        #            x = x+1
        #    square = square + 1
        #out.release()


        # Expansion of the field
        #while (fin == "false"):
        #    for i in range(dest[0]-square, dest[0]+square+1):
        #        for j in range(dest[1]-square, dest[1]+square+1):
        #            if ((i >= 0) and (i < mapIm.shape[0]) and (j >= 0) and (j < mapIm.shape[1])):
        #               border = 0
        #               for k in range(i-1, i+2):
        #                   for l in range(j-1, j+2):
        #                       if ((k >= 0) and (k < mapIm.shape[0]) and (l >= 0) and (l < mapIm.shape[1])):
        #                           val = self.grid.getVal(k, l)
        #                           val_init = self.grid.getVal(i, j)
        #                           if(mapIm[l][k] == 0):
        #                               border = border + 1
        #                           elif (mapIm[j][i] == 255):
        #                               if ((k == dest[0]) and (l == dest[1])):
        #                                   self.grid.setVal(k, l, self.grid.getVal(k, l))
        #                               elif ((k == i) and (l == j)):
        #                                   self.grid.setVal(k, l, val_init+0.0)
        #                               else:
        #                                   if ((k != i) and (l != j) and (mapIm[l][k] == 255)):
        #                                       if ((math.isnan(val)) or ((val_init + math.sqrt(2.0)) < val) or (val <= 0)):
        #                                           self.grid.setVal(k, l, val_init+math.sqrt(2.0))
        #                                   else:
        #                                       if ((math.isnan(val)) or ((val_init + 1.0) < val) or (val <= 0)) and (mapIm[l][k] == 255):
        #                                           self.grid.setVal(k, l, val_init+1.0)
        #                       imagen[l][k] = self.grid.getVal(k, l)
        #                       if self.grid.getVal(k, l) > mas:
        #                           mas = self.grid.getVal(k, l)
        #                       #plt.imshow(imagen,'gray')
        #                       #plt.show()
        #                       #img = cv2.cvtColor(imagen, cv2.COLOR_GRAY2RGB)
        #                       #if (x/o) == 200:
        #                       #    out.write((imagen))
        #                       #    o = o+1
        #               if (((i < dest[0]-square+1) or (i > dest[0]+square-1)) or ((i >= dest[0]-square+1) and (i <= dest[0]+square-1) and ((j < dest[1]-square+1) or (j > dest[1]+square-1)))):
        #                   if ((i >= 0) and (i < 400) and (j >= 0) and (j < 400)):
        #                       if (border != 9 and mapIm[j][i] == 0):
        #                           pos_obstacles_border.append([i,j])                
        #            # Cases of the margins
        #            fin = self.findStopExpansion(dest, posRobot, margin, i, j, fin)
        #            x = x+1
        #    square = square + 1
        #out.release()

        # New nodes
        nodos = []

        # Expansion of the field
        while (fin == "false"):
            for i in range(0, len(nodo)):
                if ((mapIm[nodo[i][1], nodo[i][0]] == 255) and nodo[i][0] >= 0 and nodo[i][0] < mapIm.shape[0] and nodo[i][1] >= 0 and nodo[i][1] < mapIm.shape[1]):
                    # Wave fronts of each node
                    frente1 = [[nodo[i][0]-1, nodo[i][1]], [nodo[i][0], nodo[i][1]-1], [nodo[i][0]+1, nodo[i][1]], [nodo[i][0], nodo[i][1]+1]]
                    frente2 = [[nodo[i][0]-1, nodo[i][1]-1], [nodo[i][0]+1, nodo[i][1]-1], [nodo[i][0]+1, nodo[i][1]+1], [nodo[i][0]-1, nodo[i][1]+1]]
                    val_init = self.grid.getVal(nodo[i][0], nodo[i][1])
                    for j in range(0, len(frente1)):
                        if (j >= 400) and (j <400):
                            if mapIm[frente1[j][1], frente1[j][0]] == 255:
                                val = self.grid.getVal(frente1[j][0], frente1[j][1])
                                if ((math.isnan(val)) or ((val_init + 1.0) < val) or (val <= 0)):
                                    if frente1[j][0] != dest[0] or frente1[j][1] != dest[1]:
                                        self.grid.setVal(frente1[j][0], frente1[j][1], val_init+1.0)
                                        nodos = self.incorporateNode(frente1[j][0], frente1[j][1], nodos)
                            else:
                                pos_obstacles_border.append([frente1[j][0],frente1[j][1]])
                            imagen[frente1[j][1]][frente1[j][0]] = self.grid.getVal(frente1[j][0], frente1[j][1])
                            #if (x/o) == 100:
                            #    out.write((imagen))
                            #    o = o + 1
                    for j in range(0, len(frente2)):
                        if (j >= 400) and (j <400):
                            if mapIm[frente2[j][1], frente2[j][0]] == 255:
                                val = self.grid.getVal(frente2[j][0], frente2[j][1])
                                if ((math.isnan(val)) or ((val_init + math.sqrt(2.0)) < val) or (val <= 0)):
                                    if frente2[j][0] != dest[0] or frente2[j][1] != dest[1]:
                                        self.grid.setVal(frente2[j][0], frente2[j][1], val_init+math.sqrt(2.0))
                                        nodos = self.incorporateNode(frente2[j][0], frente2[j][1], nodos)
                            imagen[frente2[j][1]][frente2[j][0]] = self.grid.getVal(frente2[j][0], frente2[j][1])
                            #if (x/o) == 100:
                            #    out.write((imagen))
                            #    o = o + 1
                # Cases of the margins
                fin = self.findStopExpansion(dest, posRobot, margin, nodo[i][0], nodo[i][1], fin)
                #x = x + 1
            if (nodos != []):
                nodo = nodos[0]
                nodos.pop(0)
        #out.release()



        # Obstacles penalties
        for i in range(0, len(pos_obstacles_border)):
            for k in range(pos_obstacles_border[i][0]-3, pos_obstacles_border[i][0]+4):
                for l in range(pos_obstacles_border[i][1]-3, pos_obstacles_border[i][1]+4):
                    if ((k >= 0) and (k < 400) and (l >= 0) and (l < 400)):
                        if (mapIm[l][k] == 255):
                            self.penaltiesObstacles(k, l, pos_obstacles_border[i][0], pos_obstacles_border[i][1])
                    imagen[l][k] = self.grid.getVal(k, l)
                    #if (x/o) == 100:
                    #    out.write((imagen))
                    #    o = o+1
            #x=x+1
        #out.release()



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
                        print("posactual",i, j, "posMin", posMin,"dest", dest, "posnei", posMinNeighbour)
                        print("valMin", valMin, "val pos actual", val, "val dest", self.grid.getVal(dest[0], dest[1]), "val neig", valMinNeighbour)
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
        print("GOING TO DESTINATION")
        # dest is the selected destination    
        dest = self.grid.getDestiny()
        # Position of the robot
        posRobotX = self.sensor.getRobotX()
        posRobotY = self.sensor.getRobotY()
        orientationRobot = self.sensor.getRobotTheta()
        print (posRobotX, posRobotY, orientationRobot)

        #EXAMPLE OF HOW TO SEND INFORMATION TO THE ROBOT ACTUATORS
        #self.vel.setV(10)
        #self.vel.setW(5)
        #self.vel.sendVelocities()
