#ifndef GUI_H
#define GUI_H

#include <QtWidgets>

#include "../robot/robot.h"
#include "stategui.h"

#include "widget/controlvw.h"
#include "widget/cameraswidget.h"
#include "widget/glwidget.h"
#include "widget/laserwidget.h"

#include "../depuratewindow.h"

class GUI:public QWidget
{
    Q_OBJECT

public:
    GUI(Robot* robot, StateGUI* state, Ice::CommunicatorPtr ic);
    void updateThreadGUI();

private:
    QPushButton* buttonStopRobot;

    controlVW* canvasVW;
    CamerasWidget* camerasWidget;
    GLWidget* glwidget;
    LaserWidget* laserWidget1;
    LaserWidget* laserWidget2;
    LaserWidget* laserWidget3;
    DepurateWindow* depurateWindow;

    Robot* robot;
    StateGUI* state;

    QCheckBox* check3DWorld;
    QCheckBox* checkCameras;
    QCheckBox* checkLaser;

    QLabel* currentV;
    QLabel* currentW;
    QLabel* InfoCurrentV;
    QLabel* InfoCurrentW;


signals:
    void signal_updateGUI();

public slots:
    void on_updateGUI_recieved();
    void on_buttonStopRobot_clicked();

    void on_update_canvas_recieved(float v, float w);
    void on_checks_changed();

};

#endif // GUI_H
