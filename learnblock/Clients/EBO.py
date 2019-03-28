#!/usr/bin/env python
# -*- coding: utf-8 -*-
from learnblock.Clients.Client import *
import os, Ice, numpy as np, PIL.Image as Image, io, paho.mqtt.client
import learnbot_dsl.Clients.Devices as Devices

ROBOCOMP = ''
try:
    ROBOCOMP = os.environ['ROBOCOMP']
except KeyError:
    print('$ROBOCOMP environment variable not set, using the default value /opt/robocomp')
    ROBOCOMP = os.path.join('opt', 'robocomp')

ICEs = ["Laser.ice", "DifferentialRobot.ice", "JointMotor.ice", "EmotionalMotor.ice", "GenericBase.ice"]
icePaths = []
icePaths.append("/home/ivan/robocomp/components/learnbot/learnbot_dsl/interfaces")
for ice in ICEs:
    for p in icePaths:
        if os.path.isfile(os.path.join(p, ice)):
            wholeStr = ' -I' + p + " --all " + os.path.join(p, ice)
            Ice.loadSlice(wholeStr)
            break

import RoboCompLaser, RoboCompDifferentialRobot, RoboCompJointMotor, RoboCompGenericBase, RoboCompEmotionalMotor


class Robot(Client):
    devicesAvailables = ["base", "camera", "display", "distancesensors", "jointmotor"]

    def __init__(self):
        Client.__init__(self)
        try:
            # self.client = paho.mqtt.client.Client(client_id='learnbotClient', clean_session=False)
            self.client = paho.mqtt.client.Client()
            self.client.on_message = self.on_message
            self.client.connect(host='192.168.16.1', port=50000)
            self.client.subscribe(topic='camara', qos=2)
            self.client.loop_start()
            print("Streamer iniciado correctamente")
        except Exception as e:
            print("Error connect Streamer\n", e)
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

    def on_message(self, client, userdata, message):
        self.newImage = True
        data = message.payload
        image_stream = io.BytesIO()
        image_stream.write(data)
        image = Image.open(image_stream)
        self.open_cv_image = np.array(image)

    def connectToRobot(self):
        self.laser_proxy = connectICEProxy("laser:tcp -h 192.168.16.1 -p 10104", RoboCompLaser.LaserPrx)
        self.differentialrobot_proxy = connectICEProxy("differentialrobot:tcp -h 192.168.16.1 -p 10004",
                                                        RoboCompDifferentialRobot.DifferentialRobotPrx)
        self.jointmotor_proxy = connectICEProxy("jointmotor:tcp -h 192.168.16.1 -p 10067",
                                                 RoboCompJointMotor.JointMotorPrx)
        self.emotionalmotor_proxy = connectICEProxy("emotionalmotor:tcp -h 192.168.16.1 -p 30001",
                                                     RoboCompEmotionalMotor.EmotionalMotorPrx)

    def deviceReadLaser(self):
        laserdata = self.laser_proxy.getLaserData()
        usList = [d.dist for d in laserdata]
        return {"front": usList[1:4],  # The values must be in mm
                "left": usList[:2],
                "right": usList[3:]}

    def deviceMove(self, _adv, _rot):
        self.differentialrobot_proxy.setSpeedBase(_adv, _rot)

    def deviceReadCamera(self, ):
        return self.open_cv_image, self.newImage

    def deviceSendEmotion(self, _emotion):
        if _emotion is Emotions.Joy:
            self.emotionalmotor_proxy.expressJoy()
        elif _emotion is Emotions.Sadness:
            self.emotionalmotor_proxy.expressSadness()
        elif _emotion is Emotions.Surprise:
            self.emotionalmotor_proxy.expressSurprise()
        elif _emotion is Emotions.Disgust:
            self.emotionalmotor_proxy.expressDisgust()
        elif _emotion is Emotions.Anger:
            self.emotionalmotor_proxy.expressAnger()
        elif _emotion is Emotions.Fear:
            self.emotionalmotor_proxy.expressFear()
        elif _emotion is Emotions.Neutral:
            self.emotionalmotor_proxy.expressNeutral()

    def deviceSendAngleHead(self, _angle):
        goal = RoboCompJointMotor.MotorGoalPosition()
        goal.name = 'servo'
        goal.position = _angle
        self.jointmotor_proxy.setPosition(goal)


if __name__ == '__main__':
    robot = Robot()
    print(robot.__dict__)
    while True:
        if robot.obstacle_free(50):

            if not robot.am_I_turning():

                if robot.left_obstacle(50):
                    robot.turn_right()
                else:
                    robot.turn_left()

        else:
            robot.move_straight()
    ebo.join()
