from learnblock.utils.point import Point
import copy
def bezier(p1: Point, p2: Point, t):
    diff = p2-p1
    return diff * t

def getPointsBezier(points):
    bezierPoints = list()
    pointsCopy = copy.copy(points)
    for t in [x / 50. for x in range(51)]:
        while len(points) != 1:
            newPoints = list()
            p1 = points[0]
            for p2 in points[1:]:
                newPoints.append(bezier(p1, p2, t))
                p1 = p2
            points = newPoints
        bezierPoints.append(tuple(points[0]))
        points = pointsCopy
    return bezierPoints