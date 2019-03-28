import os, json

from PIL import ImageFont

path = os.path.dirname(os.path.realpath(__file__))
__version__ = '0.3.8'

PATHINTERFACES = os.path.join(path, "interfaces")
PATHCLIENT = os.path.join(path, "Clients")
PATHLANGUAGES = os.path.join(path, "languages")
PATHFUNCTIONSSRC = os.path.join(path, "functions", "src")
PATHFUNCTIONSCONF = os.path.join(path, "functions","configs")
PATHBLOCKSIMG = os.path.join(path, "blocks","desings")
PATHBLOCKSCONF = os.path.join(path, "blocks","configs")
PATHAPRILDICT = os.path.join(os.getenv('HOME'), ".learnblock", "AprilDict.json")
PATHFONT = os.path.join(path, "font", "BalooChettan-Regular.ttf")

textfont = ImageFont.truetype(PATHFONT, 20)


def log(func):
     def interna(*args, **kwargs):
         print("{} :LLamada con argumentos : {},{}".format(func.__name__,args, kwargs))
         return func(*args, **kwargs)
     return interna
