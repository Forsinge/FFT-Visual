import time
import tkinter as tk
import numpy as np
from scipy.fft import fft, fftfreq, fftshift

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def abs(self):
        return np.sqrt(self.x * self.x + self.y * self.y)

class Transform:
    def __init__(self, f, len, offset):
        transform_raw = fft(f)
        self.len = len
        self.frequencies = fftfreq(len)
        self.phases = np.angle(transform_raw)
        self.coefficients = np.absolute(transform_raw)/len
        self.points = [Point(0,0) for _ in range(len)]
        self.offset = offset

    def update(self):
        for i in range(0, self.len):
            self.points[i] = self.getPoint(i)
    
    def getPoint(self, i):
        arg = (time.time()*150) * self.frequencies[i] + self.phases[i] + self.offset
        return Point(self.coefficients[i] * np.cos(arg), self.coefficients[i] * np.sin(arg))

class UserPath:
    def __init__(self):
        self.counter = 0
        self.points = []

    def append(self, p):
        self.points.append(p)
        if (self.counter != 0):
            drawLine(self.points[self.counter-1], self.points[self.counter], 'red', 2, userCanvas)
        self.counter += 1
        
    def reset(self):
        if (self.counter != 0):
            userCanvas.delete("all")
        self.points.clear()
        self.counter = 0

class FFTPath:
    def __init__(self, len):
        self.len = len
        self.counter = 0
        self.points = [Point(0, 0) for _ in range(len)]
    
    def append(self, p):
        self.points[self.counter] = p
        self.counter = (self.counter+1) % self.len
    
    def draw(self):
        for i in range(0, self.len-1):
            if (i+1 != self.counter):
                fr = self.points[i]
                to = self.points[i+1]
                if (fr.abs() != 0 and to.abs() != 0):
                    drawLine(fr, to, 'green', 3, fftCanvas)
        if (self.counter != 0 and self.points[self.len-1].abs() != 0):
            drawLine(self.points[self.len-1], self.points[0], 'green', 3, fftCanvas)


def drawLine(p1, p2, color, width, canvas):
    canvas.create_line((p1.x, p1.y), (p2.x, p2.y), fill=color, width=width)

def addPoints(p1, p2):
    return Point(p1.x + p2.x, p1.y + p2.y)

def quitCallback():
    global appActive
    appActive = False
    root.after(100, root.destroy())

def mousePress(event):
    global dragActive
    dragActive = True
    p = Point(event.x, event.y)
    userPath.reset()
    userPath.append(p)

def mouseDrag(event):
    if (dragActive):
        p = Point(event.x, event.y)
        userPath.append(p)

def mouseRelease(event):
    global dragActive
    global tx, ty
    global fftPath

    pathLen = len(userPath.points)
    if (pathLen % 2 == 0):
        userPath.points.append(userPath.points[pathLen-1])

    fftPath = FFTPath(len(userPath.points))
    dragActive = False
    fftCanvas.delete("all")
    (a, b) = getTransforms(userPath.points)
    tx = a
    ty = b
    

def getTransforms(path):
    fx = []
    fy = []
    for i in range(len(path)):
        fx.append(path[i].x)
        fy.append(path[i].y)
    return (Transform(fx, len(fx), 0), Transform(fy, len(fy), np.pi/2))

def drawArms():
    tx.update()
    ty.update()
    fr = addPoints(tx.points[0], ty.points[0]) # start from center of drawing

    pos = 1
    neg = tx.len-1

    while (neg >= pos):
        to = addPoints(fr, tx.points[pos])
        drawLine(fr, to, 'white', 1, fftCanvas)
        fr = to

        to = addPoints(fr, ty.points[pos])
        drawLine(fr, to, 'white', 1, fftCanvas)
        fr = to

        if (pos != neg):
            to = addPoints(fr, tx.points[neg])
            drawLine(fr, to, 'white', 1, fftCanvas)
            fr = to

            to = addPoints(fr, ty.points[neg])
            drawLine(fr, to, 'white', 1, fftCanvas)
            fr = to

        pos += 1
        neg -= 1

    return fr

def main():
    global root, userCanvas, fftCanvas
    global appActive, dragActive
    global userPath, fftPath
    global tx, ty

    appActive = True
    dragActive = False
    
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.protocol("WM_DELETE_WINDOW", quitCallback)
    root.geometry('1600x800')
    root.title("DFT Visual")

    userCanvas = tk.Canvas(root, width=800, height=800, bg='black')
    userCanvas.grid(row=0, column=0)
    userCanvas.bind('<ButtonPress>', mousePress)
    userCanvas.bind('<Motion>', mouseDrag)
    userCanvas.bind('<ButtonRelease>', mouseRelease)

    fftCanvas = tk.Canvas(root, width=800, height=800, bg='black')
    fftCanvas.grid(row=0, column=1)

    userPath = UserPath()
    fftPath = FFTPath(1)

    tx = Transform([0], 1, 0)
    ty = Transform([0], 1, 0)
    
    while(True and appActive):
        if (tx.len > 1):
            total = drawArms()
            fftPath.append(total)
            fftPath.draw()
        
        time.sleep(0.01)
        try:
            root.update()
            fftCanvas.delete("all")
        except:
            exit(1)
    
main()