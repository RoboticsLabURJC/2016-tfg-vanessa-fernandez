/*********************************************************************
* Software License Agreement (BSD License)
*
*  Copyright (c) 2013, Willow Garage
*  All rights reserved.
*
*  Redistribution and use in source and binary forms, with or without
*  modification, are permitted provided that the following conditions
*  are met:
*
*   * Redistributions of source code must retain the above copyright
*     notice, this list of conditions and the following disclaimer.
*   * Redistributions in binary form must reproduce the above
*     copyright notice, this list of conditions and the following
*     disclaimer in the documentation and/or other materials provided
*     with the distribution.
*   * Neither the name of Willow Garage nor the names of its
*     contributors may be used to endorse or promote products derived
*     from this software without specific prior written permission.
*
*  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
*  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
*  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
*  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
*  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
*  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
*  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
*  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
*  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
*  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
*  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
*  POSSIBILITY OF SUCH DAMAGE.
*********************************************************************/

/* Author: Ioan Sucan */

#define BOOST_TEST_MODULE "PlannerTerminationCondition"
#include <boost/test/unit_test.hpp>
#include <iostream>
#include <thread>

#include "ompl/base/PlannerTerminationCondition.h"
#include "ompl/util/Time.h"

#include "../BoostTestTeamCityReporter.h"

using namespace ompl;

BOOST_AUTO_TEST_CASE(TestSimpleTermination)
{
  static const double dt = 0.1;
  const base::PlannerTerminationCondition &ptc = base::timedPlannerTerminationCondition(dt);
  BOOST_CHECK(ptc == false);
  BOOST_CHECK(ptc() == false);
  std::this_thread::sleep_for(ompl::time::seconds(dt + 0.01));
  BOOST_CHECK(ptc == true);
  BOOST_CHECK(ptc() == true);

  const base::PlannerTerminationCondition &ptc_long = base::timedPlannerTerminationCondition(100.0 * dt);
  BOOST_CHECK(ptc_long == false);
  BOOST_CHECK(ptc_long() == false);
  ptc_long.terminate();
  BOOST_CHECK(ptc_long == true);
  BOOST_CHECK(ptc_long() == true);
}

BOOST_AUTO_TEST_CASE(TestThreadedTermination)
{
  static const double dt = 0.2;
  static const double interval = 0.005;
  const base::PlannerTerminationCondition &ptc = base::timedPlannerTerminationCondition(dt, interval);
  BOOST_CHECK(ptc == false);
  BOOST_CHECK(ptc() == false);
  std::this_thread::sleep_for(ompl::time::seconds(dt + interval * 3.0));
  BOOST_CHECK(ptc == true);
  BOOST_CHECK(ptc() == true);

  const base::PlannerTerminationCondition &ptc_long = base::timedPlannerTerminationCondition(100.0 * dt, interval);
  BOOST_CHECK(ptc_long == false);
  BOOST_CHECK(ptc_long() == false);
  ptc_long.terminate();
  BOOST_CHECK(ptc_long == true);
  BOOST_CHECK(ptc_long() == true);
}
