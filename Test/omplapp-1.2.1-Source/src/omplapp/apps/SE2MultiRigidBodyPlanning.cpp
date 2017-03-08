/*********************************************************************
* Rice University Software Distribution License
*
* Copyright (c) 2012, Rice University
* All Rights Reserved.
*
* For a full description see the file named LICENSE.
*
*********************************************************************/

/* Author: Ryan Luna */

#include "omplapp/apps/SE2MultiRigidBodyPlanning.h"

ompl::app::SE2MultiRigidBodyPlanning::SE2MultiRigidBodyPlanning(unsigned int n) :
    AppBase<GEOMETRIC>(base::StateSpacePtr(new base::CompoundStateSpace()), Motion_2D), n_(n)
{
    assert (n > 0);
    name_ = "Multi rigid body planning (2D)";
    // Adding n SE(2) StateSpaces
    for (unsigned int i = 0; i < n_; ++i)
        si_->getStateSpace()->as<base::CompoundStateSpace>()->addSubspace(base::StateSpacePtr(new base::SE2StateSpace()), 1.0);
}

void ompl::app::SE2MultiRigidBodyPlanning::inferEnvironmentBounds(void)
{
    // Infer bounds for all n SE(2) spaces
    for (unsigned int i = 0; i < n_; ++i)
        InferEnvironmentBounds(getGeometricComponentStateSpace(i), *static_cast<RigidBodyGeometry*>(this));
}

void ompl::app::SE2MultiRigidBodyPlanning::inferProblemDefinitionBounds(void)
{
    // Make sure that all n SE(2) spaces get the same bounds, if they are adjusted
    for (unsigned int i = 0; i < n_; ++i)
        InferProblemDefinitionBounds(AppTypeSelector<GEOMETRIC>::SimpleSetup::getProblemDefinition(),
                                    getGeometricStateExtractor(), factor_, add_,
                                    n_, getGeometricComponentStateSpace(i), mtype_);
}

ompl::base::ScopedState<> ompl::app::SE2MultiRigidBodyPlanning::getDefaultStartState(void) const
{
    base::ScopedState<> st(getStateSpace());
    base::CompoundStateSpace::StateType* c_st = st.get()->as<base::CompoundStateSpace::StateType>();
    for (unsigned int i = 0; i < n_; ++i)
    {
        aiVector3D s = getRobotCenter(i);
        base::SE2StateSpace::StateType* sub = c_st->as<base::SE2StateSpace::StateType>(i);
        sub->setX(s.x);
        sub->setY(s.y);
        sub->setYaw(0.0);
    }
    return st;
}

const ompl::base::State* ompl::app::SE2MultiRigidBodyPlanning::getGeometricComponentStateInternal(const ompl::base::State* state, unsigned int index) const
{
    assert (index < n_);
    const base::SE2StateSpace::StateType* st = state->as<base::CompoundStateSpace::StateType>()->as<base::SE2StateSpace::StateType>(index);
    return static_cast<const base::State*>(st);
}

