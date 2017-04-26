#include <boost/bind.hpp>
#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <stdio.h>
#include <iostream>

namespace gazebo
{
  	class ModelPush : public ModelPlugin {

		private: math::Pose pose;

  		public: void Load(physics::ModelPtr _parent, sdf::ElementPtr ) {
      			this->model = _parent;
	  		this->updateConnection = event::Events::ConnectWorldUpdateBegin(
          		boost::bind(&ModelPush::OnUpdate, this, _1));
			std::cout << "Loading carplugin dummy" << std::endl;
		}

    		public: void OnUpdate(const common::UpdateInfo & ) {
			pose = this->model->GetWorldPose();
		
  			
  			if (pose.pos.y <= 0){
  			    this->model->SetLinearVel(math::Vector3(10, 0, 0));
      			if ( pose.pos.x >=50 ) {
			        pose.pos.x = -50;
			        this->model->SetWorldPose(pose);
			    }
			}
			
			if (pose.pos.y >= 0){
			    this->model->SetLinearVel(math::Vector3(-5, 0, 0));
      			if ( pose.pos.x <= -50 ) {
			        pose.pos.x = 50;
			        this->model->SetWorldPose(pose);
			    }
			}	

		}
		private: physics::ModelPtr model;
		private: event::ConnectionPtr updateConnection;
  	};
  	GZ_REGISTER_MODEL_PLUGIN(ModelPush)
}
