#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, Ice, numpy as np, io, cv2, threading, json
import learnbot_dsl.Clients.Devices as Devices
from learnblock.utils.RenderFace import Face
from learnblock.utils import EMOTIONSCONFIGPATH
from learnblock.Clients.Devices import *
from learnblock.Clients.Client import Client
from learnblock.utils.ConnectICEProxy import connectICEProxy


ROBOCOMP = ''
try:
    ROBOCOMP = os.environ['ROBOCOMP']
except KeyError:
    print('$ROBOCOMP environment variable not set, using the default value /opt/robocomp')
    ROBOCOMP = os.path.join('opt', 'robocomp')

ICEs = ["Laser.ice", "DifferentialRobot.ice", "JointMotor.ice", "Display.ice", "RGBD.ice", "GenericBase.ice"]
icePaths = []
icePaths.append("/home/ivan/robocomp/components/learnbot/learnbot_dsl/interfaces")
for ice in ICEs:
    for p in icePaths:
        if os.path.isfile(os.path.join(p, ice)):
            wholeStr = ' -I' + p + " --all " + os.path.join(p, ice)
            Ice.loadSlice(wholeStr)
            break

import RoboCompLaser, RoboCompDifferentialRobot, RoboCompJointMotor, RoboCompGenericBase, RoboCompDisplay, RoboCompRGBD




class Robot(Client):

    devicesAvailables = ["base", "camera", "display", "distancesensors", "jointmotor"]

    def __init__(self):
        Client.__init__(self)

        self.connectToRobot()
        self.open_cv_image = np.zeros((240, 320, 3), np.uint8)
        self.newImage = False
        self.distanceSensors = Devices.DistanceSensors(_readFunction=self.deviceReadLaser)
        self.camera = Devices.Camera(_readFunction=self.deviceReadCamera)
        self.base = Devices.Base(_callFunction=self.deviceMove)
        self.display = Devices.Display(_setEmotion=self.deviceSendEmotion, _setImage=None)
        self.addJointMotor("CAMERA",
                           _JointMotor=Devices.JointMotor(_callDevice=self.deviceSendAngleHead, _readDevice=None))
        self.start()

    def connectToRobot(self):
        self.laser_proxys = []
        # Remote object connection for Lasers

        for i in range(2, 7):
            self.laser_proxys.append(connectICEProxy("laser:tcp -h localhost -p 1010" + str(i), RoboCompLaser.LaserPrx))

        self.differentialrobot_proxy = connectICEProxy("differentialrobot:tcp -h localhost -p 10004",
                                                        RoboCompDifferentialRobot.DifferentialRobotPrx)
        self.jointmotor_proxy = connectICEProxy("jointmotor:tcp -h localhost -p 10067",
                                                 RoboCompJointMotor.JointMotorPrx)
        self.display_proxy = connectICEProxy("emotionalmotor:tcp -h localhost -p 30001",
                                                     RoboCompDisplay.DisplayPrx)
        self.rgbd_proxy = connectICEProxy("rgbd:tcp -h localhost -p 10097", RoboCompRGBD.RGBDPrx)

        self.configEmotions = {}
        self.face = Face(self.display_proxy)

        for path in os.listdir(EMOTIONSCONFIGPATH):
            if os.path.splitext(path)[1] == ".json":
                with open(os.path.join(EMOTIONSCONFIGPATH, path), "r") as f:
                    self.configEmotions[os.path.splitext(path)[0]] = json.loads(f.read())

    def deviceReadLaser(self):
        usList = []
        for prx in self.laser_proxys:
            laserdata = prx.getLaserData()
            usList.append(min([x.dist for x in laserdata]))
        print(usList)
        return {"front": usList[1:4],  # The values must be in mm
                "left": usList[:2],
                "right": usList[3:]}

    def deviceMove(self, _adv, _rot):
        self.differentialrobot_proxy.setSpeedBase(_adv, _rot)

    def deviceReadCamera(self, ):
        color, depth, headState, baseState = self.rgbd_proxy.getData()
        if (len(color) == 0) or (len(depth) == 0):
            print('Error retrieving images!')
        image = np.fromstring(color, dtype=np.uint8).reshape((240, 320, 3))
        return image, True

    def deviceSendEmotion(self, _emotion):
        if _emotion is Emotions.Joy:
            self.face.setConfig(self.configEmotions["Joy"])
        elif _emotion is Emotions.Sadness:
            self.face.setConfig(self.configEmotions["Sadness"])
        elif _emotion is Emotions.Surprise:
            self.face.setConfig(self.configEmotions["Surprise"])
        elif _emotion is Emotions.Disgust:
            self.face.setConfig(self.configEmotions["Disgust"])
        elif _emotion is Emotions.Anger:
            self.face.setConfig(self.configEmotions["Anger"])
        elif _emotion is Emotions.Fear:
            self.face.setConfig(self.configEmotions["Fear"])
        elif _emotion is Emotions.Neutral:
            self.face.setConfig(self.configEmotions["Neutral"])

    def deviceSendAngleHead(self, _angle):
        goal = RoboCompJointMotor.MotorGoalPosition()
        goal.name = 'servo'
        goal.position = _angle
        self.jointmotor_proxy.setPosition(goal)


if __name__ == '__main__':
    ebo = Robot()
    ebo.start()
    ebo.setBaseSpeed(0, 0)
    ebo.setJointAngle("CAMERA", 0.6000000238)
