---
layout: default
---
# Stop Practice


* **Eighth step with solution:**

[![Stop Practice v8 (JdeRobot Academy)](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/stop.png)](https://www.youtube.com/watch?v=IOdmZzXmbf8)


* **Seventh step with solution**

[![Stop Practice v7 (JdeRobot Academy)](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/stop.png)](https://www.youtube.com/watch?v=Tne9SZRI4vE)


* **Sixth step with solution**

[![Stop Practice v6 (JdeRobot Academy)](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/stop.png)](https://www.youtube.com/watch?v=cyYbcvvSaT4)


* **Fifth step with solution**

[![Stop Practice v5 (JdeRobot Academy)](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/stop.png)](https://www.youtube.com/watch?v=z3Q7idhFOVM)


* **Fourth step with solution**

[![Stop Practice v4 (JdeRobot Academy)](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/stop.png)](https://www.youtube.com/watch?v=ggxYFdi1Wvs)


* **Updated**

![New world](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/new_stop.png)


* **Third step with solution**

[![Stop Practice v3 (JdeRobot Academy)](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/stop.png)](https://www.youtube.com/watch?v=dgnApi4-rtA)


* **Second step with solution**

[![Stop Practice v2 (JdeRobot Academy)](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/stop.png)](https://www.youtube.com/watch?v=cozAPOndtoY)


* **First step with solution**

[![Stop Practice v1 (JdeRobot Academy)](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/stop.png)](https://www.youtube.com/watch?v=zHv_F0uZM7c)



* **Cars that move alone in different directions and at different speeds**

I've modified the stop.world. Now, there are cars that move in different directions and at different speeds. 

[![Dummy](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/stop.png)](https://www.youtube.com/watch?v=kF8ISlxbMHA)


* **Cars that move by themselves in the Stop world**

I've maked a world named stop.world in Gazebo. In this world, there are cars that move by themself.

[![Dummycar stop: test in Gazebo](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/stop.png)](https://www.youtube.com/watch?v=0JcB6dxByd0)


* **Collisions with objects + kobukiViewer**

I've created a world in Gazebo using a .dae file. To create this file I has used the program Sketchup in Windows.In the world I added a turtlebot to teleoperate it with kobukiViewer component.In the following video we can see how it moves the turtlebot when we teleoperate it. When I've created the world I've added a collision mesh for road.Thus the robot doesn't fall.

[![kobukiViewer (JdeRobot)](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/stop.png)](https://www.youtube.com/watch?v=g1MN0oACf48)


* **Roads, house and carApriltag in Gazebo**

I created a world called road.world in Gazebo. I have used the car created by Andres Hernández (carApriltag). I included a house and some roads. I created the roads using coordinates. First, I've included the carMotors.cfg file:

<pre>
    Motors.Endpoints=default -h localhost -p 9999
</pre>

The .word file is as follows:

<pre>
<?xml version="1.0" ?>
<sdf version="1.5">
<world name="default">
	<scene>
	<grid>false</grid>
</scene>
<!-- A global light source -->
<include>
	<uri>model://sun</uri>
</include>

<!-- A ground plane -->
<include>
	<uri>model://ground_plane</uri>
</include>

	<!-- A car-->
<include>
	<uri>model://carApriltag</uri>
	<pose>0 0 0.5 0 0 3.15</pose>
</include>
<!-- A road -->
<road name="my_road">
	<width>3</width>
	<point>0 -20 0.02</point>
	<point>0 0 0.02</point>
	<point>0 20 0.02</point>
</road>
<road name="my_road2">
	<width>3</width>
	<point>-20 20 0.02</point>
	<point>0 20 0.02</point>
	<point>20 20 0.02</point>
</road>

	<!-- A houses-->
	<include>
  	<static>true</static>
		<uri>model://house_3</uri>
	<pose>-4 13 0.5 0 0 1.6</pose>
	</include>
</world>
</sdf>
</pre>


![World](https://roboticslaburjc.github.io/2016-tfg-vanessa-fernandez/images/car_house.png)



