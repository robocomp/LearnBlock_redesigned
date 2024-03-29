import threading, os, time, cv2, numpy as np
from PIL import Image, ImageDraw
from random import randint
from learnblock import path as Learnblock_Path
from learnblock.utils.Bezier import *

def getBecierConfig(old_config, config_target, t):
    config = copy.copy(old_config)
    for parte in old_config:
        for point in old_config[parte]:
            if point in ["Radio", "Radio1", "Radio2"]:
                radio = bezier((old_config[parte][point]["Value"], 0), (config_target[parte][point]["Value"], 0), t)
                config[parte][point]["Value"] = radio[0]
            else:
                p = bezier((old_config[parte][point]["x"], old_config[parte][point]["y"]),
                           (config_target[parte][point]["x"], config_target[parte][point]["y"]), t)
                config[parte][point]["x"] = p[0]
                config[parte][point]["y"] = p[1]
    return config

DEFAULTCONFIGNEUTRAL = {
    "cejaD": {"P2": {"y": 73, "x": 314},
                                  "P3": {"y": 99, "x": 355},
                                  "P1": {"y": 99, "x": 278},
                                  "P4": {"y": 94, "x": 313}
                                  },
                        "parpadoI": {"P2": {"y": 80, "x": 160},
                                     "P3": {"y": 151, "x": 214},
                                     "P1": {"y": 151, "x": 112},
                                     "P4": {"y": 80, "x": 160}},
                        "ojoI": {"Radio1": {"Value": 34},
                                 "Center": {"y": 151, "x": 161},
                                 "Radio2": {"Value": 34}},
                        "cejaI": {"P2": {"y": 73, "x": 160},
                                  "P3": {"y": 99, "x": 201},
                                  "P1": {"y": 99, "x": 122},
                                  "P4": {"y": 94, "x": 160}},
                        "ojoD": {"Radio1": {"Value": 34},
                                 "Center": {"y": 151, "x": 316},
                                 "Radio2": {"Value": 34}},
                        "boca": {"P2": {"y": 231, "x": 239},
                                 "P3": {"y": 234, "x": 309},
                                 "P1": {"y": 234, "x": 170},
                                 "P6": {"y": 242, "x": 170},
                                 "P4": {"y": 242, "x": 309},
                                 "P5": {"y": 241, "x": 239}},
                        "pupilaD": {"Radio": {"Value": 5},
                                    "Center": {"y": 151, "x": 316}},
                        "lengua": {"P2": {"y": 238, "x": 239},
                                   "P3": {"y": 238, "x": 309},
                                   "P1": {"y": 238, "x": 199},
                                   "P4": {"y": 238, "x": 273}},
                        "mejillaI": {"P2": {"y": 188, "x": 160},
                                     "P3": {"y": 187, "x": 201},
                                     "P1": {"y": 187, "x": 122},
                                     "P4": {"y": 187, "x": 160}},
                        "parpadoD": {"P2": {"y": 80, "x": 314},
                                     "P3": {"y": 151, "x": 369},
                                     "P1": {"y": 151, "x": 266},
                                     "P4": {"y": 80, "x": 313}},
                        "pupilaI": {"Radio": {"Value": 5},
                                    "Center": {"y": 151, "x": 161}},
                        "mejillaD": {"P2": {"y": 188, "x": 314},
                                     "P3": {"y": 187, "x": 355},
                                     "P1": {"y": 187, "x": 278},
                                     "P4": {"y": 187, "x": 313}}}

OFFSET = 0.06666666666666667

imgPaths = os.path.join(Learnblock_Path, 'imgs')



