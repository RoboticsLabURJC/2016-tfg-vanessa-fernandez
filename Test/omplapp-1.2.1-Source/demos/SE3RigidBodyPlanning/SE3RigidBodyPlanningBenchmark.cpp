/*********************************************************************
* Rice University Software Distribution License
*
* Copyright (c) 2010, Rice University
* All Rights Reserved.
*
* For a full description see the file named LICENSE.
*
*********************************************************************/

/* Author: Ioan Sucan */

#include <omplapp/config.h>
#include <omplapp/apps/SE3RigidBodyPlanning.h>
#include <ompl/tools/benchmark/Benchmark.h>
#include <ompl/geometric/planners/rrt/RRTConnect.h>
#include <ompl/geometric/planners/rrt/RRT.h>
#include <ompl/geometric/planners/kpiece/LBKPIECE1.h>
#include <ompl/geometric/planners/kpiece/BKPIECE1.h>
#include <ompl/geometric/planners/kpiece/KPIECE1.h>
#include <ompl/geometric/planners/sbl/SBL.h>
#include <ompl/geometric/planners/est/EST.h>
#include <ompl/geometric/planners/prm/PRM.h>

#include <ompl/base/samplers/UniformValidStateSampler.h>
#include <ompl/base/samplers/GaussianValidStateSampler.h>
#include <ompl/base/samplers/ObstacleBasedValidStateSampler.h>
#include <ompl/base/samplers/MaximizeClearanceValidStateSampler.h>
using namespace ompl;

base::ValidStateSamplerPtr allocUniformStateSampler(const base::SpaceInformation *si)
{
    return base::ValidStateSamplerPtr(new base::UniformValidStateSampler(si));
}

base::ValidStateSamplerPtr allocGaussianStateSampler(const base::SpaceInformation *si)
{
    return base::ValidStateSamplerPtr(new base::GaussianValidStateSampler(si));
}

base::ValidStateSamplerPtr allocObstacleStateSampler(const base::SpaceInformation *si)
{
    return base::ValidStateSamplerPtr(new base::ObstacleBasedValidStateSampler(si));
}

base::ValidStateSamplerPtr allocMaximizeClearanceStateSampler(const base::SpaceInformation *si)
{
    base::MaximizeClearanceValidStateSampler *s = new base::MaximizeClearanceValidStateSampler(si);
    s->setNrImproveAttempts(5);
    return base::ValidStateSamplerPtr(s);
}

void benchmark0(std::string& benchmark_name, app::SE3RigidBodyPlanning& setup,
                double& runtime_limit, double& memory_limit, int& run_count)
{
    benchmark_name = std::string("cubicles");
    std::string robot_fname = std::string(OMPLAPP_RESOURCE_DIR) + "/3D/cubicles_robot.dae";
    std::string env_fname = std::string(OMPLAPP_RESOURCE_DIR) + "/3D/cubicles_env.dae";
    setup.setRobotMesh(robot_fname.c_str());
    setup.setEnvironmentMesh(env_fname.c_str());

    base::ScopedState<base::SE3StateSpace> start(setup.getSpaceInformation());
    start->setX(-4.96);
    start->setY(-40.62);
    start->setZ(70.57);
    start->rotation().setIdentity();

    base::ScopedState<base::SE3StateSpace> goal(start);
    goal->setX(200.49);
    goal->setY(-40.62);
    goal->setZ(70.57);
    goal->rotation().setIdentity();

    setup.setStartAndGoalStates(start, goal);
    setup.getSpaceInformation()->setStateValidityCheckingResolution(0.01);
    setup.getSpaceInformation()->setValidStateSamplerAllocator(&allocUniformStateSampler);
    setup.setup();

    std::vector<double> cs(3);
    cs[0] = 35; cs[1] = 35; cs[2] = 35;
    setup.getStateSpace()->getDefaultProjection()->setCellSizes(cs);

    runtime_limit = 10.0;
    memory_limit  = 10000.0; // set high because memory usage is not always estimated correctly
    run_count     = 500;
}

