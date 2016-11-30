#include "gui.h"

GUI::GUI(Robot* robot, StateGUI *state, Ice::CommunicatorPtr ic)
{

    this->state = state;
    this->robot = robot;

    QGridLayout* mainLayout = new QGridLayout();
    QGridLayout* layoutControl = new QGridLayout();
    QVBoxLayout* layoutButtons = new QVBoxLayout();


    camerasWidget = new CamerasWidget(robot);
    glwidget = new GLWidget(state, robot);

    buttonStopRobot = new QPushButton("Stop Robot");
    checkLaser = new QCheckBox("Laser");
    checkCameras = new QCheckBox("Cameras");
    check3DWorld = new QCheckBox("3DWorld");

	InfoCurrentV = new QLabel("Current v (m/s):");
	InfoCurrentW = new QLabel("Current w (rad/s):");
	currentV = new QLabel("0");
	currentW = new QLabel("0");

    canvasVW = new controlVW();
    canvasVW->setIC(ic);
    laserWidget1 =new LaserWidget();
    laserWidget2 =new LaserWidget();
    laserWidget3 =new LaserWidget();

    depurateWindow = new DepurateWindow();
    state->setDepurateWindow(depurateWindow);

    int indiceFilaGui = 0;
    layoutControl->addWidget(canvasVW, 0, 0);

    layoutButtons->addWidget(InfoCurrentV, 0);
    layoutButtons->addWidget(currentV, 1);
    layoutButtons->addWidget(InfoCurrentW, 2);
    layoutButtons->addWidget(currentW, 3);

	QSpacerItem *item = new QSpacerItem(0,200, QSizePolicy::Expanding, QSizePolicy::Fixed);
	layoutButtons->addItem(item);

    layoutButtons->addWidget(buttonStopRobot, 2);
    layoutButtons->addWidget(check3DWorld, 3);
    layoutButtons->addWidget(checkCameras, 4);
    layoutButtons->addWidget(checkLaser, 5);



    mainLayout->addLayout(layoutControl, 0, 0);
    mainLayout->addLayout(layoutButtons, 0, 1);

    setLayout(mainLayout);

    setVisible(true);

    adjustSize();

    connect(this, SIGNAL(signal_updateGUI()), this, SLOT(on_updateGUI_recieved()));

    connect(buttonStopRobot, SIGNAL(clicked()),this, SLOT(on_buttonStopRobot_clicked()) );

    connect(canvasVW, SIGNAL(VW_changed(float,float)), this, SLOT(on_update_canvas_recieved(float, float)));

    connect(check3DWorld, SIGNAL(stateChanged(int)), this, SLOT(on_checks_changed()));
    connect(checkLaser, SIGNAL(stateChanged(int)), this, SLOT(on_checks_changed()));
    connect(checkCameras, SIGNAL(stateChanged(int)), this, SLOT(on_checks_changed()));

    show();

    depurateWindow->setVisible(false);

}

void GUI::on_checks_changed()
{
    glwidget->setVisible(check3DWorld->isChecked());
    camerasWidget->setVisible(checkCameras->isChecked());
    laserWidget1->setVisible(checkLaser->isChecked());
    laserWidget2->setVisible(checkLaser->isChecked());
    laserWidget3->setVisible(checkLaser->isChecked());
}

void GUI::on_update_canvas_recieved(float v, float w)
{

    this->robot->getActuators()->setMotorV((float)v);
    this->robot->getActuators()->setMotorW((float)w);
}

void GUI::on_buttonStopRobot_clicked()
{
    canvasVW->Stop();
}

void GUI::updateThreadGUI()
{
    emit signal_updateGUI();
}

void GUI::on_updateGUI_recieved()
{
    camerasWidget->update();
    glwidget->updateGL();
    laserWidget1->update(this->robot->getSensors()->getLaserData(1));
    laserWidget2->update(this->robot->getSensors()->getLaserData(2));
    laserWidget3->update(this->robot->getSensors()->getLaserData(3));
	currentV->setText( QString::number(canvasVW->getV()));
	currentW->setText( QString::number(canvasVW->getW()));
    depurateWindow->update();
}

