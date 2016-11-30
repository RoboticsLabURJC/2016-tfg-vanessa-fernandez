#include "sensors.h"

Sensors::Sensors(Ice::CommunicatorPtr ic)
{
    this-> ic = ic;
    Ice::PropertiesPtr prop = ic->getProperties();

    ////////////////////////////// Pose3D //////////////////////////////
    // Contact to POSE3D interface
    Ice::ObjectPrx basePose3D = ic->propertyToProxy("kobukiViewer.Pose3D.Proxy");
    if (0 == basePose3D) {
		pose3dON = false;
		std::cout << "Pose3D configuration not specified" <<std::endl;
        //throw "Could not create proxy with pose3D";
	}else{
		// Cast to pose3D
		try {
			p3dprx = jderobot::Pose3DPrx::checkedCast(basePose3D);
			if (0 == p3dprx)
				throw "Invalid proxy kobukiViewer.Pose3D.Proxy";

			pose3dON = true;
			std::cout << "Pose3D connected" << std::endl;
		}catch (Ice::ConnectionRefusedException& e){
			pose3dON=false;
			std::cout << "Pose3D inactive" << std::endl;
		}
	}


    ////////////////////////////// CAMERA1 /////////////////////////////

	jderobot::ImageDataPtr data;

    Ice::ObjectPrx baseCamera1 = ic->propertyToProxy("kobukiViewer.Camera1.Proxy");
    if (0==baseCamera1) {
		camera1ON = false;
		image1.create(400, 400, CV_8UC3);
		std::cout << "Camera1 configuration not specified" <<std::endl;
      //throw "Could not create proxy";
	}else{
    /*cast to CameraPrx*/
	try {
		camera1 = jderobot::CameraPrx::checkedCast(baseCamera1);
		if (0==camera1)
		  throw "Invalid proxy";

		camera1ON = true;
		std::cout << "Camera1 connected" << std::endl;

		data = camera1->getImageData(camera1->getImageFormat().at(0));
		image1.create(data->description->height, data->description->width, CV_8UC3);
	}catch (Ice::ConnectionRefusedException& e){
		camera1ON=false;
		std::cout << "Camera1 inactive" << std::endl;

		//create an empty image if no camera connected (avoid seg. fault)
		image1.create(400, 400, CV_8UC3);
	}}

    ////////////////////////////// CAMERA2 /////////////////////////////
	Ice::ObjectPrx baseCamera2 = ic->propertyToProxy("kobukiViewer.Camera2.Proxy");
    if (0==baseCamera2) {
		camera2ON = false;
		image2.create(400, 400, CV_8UC3);
		std::cout << "Camera2 configuration not specified" <<std::endl;
      //throw "Could not create proxy";
	}else{
    /*cast to CameraPrx*/
	try {
		camera2 = jderobot::CameraPrx::checkedCast(baseCamera2);
		if (0==camera2)
		  throw "Invalid proxy";

		camera2ON = true;
		std::cout << "Camera2 connected" << std::endl;

		data = camera2->getImageData(camera2->getImageFormat().at(0));
		image2.create(data->description->height, data->description->width, CV_8UC3);
	}catch (Ice::ConnectionRefusedException& e){
		camera2ON=false;
		std::cout << "Camera2 inactive" << std::endl;

		//create an empty image if no camera connected (avoid seg. fault)
		image2.create(400, 400, CV_8UC3);
	}}

    ////////////////////////////// LASER //////////////////////////////
	// Contact to LASER interface
    laserICE = ic->propertyToProxy("kobukiViewer.Laser1.Proxy");
    if (0 == laserICE) {
		laser1ON = false;
		std::cout << "Laser configuration not specified" <<std::endl;
        //throw "Could not create proxy with Laser";
	}else{
    // Cast to LASER
	try {
		laserprx1 = jderobot::LaserPrx::checkedCast(laserICE);
		if (0 == laserprx1){
		   throw std::string("Invalid proxy kobukiViewer.Laser1.Proxy");
		}

		laser1ON = true;
		std::cout << "Laser connected" << std::endl;
	}catch (Ice::ConnectionRefusedException& e){
		laser1ON=false;
		std::cout << "Laser inactive" << std::endl;
	}}
	
	// Contact to LASER interface
    laserICE = ic->propertyToProxy("kobukiViewer.Laser2.Proxy");
    if (0 == laserICE) {
		laser2ON = false;
		std::cout << "Laser configuration not specified" <<std::endl;
        //throw "Could not create proxy with Laser";
	}else{
    // Cast to LASER
	try {
		laserprx2 = jderobot::LaserPrx::checkedCast(laserICE);
		if (0 == laserprx2){
		   throw std::string("Invalid proxy kobukiViewer.Laser2.Proxy");
		}

		laser2ON = true;
		std::cout << "Laser connected" << std::endl;
	}catch (Ice::ConnectionRefusedException& e){
		laser2ON=false;
		std::cout << "Laser inactive" << std::endl;
	}}

    // Contact to LASER interface
    laserICE = ic->propertyToProxy("kobukiViewer.Laser3.Proxy");
    if (0 == laserICE) {
		laser3ON = false;
		std::cout << "Laser configuration not specified" <<std::endl;
        //throw "Could not create proxy with Laser";
	}else{
    // Cast to LASER
	try {
		laserprx3 = jderobot::LaserPrx::checkedCast(laserICE);
		if (0 == laserprx3){
		   throw std::string("Invalid proxy kobukiViewer.Laser3.Proxy");
		}

		laser3ON = true;
		std::cout << "Laser connected" << std::endl;
	}catch (Ice::ConnectionRefusedException& e){
		laser3ON=false;
		std::cout << "Laser inactive" << std::endl;
	}}


    /*boolLaser = prop->getPropertyAsInt("kobukiViewer.Laser");

    std::cout << "Laser " <<  boolLaser << std::endl;
    if(boolLaser){
        // Contact to LASER interface
        Ice::ObjectPrx laserICE = ic->propertyToProxy("kobukiViewer.Laser.Proxy");
        if (0 == laserICE)
            throw "Could not create proxy with Laser";

        // Cast to LASER
        laserprx = jderobot::LaserPrx::checkedCast(laserICE);
        if (0 == laserprx){
           throw std::string("Invalid proxy kobukiViewer.Laser.Proxy");
        }
    }*/
}

