import os, json

from learnblock import PATHAPRILDICT


def getAprilTextDict():
    if os.path.exists(PATHAPRILDICT):
        with open(PATHAPRILDICT, "r") as f:
            dictAprilTags = json.load(f)
        return dictAprilTags
    return {}
