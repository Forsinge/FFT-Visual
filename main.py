import tkinter as tk
from time import sleep
from numpy import sqrt, pi, sin, cos, absolute, angle
from scipy.fft import fft, fftfreq

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def abs(self):
        return sqrt(self.x * self.x + self.y * self.y)

    def add(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def dist(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return sqrt(dx * dx + dy * dy)

class Transform:
    def __init__(self, f, len, offset):
        transform_raw = fft(f)
        self.len = len
        self.frequencies = fftfreq(len)
        self.phases = angle(transform_raw)
        self.coefficients = absolute(transform_raw)/len
        self.points = [Point(0,0) for _ in range(len)]
        self.offset = offset

    def update(self, timer):
        for i in range(0, self.len):
            self.points[i] = self.getPoint(i, timer)
    
    def getPoint(self, i, timer):
        arg = timer.time() * self.frequencies[i] + self.phases[i] + self.offset
        return Point(self.coefficients[i] * cos(arg), self.coefficients[i] * sin(arg))

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
    def __init__(self):
        self.maxlen = 390   # out of 400, leaves a small gap when retracing
        self.counter = 0
        self.points = []

    
    def append(self, p):
        if (self.counter >= self.maxlen):
            self.points[self.counter % self.maxlen] = p
        else:
            self.points.append(p)
        self.counter += 1
    
    def draw(self):
        if (self.counter >= 4):
            if (self.counter > self.maxlen):
                cutoff = self.counter % self.maxlen
                rotated = self.points[cutoff:] + self.points[:cutoff]
                fftCanvas.create_line(rotated, fill='green', width=3)
            else:
                if (self.counter % 2 == 0):
                    fftCanvas.create_line(self.points, fill='green', width=3)
                else:
                    fftCanvas.create_line(self.points[:self.counter-1], fill='green', width=3)

class Timer:
    def __init__(self, len):
        self.len = len
        self.counter = 0
    
    def incr(self):
        self.counter = self.counter + 0.005 * self.len * pi

    def time(self):
        return self.counter


def drawLine(p1, p2, color, width, canvas):
    canvas.create_line((p1.x, p1.y), (p2.x, p2.y), fill=color, width=width)

def drawCircle(center, radius, color, canvas):
    canvas.create_oval(center.x-radius, center.y-radius, center.x+radius, center.y+radius, outline=color, width=1)

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
    global timer

    timer = Timer(len(userPath.points))
    fftPath = FFTPath()
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
    return (Transform(fx, len(fx), 0), Transform(fy, len(fy), pi/2))

def drawArms():
    tx.update(timer)
    ty.update(timer)

    center = tx.points[0].add(ty.points[0])

    arms = [(center.x, center.y)]
    pos = 1
    neg = tx.len-1

    stop = center
    while (neg >= pos):
        start = stop.add(tx.points[pos]).add(ty.points[pos])
        arms.append((start.x, start.y))

        radius = stop.dist(start)
        if (radius > 8):
            drawCircle(stop, radius, 'gray', fftCanvas)

        if (pos != neg):
            stop = start.add(tx.points[neg]).add(ty.points[neg]) 
            arms.append((stop.x, stop.y))
            
            radius = start.dist(stop)
            if (radius > 8):
                drawCircle(start, radius, 'gray', fftCanvas)
            
        pos += 1
        neg -= 1

    if (len(arms) % 2 == 0):
        arms.pop()
    
    fftCanvas.create_line(arms, fill='white', width=1)
    return stop

def main():
    global root, userCanvas, fftCanvas
    global appActive, dragActive
    global userPath, fftPath
    global tx, ty
    global timer

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
    fftPath = FFTPath()

    tx = Transform([0], 1, 0)
    ty = Transform([0], 1, 0)
    
    timer = Timer(1)

    while(True and appActive):
        if (tx.len > 1 and not dragActive):
            timer.incr()
            total = drawArms()
            fftPath.append((total.x, total.y))
            fftPath.draw()
            sleep(0.01)
        else:
            sleep(0.001)

        try:
            root.update()
            fftCanvas.delete("all")
        except:
            exit(1)
    
main()