cv::Mat Sensors::getCamera1()
{
    mutex.lock();
    cv::Mat result = image1.clone();
    mutex.unlock();
    return result;

}

cv::Mat Sensors::getCamera2()
{
    mutex.lock();
    cv::Mat result = image2.clone();
    mutex.unlock();
    return result;
}

void Sensors::update()
{
	if (pose3dON) {
    	pose3ddata = this->p3dprx->getPose3DData();
	    mutex.lock();
		robotx = pose3ddata->x;
		roboty = pose3ddata->y;

		//theta
		double magnitude,w,x,y,z,squ,sqx,sqy,sqz;
		magnitude = sqrt(this->pose3ddata->q0 * this->pose3ddata->q0 + this->pose3ddata->q1 * this->pose3ddata->q1 + this->pose3ddata->q2 * this->pose3ddata->q2 + this->pose3ddata->q3 * this->pose3ddata->q3);

		w = this->pose3ddata->q0 / magnitude;
		x = this->pose3ddata->q1 / magnitude;
		y = this->pose3ddata->q2 / magnitude;
		z = this->pose3ddata->q3 / magnitude;

		squ = w * w;
		sqx = x * x;
		sqy = y * y;
		sqz = z * z;

		double angle;

		angle = atan2( 2 * (x * y + w * z), squ + sqx - sqy - sqz) * 180.0 / M_PI;

		if(angle < 0)
		{
		    angle += 360.0;
		}

		this->robottheta = angle;

	    mutex.unlock();
	}

	if (camera1ON) {
	    jderobot::ImageDataPtr data = camera1->getImageData(camera1->getImageFormat().at(0));
		mutex.lock();
	    memcpy((unsigned char *) image1.data ,&(data->pixelData[0]), image1.cols*image1.rows * 3);
		mutex.unlock();
	}

	if (camera2ON) {
	    jderobot::ImageDataPtr data2 = camera2->getImageData(camera2->getImageFormat().at(0));
		mutex.lock();
	    memcpy((unsigned char *) image2.data ,&(data2->pixelData[0]), image2.cols*image2.rows * 3);
	    mutex.unlock();
	}

	if (laser1ON) {
		ld1 = laserprx1->getLaserData();
		mutex.lock();
		laserData1.resize(ld1->numLaser);
        for(int i = 0; i< ld1->numLaser; i++ ){
            laserData1[i] = ld1->distanceData[i];
        }
		mutex.unlock();
	}
	
	if (laser2ON) {
		ld2 = laserprx2->getLaserData();
		mutex.lock();
		laserData2.resize(ld2->numLaser);
        for(int i = 0; i< ld2->numLaser; i++ ){
            laserData2[i] = ld2->distanceData[i];
        }
		mutex.unlock();
	}
	
	if (laser3ON) {
		ld3 = laserprx3->getLaserData();
		mutex.lock();
		laserData3.resize(ld3->numLaser);
        for(int i = 0; i< ld3->numLaser; i++ ){
            laserData3[i] = ld3->distanceData[i];
        }
		mutex.unlock();
	}

    
}

float Sensors::getRobotPoseX()
{

	float x;
	mutex.lock();
	if (pose3dON) 
	    x = this->robotx;
   	else
		x = 0;
	mutex.unlock();

    return x;
}

float Sensors::getRobotPoseY()
{
    float y;
	mutex.lock();
	if (pose3dON) 
	    y = this->roboty;
   	else
		y = 0;
	mutex.unlock();

    return y;
}

float Sensors::getRobotPoseTheta()
{
    float theta;
	mutex.lock();
	if (pose3dON) 
	    theta = this->robottheta;
   	else
		theta = 0;
	mutex.unlock();

    return theta;
}

std::vector<float> Sensors::getLaserData(int num)
{
    std::vector<float> laserDataAux;
    mutex.lock();
	if (laser1ON && num == 1)
	    laserDataAux = laserData1;
	else if (laser2ON && num == 2)
	    laserDataAux = laserData2;
	else if (laser3ON && num == 3)
	    laserDataAux = laserData3;
	else
		laserDataAux = {0};
    mutex.unlock();
    return laserDataAux;
}

