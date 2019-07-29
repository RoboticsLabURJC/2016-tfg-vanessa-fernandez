---
layout: default
---
# Practice 2: Obstacle avoidance


In this practice the objective is to implement the logic of VFF algorithm (Virtual Force Field). The principle of this technique is that each object in the robot environment generates a repulsive force to the robot, and the destination generates an attracting force in Formula 1. The Formula 1 will move in the direction of the sum of the two forces, in this way can avoid obstacles, and reach the destination. To reach a remote destination, we use local navigation, for which we will have sub-objectives to be reached.

In order to implement this practice we have Gazebo simulator and JdeRobot platform. Furthermore, the Formula 1 have a laser sensor (which allows measuring distances in a plane, providing an array of 180 numbers), plus the right and left cameras; and as actuators have engines, for which we will consider traction speed and rotation speed.

In the next picture we see a blue mantle that are laser readings, we also have a green vector, which is the attractor vector; a red vector, which is the repulsive vector; and finally a black vector, which is the combination of the two. 


![Obstacle avoidance](https://roboticsurjc-students.github.io/2016-tfg-vanessa-fernandez/images/obstacle_avoidance.png)


The steps we must follow are:

- Getting the position of the sub-goal to which we want to reach: 

<pre>
self.currentTarget=self.getNextTarget()
self.targetx = self.currentTarget.getPose().x
self.targety = self.currentTarget.getPose().y
</pre>


- We get the robot position and orientation of the robot with respect to the map: 

<pre>
rx = self.sensor.getRobotX()
ry = self.sensor.getRobotY()
rt = self.sensor.getRobotTheta()
</pre>


- We mark the sub-objectives for which we have already crossed: 

<pre>
if(abs(ry)<(abs(self.targety)+1) and abs(ry)>(abs(self.targety)-1)):
     self.currentTarget.setReached(True)
</pre>


- We obtain the data of the laser sensor, which consist of 180 pairs of values and we obtain the laser data more clearly: 

<pre>
laser_data = self.sensor.getLaserData()
laser = parse_laser_data(laser_data)
</pre>


- We convert the absolute coordinates of the sub-goal in coordinates relative to the robot: 

<pre>
self.carx,self.cary=absolutas2relativas(self.targetx,self.targety,rx,ry,rt)
</pre>


- With the laser data, we obtain the repulsive vector: 

<pre>
dist_threshold = 6
vff_repulsor_list = []
for d,a in laser:
     # (4.2.1) laser into GUI reference system
     if(d < dist_threshold):
          x = (d - dist_threshold) * math.cos(a) * -1
          y = (d - dist_threshold) * math.sin(a) * -1
          v = (x,y)
          vff_repulsor_list += [v]

vff_repulsor = np.mean(vff_repulsor_list, axis=0)

self.obsx,self.obsy = vff_repulsor
</pre>


- We calculate the module of repulsive vector and depending in its value remains as is or increase its weight: 

<pre>
mod_repulsor = pow(pow(self.obsx,2) + pow(self.obsy,2),0.5)
if (mod_repulsor > 1.55):
     self.obsx,self.obsy = vff_repulsor * 4.5
</pre>


- We make the sum of the attractor and repulsive vectors to obtain the resulting vector:

<pre>
self.avgx = self.carx + self.obsx
self.avgy = self.cary + self.obsy
</pre>


- Calculation of the speed module: 

<pre>
speed = pow(pow(self.avgx,2) + pow(self.avgy,2),0.5)
</pre>


- Calculation of the correction: 

<pre>
if (abs(self.obsx) > 2):
     if (abs(self.obsx) < abs(self.carx)):
         if (self.obsx >= 0):
             self.avgx = abs(self.avgx)
         else:
             self.avgx = -abs(self.avgx)

if ((self.obsx == (-self.carx)) and (self.obsy == (-self.cary))):
     self.avgx = self.obsx
     self.avgy = self.cary
</pre>


- Calculation of the angle: 

<pre>
if (speed < 1):
    # Use the tangent to avoid indeterminacy
    angle = math.atan(abs(self.avgx/self.avgy))
else:
    angle = math.asin(abs(self.avgx/speed))
if(self.avgy > 0):
    angle = math.pi - angle
</pre>


- We assign the traction and rotation speeds: 

<pre>
# Linear speed
if ((speed < 1) or (speed > 3)):
     self.sensor.setV(3)
else:
     self.sensor.setV(speed)

# Angular speed
if(self.avgx < 0):
     self.sensor.setW(angle * 0.75)
else:
     self.sensor.setW(-angle * 0.75)
</pre>


Here, we see a video of this practice: 

[![Práctica 2- Obstacle avoidance](https://roboticsurjc-students.github.io/2016-tfg-vanessa-fernandez/images/obst_avoidance.png)](https://www.youtube.com/watch?v=8dEg-3qunU4)



* Problem with solution of VFF

[![Problem obstacle avoidance](https://roboticsurjc-students.github.io/2016-tfg-vanessa-fernandez/images/obst_avoidance.png)](https://www.youtube.com/watch?v=rCKQaw2_0hA)



* Practice: obstacle avoidance (VFF) in version JdeRobot 5.4.2

I have made the solution of the VFF's algorithm for the version 5.4.2 of JdeRobot. I made some changes to the solution from the previous version of JdeRobot.The changes are:

- How to get the robot's position:

<pre>
rx = self.pose3d.getX()/1000
ry = self.pose3d.getY()/1000
rt = self.pose3d.getYaw()
</pre>


- The linear speed and the angular speed:

<pre>
if ((speed < 1) or (speed > 3)):
    self.motors.sendV(3)
else:
    self.motors.sendV(speed)

if(self.avgx < 0):
    self.motors.sendW(-angle * 0.75)
else:
    self.motors.sendW(angle * 0.75)
</pre>

[![Obstacle avoidance (versión 5.4.2 de JdeRobot)](https://roboticsurjc-students.github.io/2016-tfg-vanessa-fernandez/images/obst_avoidance.png)](https://www.youtube.com/watch?v=kVPGPjUv1oM)


