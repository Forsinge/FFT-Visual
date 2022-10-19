import time
import tkinter as tk
import numpy as np
from scipy.fft import fft

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

class Transform:
    def __init__(self, f, len):
        self.len = len
        self.frequencies = np.concatenate([np.arange(0, np.ceil(len/2)), np.arange(np.ceil(-len/2), 0)])
        transform_raw = fft(f)
        self.phases = np.arctan2(transform_raw.imag, transform_raw.real) * 180/np.pi
        self.coefficients = np.absolute(transform_raw/len)
        self.final = Point(0, 0)
    
    def get_point_x(self, i):
        arg = time.time() * self.frequencies[i] + self.phases[i]
        return Point(self.coefficients[i] * np.cos(arg), self.coefficients[i] * np.sin(arg))

    def get_point_y(self, i):
        arg = time.time() * self.frequencies[i] + self.phases[i]
        return Point(self.coefficients[i] * np.sin(arg), self.coefficients[i] * np.cos(arg))
    
    def draw(self):
        fr = self.get_point(0)
        for i in range(1, self.len):
            to = add(self.get_point(i), fr)
            draw_line(fr, to, 'white')
            fr = to
        self.final = fr

class PenTrace:
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
                draw_line(self.points[i], self.points[i+1], 'red')
        if (self.counter != 0):
            draw_line(self.points[self.len-1], self.points[0], 'red')


def draw_line(p1, p2, color):
    canvas.create_line((p1.x, p1.y), (p2.x, p2.y), width=2, fill=color)

def draw_components(tx, ty):
    fr = add(tx.get_point_x(0), ty.get_point_y(0))
    for i in range(1, tx.len):
        to = add(fr, tx.get_point_x(i))
        draw_line(fr, to, 'white')
        fr = to
        to = add(fr, ty.get_point_y(i))
        draw_line(fr, to, 'white')
        fr = to
    tx.final = fr
    

def add(p1, p2):
    return Point(p1.x + p2.x, p1.y + p2.y)

def quit_cb():
    global active
    active = False
    root.after(100, root.destroy())
    
def main():
    fx = [200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400, 420, 440, 460, 480,
    460, 440, 420, 400, 380, 360, 340, 320, 300, 280, 260, 240, 220, 200]
    fy = [200, 240, 280, 320, 360, 400, 440, 480, 440, 400, 360, 320, 280, 240, 200,
    240, 280, 320, 360, 400, 440, 480, 440, 400, 360, 320, 280, 240, 200]

    transform_x = Transform(fx, len(fx))
    transform_y = Transform(fy, len(fy))
    print(transform_y.coefficients)
    pen = PenTrace(200)

    global root 
    root = tk.Tk()

    global canvas
    canvas = tk.Canvas(root, width=800, height=800, bg='black')

    global increment
    increment = 0.02

    global active
    active = True
    
    root.protocol("WM_DELETE_WINDOW", quit_cb)
    root.geometry('800x800')
    root.title("DFT Visual")
    canvas.pack(anchor=tk.CENTER, expand=True)

    while(True and active):
        draw_components(transform_x, transform_y)
        pen.append(transform_x.final)
        pen.draw()
        time.sleep(increment)
        try:
            root.update()
            canvas.delete("all")
        except:
            exit(1)
        
            
main()