# $1 gesture recognizer 
import math
import numpy as np
import os
import xml.etree.ElementTree as ET
from datetime import datetime

#Note:
# - I pretty much just translated the pseudo-code from: https://depts.washington.edu/acelab/proj/dollar/dollar.pdf

NUM_UNI_STROKES = 16
NUM_POINTS = 64
SQUARE_SIZE = 250
PHI = 0.5 * (-1 + math.sqrt(5))
ORIGIN = (0,0)
SAVE_PATH = "datasets/my_logs/s01/medium"

def transformForRecognition(points):
    resampled = resample(points)
    angle = indicative_angle(resampled)
    rotated = rotate_by(resampled, -angle)
    scaled = scaleTo(rotated, SQUARE_SIZE)
    translated = translateTo(scaled)

    return translated

def saveAsXml(shape_name, points, windowHeight, path = "datasets/my_logs/s01/medium"):
    if not os.path.exists(path):
        os.makedirs(path)

    points = resample(points)
    files = os.listdir(path)
    counter = 1
    for file in files:
        if shape_name in file.removesuffix(".xml"):
            counter += 1
    print(f"made {shape_name} Number: {counter}")
    filename = os.path.join(path, f"{shape_name}{counter:02d}.xml")
    gesture = ET.Element("Gesture")
    now = datetime.now()

    duration = points[-1][2]

    gesture.set("Name", shape_name)
    gesture.set("Subject", "1")
    gesture.set("Speed", "medium")
    gesture.set("Number", f"{counter}")
    gesture.set("NumPts", str(len(points)))
    gesture.set("Milliseconds", str(duration))
    gesture.set("AppName", "Gestures")
    gesture.set("AppVer", "3.5.0.0")
    gesture.set("Date", now.strftime("%A, %B %d, %Y"))
    gesture.set("TimeOfDay", now.strftime("%I:%M:%S %p"))

    for x, y, t in points:
        pt = ET.SubElement(gesture, "Point")
        pt.set("X", str(int(x//3)))
        pt.set("Y", str(int((windowHeight - y)//3)))
        pt.set("T", str(t))

    tree = ET.ElementTree(gesture)
    ET.indent(tree, space="    ", level=0)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

def recognize(points, windowHeight, path = SAVE_PATH):  
    turned_points = []
    for p in points:
        turned_points.append((p[0], windowHeight - p[1]))
    transformedShape = transformForRecognition(turned_points)
    if not os.path.exists(path):
        return None
    
    xmlFiles = os.listdir(path)
    if(len(xmlFiles) == 0): 
        return

    best_distance = float("inf")
    best_shape = None
    best_File = None
    lastName = ""

    for xmlFile in xmlFiles:
        gesture = ET.parse(f"{path}/{xmlFile}").getroot()
        shape_name = gesture.get("Name")

        #Code for ony one file getting used for predicition
        #if lastName == shape_name:
        #    continue
        #lastName = shape_name

        template = []
        for pt in gesture.findall("Point"):
            x = float(pt.get("X"))
            y = float(pt.get("Y"))
            template.append((x, y))

        
        transformedTemplate = transformForRecognition(template)

        d = distanceAtBestAngle(
            transformedShape,
            transformedTemplate,
            -math.radians(45),
            math.radians(45),
            math.radians(2)
        )

        if d < best_distance:
            best_distance = d
            best_shape = shape_name
            best_File = xmlFile
    score = 1 - best_distance / (0.5 * math.sqrt(SQUARE_SIZE**2 + SQUARE_SIZE**2))

    #print(best_File)
    return best_shape, score

def recognizeOnAll(points,path ):  
    turned_points = []
    for p in points:
        p[0] = int(p[0])
        p[1] = int(p[1])
        turned_points.append((p[0], p[1]))
    transformedShape = transformForRecognition(turned_points)
    

    best_distance = float("inf")
    best_shape = None
    best_File = None
    lastName = ""

    for parFolder in os.listdir(path):
        for folder in os.listdir(f"{path}/{parFolder}"):
            for xmlFile in os.listdir(f"{path}/{parFolder}/{folder}"):
                if "ipynb" in xmlFile:
                    continue
                gesture = ET.parse(f"{path}/{parFolder}/{folder}/{xmlFile}").getroot()
                shape_name = gesture.get("Name")

                template = []
                for pt in gesture.findall("Point"):
                    x = float(pt.get("X"))
                    y = float(pt.get("Y"))
                    template.append((x, y))

                
                transformedTemplate = transformForRecognition(template)

                d = distanceAtBestAngle(
                    transformedShape,
                    transformedTemplate,
                    -math.radians(45),
                    math.radians(45),
                    math.radians(2)
                )

                if d < best_distance:
                    best_distance = d
                    best_shape = shape_name
                    best_File = xmlFile

    score = 1 - best_distance / (0.5 * math.sqrt(SQUARE_SIZE**2 + SQUARE_SIZE**2))

    return best_shape, score

def distanceBetweenPoints(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def completeLength(points):
    total = 0
    for i in range(1, len(points)):
        total += distanceBetweenPoints(points[i - 1], points[i])

    return total

def resample(points, n=64):
    I = completeLength(points) / (n - 1)
    D = 0

    new_points = [points[0]]

    for i in range(1, len(points)):
        d = distanceBetweenPoints(points[i - 1], points[i])
        if D + d >= I:
            t = (I - D) / d

            qx = points[i - 1][0] + t * (points[i][0] - points[i - 1][0])
            qy = points[i - 1][1] + t * (points[i][1] - points[i - 1][1])

            if len(points[0]) > 2:
                q = (qx, qy, points[i][2])
            else:
                q = (qx, qy)

            new_points.append(q)
            points[i] = q
            D = 0
        else:
            D += d

    if len(new_points) == n - 1:
        new_points.append(points[-1])
         
    return new_points

#Step 2 rotation
def getCentroid(points):
    return np.mean(points, axis=0)

def indicative_angle(points):
    points = np.array(points)
    c = getCentroid(points)
    return np.arctan2(c[1] - points[0][1], c[0] - points[0][0])

def rotate_by(points, omega):
    c = getCentroid(points)

    cos_o = math.cos(omega)
    sin_o = math.sin(omega)

    rotated = []

    for x, y in points:
        dx = x - c[0]
        dy = y - c[1]

        rx = dx * cos_o - dy * sin_o + c[0]
        ry = dx * sin_o + dy * cos_o + c[1]

        rotated.append((rx, ry))

    return rotated


#Step 3 scale
def getBoundingBox(points):
    xPoints = [p[0] for p in points]
    yPoints = [p[1] for p in points]

    minX = min(xPoints)
    maxX = max(xPoints)
    minY = min(yPoints)  
    maxY = max(yPoints)

    return ((minX, minY), (maxX, maxY))

def scaleTo(points, size):
    B = getBoundingBox(points)
    scaledPoints = []
    for p in points:
        qx = p[0] * size / (B[1][0] - B[0][0])
        qy = p[1] * size / (B[1][1] - B[0][1])
        scaledPoints.append((qx,qy))
    
    return scaledPoints

def translateTo(points, k=(0,0)):
    c = getCentroid(points)
    translatedPoints = []
    for p in points:
        qx = p[0] + k[0] - c[0]
        qy = p[1] + k[1] - c[1]
        translatedPoints.append((qx,qy))

    return translatedPoints


#Step 4 recognize
def pathDistance(A, B):
    d = 0
    for a, b in zip(A, B):
        d += distanceBetweenPoints(a, b)

    return d / len(A)


def distanceAtAngle(points, template, theta):
    newPoints = rotate_by(points, theta)
    return pathDistance(newPoints, template)


def distanceAtBestAngle(points, template, theta_a=-math.radians(45), theta_b=math.radians(45), theta_delta=math.radians(2)):
    x1 = PHI * theta_a + (1 - PHI) * theta_b
    f1 = distanceAtAngle(points, template, x1)

    x2 = (1 - PHI) * theta_a + PHI * theta_b
    f2 = distanceAtAngle(points, template, x2)

    while abs(theta_b - theta_a) > theta_delta:
        if f1 < f2:
            theta_b = x2
            x2 = x1
            f2 = f1
            x1 = PHI * theta_a + (1 - PHI) * theta_b
            f1 = distanceAtAngle(points, template, x1)

        else:
            theta_a = x1
            x1 = x2
            f1 = f2
            x2 = (1 - PHI) * theta_a + PHI * theta_b
            f2 = distanceAtAngle(points, template, x2)

    return min(f1, f2)