class Face(threading.Thread):

    def __init__(self, display_proxy):
        threading.Thread.__init__(self)
        self.img = Image.new('RGB', (480, 320), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.img)
        self.config = DEFAULTCONFIGNEUTRAL
        self.old_config = DEFAULTCONFIGNEUTRAL
        self.t = 0.9
        self.config_target = DEFAULTCONFIGNEUTRAL
        self.display_proxy = display_proxy

    def run(self):
        start = time.time()
        sec = randint(2,6)
        while True:
            print(time.time() - start, sec)
            if time.time() - start > sec:
                self.pestaneo()
                sec = randint(2, 6)
                start = time.time()
                # print("entro")
            path = self.render()
            if path is not None:
                self.display_proxy.setImageFromFile(path)

    def pestaneo(self):
        configaux = copy.copy(self.config)
        value1 = copy.copy((configaux["ojoD"]["Radio2"]["Value"]))
        value2 = copy.copy((configaux["ojoI"]["Radio2"]["Value"]))

        for t in [(x+1)/5. for x in range(5)] + sorted([(x)/5. for x in range(5)], reverse=True):
            configaux["ojoD"]["Radio2"]["Value"] = bezier((value1,0), (0,0), t)[0]
            configaux["ojoI"]["Radio2"]["Value"] = bezier((value2, 0), (0, 0), t)[0]
            # config1 = getBecierConfig(configaux, configPestaneo, t)
            self.drawConfig(configaux)
            img = np.array(self.img)
            img = cv2.flip(img, 1)
            cv2.imwrite("/tmp/ebofaceimg.png", img)
            self.display_proxy.setImageFromFile("/tmp/ebofaceimg.png")
            # time.sleep(0.01)


    def drawConfig(self, config):
        self.draw.rectangle(((0, 0), (479, 319)), fill=(255, 255, 255), outline=(255, 255, 255))
        self.renderOjo(config["ojoI"])
        self.renderOjo(config["ojoD"])
        self.renderParpado(config["parpadoI"])
        self.renderParpado(config["parpadoD"])
        self.renderCeja(config["cejaI"])
        self.renderCeja(config["cejaD"])
        self.renderBoca(config["boca"])
        self.renderPupila(config["pupilaI"])
        self.renderPupila(config["pupilaD"])
        self.renderMejilla(config["mejillaI"])
        self.renderMejilla(config["mejillaD"])
        self.renderLengua(config["lengua"])

    def render(self):
        if self.t <= 1 and self.config_target is not None:
            config = self.config = getBecierConfig(self.old_config, self.config_target, self.t)
            self.t += OFFSET
            self.drawConfig(config)
            img = np.array(self.img)
            img = cv2.flip(img, 1)
            cv2.imwrite("/tmp/ebofaceimg.png",img)
            return "/tmp/ebofaceimg.png"
        elif self.config_target is not None:
            # with self.mutex:
            self.old_config = self.config_target
            self.config_target = None
        return None

    def renderPupila(self, points):
        P1 = (points["Center"]["x"] - points["Radio"]["Value"], points["Center"]["y"] - points["Radio"]["Value"])
        P2 = (points["Center"]["x"] + points["Radio"]["Value"], points["Center"]["y"] + points["Radio"]["Value"])
        self.draw.ellipse((P1, P2), fill=(255, 255, 255), outline=(255, 255, 255))

    # self.draw.ellipse((P1, P2), fill=1)

    def renderLengua(self, points):
        P1 = (points["P1"]["x"], points["P1"]["y"])
        P2 = (points["P2"]["x"], points["P2"]["y"])
        P3 = (points["P3"]["x"], points["P3"]["y"])
        P4 = (points["P4"]["x"], points["P4"]["y"])
        self.draw.polygon(getPointsBezier([P1, P2, P3, P4]), fill=(131,131,255), outline=(0,0,0))

    def renderParpado(self, points):
        P1 = (points["P1"]["x"], points["P1"]["y"])
        P2 = (points["P2"]["x"], points["P2"]["y"])
        P3 = (points["P3"]["x"], points["P3"]["y"])
        P4 = (points["P4"]["x"], points["P4"]["y"])
        self.draw.polygon(getPointsBezier([P1, P2, P3]) + getPointsBezier([P3, P4, P1]), fill=(255, 255, 255))

    def renderMejilla(self, points):
        P1 = (points["P1"]["x"], points["P1"]["y"])
        P2 = (points["P2"]["x"], points["P2"]["y"])
        P3 = (points["P3"]["x"], points["P3"]["y"])
        P4 = (points["P4"]["x"], points["P4"]["y"])
        self.draw.polygon(getPointsBezier([P1, P2, P3]) + getPointsBezier([P3, P4, P1]), fill=(255, 255, 255))

    def renderCeja(self, points):
        P1 = (points["P1"]["x"], points["P1"]["y"])
        P2 = (points["P2"]["x"], points["P2"]["y"])
        P3 = (points["P3"]["x"], points["P3"]["y"])
        P4 = (points["P4"]["x"], points["P4"]["y"])
        self.draw.polygon(getPointsBezier([P1, P2, P3]) + getPointsBezier([P3, P4, P1]), fill=1)

    def renderOjo(self, points):
        P1 = (points["Center"]["x"] - points["Radio1"]["Value"], points["Center"]["y"] - points["Radio2"]["Value"])
        P2 = (points["Center"]["x"] + points["Radio1"]["Value"], points["Center"]["y"] + points["Radio2"]["Value"])
        # P1 = (points["P1"]["x"], points["P1"]["y"])
        # P2 = (points["P2"]["x"], points["P2"]["y"])
        self.draw.ellipse((P1, P2), fill=1)

    def renderBoca(self, points):
        P1 = (points["P1"]["x"], points["P1"]["y"])
        P2 = (points["P2"]["x"], points["P2"]["y"])
        P3 = (points["P3"]["x"], points["P3"]["y"])
        P4 = (points["P4"]["x"], points["P4"]["y"])
        P5 = (points["P5"]["x"], points["P5"]["y"])
        P6 = (points["P6"]["x"], points["P6"]["y"])
        self.draw.polygon(getPointsBezier([P1, P2, P3]) + getPointsBezier([P4, P5, P6]), fill=1, outline=10)

    def setConfig(self, config):
        # with self.mutex:
        self.config_target = config
        self.old_config = self.config
        self.t = 0.06666666666666667
        # self.start()