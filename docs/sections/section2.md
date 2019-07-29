---
layout: default
---
# Practice 2: Obstacle avoidance


In this practice the objective is to implement the logic of VFF algorithm (Virtual Force Field). The principle of this technique is that each object in the robot environment generates a repulsive force to the robot, and the destination generates an attracting force in Formula 1. The Formula 1 will move in the direction of the sum of the two forces, in this way can avoid obstacles, and reach the destination. To reach a remote destination, we use local navigation, for which we will have sub-objectives to be reached.

In order to implement this practice we have Gazebo simulator and JdeRobot platform. Furthermore, the Formula 1 have a laser sensor (which allows measuring distances in a plane, providing an array of 180 numbers), plus the right and left cameras; and as actuators have engines, for which we will consider traction speed and rotation speed.

In the next picture we see a blue mantle that are laser readings, we also have a green vector, which is the attractor vector; a red vector, which is the repulsive vector; and finally a black vector, which is the combination of the two. 


![Obstacle avoidance](https://roboticsurjc-students.github.io/2016-tfg-vanessa-fernandez/images/obstacle_avoidance.png)
