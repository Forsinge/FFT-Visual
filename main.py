from tkinter import Tk, Canvas
from time import sleep
from numpy import sqrt, pi, sin, cos, absolute, angle
from scipy.fft import fft, fftfreq

class Transform:
    def __init__(self, path):
        self.length = len(path)
        self.tx = fft([point[0] for point in path])
        self.ty = fft([point[1] for point in path])
        self.cx = absolute(self.tx)/self.length
        self.cy = absolute(self.ty)/self.length
        self.px = angle(self.tx)
        self.py = angle(self.ty)
        self.frequencies = fftfreq(self.length)
        self.angle = 0
        self.points = []

    def vector(self, i):
        arg = self.angle * self.frequencies[i]
        vx = (self.cx[i] * cos(arg + self.px[i]), self.cx[i] * sin(arg + self.px[i]))
        vy = (self.cy[i] * cos(arg + self.py[i] + pi/2), self.cy[i] * sin(arg + self.py[i] + pi/2))
        return (vx[0] + vy[0], vx[1] + vy[1])

    def update(self):
        self.angle += angularVelocity * pi
        self.points = []
        self.points.append(self.vector(0))
        
        i = 1
        while (i <= self.length-i and i <= maxComponents):
            prev = self.points[-1]
            vec = self.vector(i)
            self.points.append((prev[0] + vec[0], prev[1] + vec[1]))

            if (i != self.length-i):
                prev = self.points[-1]
                vec = self.vector(-i)
                self.points.append((prev[0] + vec[0], prev[1] + vec[1]))

            i += 1
    
class LeftCanvas:
    def __init__(self, root, w, h):
        self.path = []
        self.newPath = False
        self.dragActive = False
        self.canvas = Canvas(root, width=w/2, height=h-5, bg='black')
        self.canvas.grid(row=0, column=0)
        self.canvas.bind('<ButtonPress>', self.onMousePress)
        self.canvas.bind('<Motion>', self.onMouseDrag)
        self.canvas.bind('<ButtonRelease>', self.onMouseRelease)

    def onMousePress(self, event):
        self.reset()
        self.dragActive = True
        self.path.append((event.x, event.y))
    
    def onMouseDrag(self, event):
        if (self.dragActive):
            self.path.append((event.x, event.y))
            if (len(self.path) > 1):
                self.canvas.create_line(self.path[-2], self.path[-1], fill='#5F9FBF', width=3)

    def onMouseRelease(self, event):
        self.newPath = True
        self.dragActive = False
        
    def reset(self):
        self.path.clear()
        self.canvas.delete("all")

class RightCanvas:
    def __init__(self, root, w, h):
        self.canvas = Canvas(root, width=w/2, height=h-5, bg='black')
        self.canvas.grid(row=0, column=1)
        self.path = []
        self.pathLength = 0
        self.cutoff = 0
        self.transform = Transform([(0, 0)])

    def update(self, leftCanvas):
        if (not leftCanvas.dragActive):
            if (leftCanvas.newPath):
                leftCanvas.newPath = False
                self.transform = Transform(leftCanvas.path)
                self.path = []
                self.pathLength = int(2 * self.transform.length / angularVelocity) - 20
                self.cutoff = 0

            elif (self.transform.length > 1):
                self.canvas.delete("all")
                self.transform.update()
                self.drawEpicycles()

                self.appendPath(self.transform.points[-1])
                rotatedPath = self.path[self.cutoff:] + self.path[:self.cutoff]
                if (len(self.path) > 1):
                    self.canvas.create_line(rotatedPath, fill='#5F9FBF', width=3)

                self.canvas.create_line(self.transform.points, fill='white', width=1)

                

    def appendPath(self, point):
        if (len(self.path) < self.pathLength):
            self.path.append(point)
        else:
            self.path[self.cutoff] = point
            self.cutoff = int((self.cutoff + 1) % self.pathLength)

    def drawEpicycles(self):
        for i in range(1, min(self.transform.length, maxComponents)):
            p1 = self.transform.points[i-1]
            p2 = self.transform.points[i]
            dx = p1[0] - p2[0]
            dy = p1[1] - p2[1]
            radius = sqrt(dx * dx + dy * dy)
            if (radius > 5):
                self.canvas.create_oval(p1[0]-radius, p1[1]-radius, p1[0]+radius, p1[1]+radius, outline='#202020', width=1)
    
def onWindowClose():
    global appActive
    appActive = False
    root.destroy()

def main():
    global appActive
    appActive = True

    global angularVelocity, maxComponents
    angularVelocity = 1.3
    maxComponents = 50

    global root
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.state("zoomed")
    root.title("FFT Visual")
    root.protocol("WM_DELETE_WINDOW", onWindowClose)
    root.update()

    w,h = root.winfo_width(), root.winfo_height()
    leftCanvas = LeftCanvas(root, w, h)
    rightCanvas = RightCanvas(root, w, h)

    while(appActive):
        sleep(0.005)
        rightCanvas.update(leftCanvas)
        root.update()

main()
