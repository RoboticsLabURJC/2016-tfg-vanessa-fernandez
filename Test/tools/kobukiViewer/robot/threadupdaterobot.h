#ifndef THREADUPDATEROBOT_H
#define THREADUPDATEROBOT_H

#include <QtWidgets>

#include <iostream>
#include <sys/time.h>

#include "robot.h"
#include "../gui/stategui.h"

#define cycle_update_robot 20 //miliseconds


class ThreadUpdateRobot:public QThread
{
public:
    ThreadUpdateRobot(Robot *robot, StateGUI* state);

private:
    Robot *robot;
    StateGUI* state;

protected:
    void run();
};

#endif // THREADUPDATEROBOT_H