void benchmark1(std::string& benchmark_name, app::SE3RigidBodyPlanning& setup,
                double& runtime_limit, double& memory_limit, int& run_count)
{
    benchmark_name = std::string("Twistycool");
    std::string robot_fname = std::string(OMPLAPP_RESOURCE_DIR) + "/3D/Twistycool_robot.dae";
    std::string env_fname = std::string(OMPLAPP_RESOURCE_DIR) + "/3D/Twistycool_env.dae";
    setup.setRobotMesh(robot_fname.c_str());
    setup.setEnvironmentMesh(env_fname.c_str());

    base::ScopedState<base::SE3StateSpace> start(setup.getSpaceInformation());
    start->setX(270.);
    start->setY(160.);
    start->setZ(-200.);
    start->rotation().setIdentity();

    base::ScopedState<base::SE3StateSpace> goal(start);
    goal->setX(270.);
    goal->setY(160.);
    goal->setZ(-400.);
    goal->rotation().setIdentity();

    base::RealVectorBounds bounds(3);
    bounds.setHigh(0,350.);
    bounds.setHigh(1,250.);
    bounds.setHigh(2,-150.);
    bounds.setLow(0,200.);
    bounds.setLow(1,75.);
    bounds.setLow(2,-450.);
    setup.getStateSpace()->as<base::SE3StateSpace>()->setBounds(bounds);

    setup.setStartAndGoalStates(start, goal);
    setup.getSpaceInformation()->setStateValidityCheckingResolution(0.01);

    runtime_limit = 60.0;
    memory_limit  = 10000.0; // set high because memory usage is not always estimated correctly
    run_count     = 50;
}

void preRunEvent(const base::PlannerPtr& /*planner*/)
{
}

void postRunEvent(const base::PlannerPtr& /*planner*/, tools::Benchmark::RunProperties& /*run*/)
{
}

int main(int argc, char **argv)
{
    app::SE3RigidBodyPlanning setup;
    std::string benchmark_name;
    double runtime_limit, memory_limit;
    int run_count;
    int benchmark_id = argc > 1 ? ((argv[1][0] - '0') % 2) : 0;

    if (benchmark_id==0)
        benchmark0(benchmark_name, setup, runtime_limit, memory_limit, run_count);
    else
        benchmark1(benchmark_name, setup, runtime_limit, memory_limit, run_count);

    // create the benchmark object and add all the planners we'd like to run
    tools::Benchmark::Request request(runtime_limit, memory_limit, run_count);
    tools::Benchmark b(setup, benchmark_name);

    // optionally set pre & pos run events
    b.setPreRunEvent(std::bind(&preRunEvent, std::placeholders::_1));
    b.setPostRunEvent(std::bind(&postRunEvent, std::placeholders::_1, std::placeholders::_2));

    b.addPlanner(base::PlannerPtr(new geometric::RRTConnect(setup.getSpaceInformation())));
    b.addPlanner(base::PlannerPtr(new geometric::RRT(setup.getSpaceInformation())));
    b.addPlanner(base::PlannerPtr(new geometric::BKPIECE1(setup.getSpaceInformation())));
    b.addPlanner(base::PlannerPtr(new geometric::LBKPIECE1(setup.getSpaceInformation())));
    b.addPlanner(base::PlannerPtr(new geometric::KPIECE1(setup.getSpaceInformation())));
    b.addPlanner(base::PlannerPtr(new geometric::SBL(setup.getSpaceInformation())));
    b.addPlanner(base::PlannerPtr(new geometric::EST(setup.getSpaceInformation())));
    b.addPlanner(base::PlannerPtr(new geometric::PRM(setup.getSpaceInformation())));

    int sampler_id = argc > 2 ? ((argv[2][0] - '0') % 4) : -1;

    if (sampler_id == 0 || sampler_id < 0)
    {
        // run all planners with a uniform valid state sampler on the benchmark problem
        setup.getSpaceInformation()->setValidStateSamplerAllocator(&allocUniformStateSampler);
        b.setExperimentName(benchmark_name + "_uniform_sampler");
        b.benchmark(request);
        b.saveResultsToFile();
    }

    if (sampler_id == 1 || sampler_id < 0)
    {
        // run all planners with a Gaussian valid state sampler on the benchmark problem
        setup.getSpaceInformation()->setValidStateSamplerAllocator(&allocGaussianStateSampler);
        b.setExperimentName(benchmark_name + "_gaussian_sampler");
        b.benchmark(request);
        b.saveResultsToFile();
    }

    if (sampler_id == 2 || sampler_id < 0)
    {
        // run all planners with a obstacle-based valid state sampler on the benchmark problem
        setup.getSpaceInformation()->setValidStateSamplerAllocator(&allocObstacleStateSampler);
        b.setExperimentName(benchmark_name + "_obstaclebased_sampler");
        b.benchmark(request);
        b.saveResultsToFile();
    }

    if (sampler_id == 3 || sampler_id < 0)
    {
        // run all planners with a maximum-clearance valid state sampler on the benchmark problem
        setup.getSpaceInformation()->setValidStateSamplerAllocator(&allocMaximizeClearanceStateSampler);
        b.setExperimentName(benchmark_name + "_maxclearance_sampler");
        b.benchmark(request);
        b.saveResultsToFile();
    }

    return 0;
}
