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
        self.frequencies = np.concatenate([np.arange(0, np.floor(len/2)), np.arange(np.floor(-len/2), 0)])
        transform_raw = fft(f)
        self.phases = np.arctan2(transform_raw.imag, transform_raw.real) * 180/np.pi
        self.coefficients = np.absolute(transform_raw/len)
        self.final = Point(0, 0)
    
    def get_point(self, i):
        arg = time.time() * self.frequencies[i] + self.phases[i]
        return Point(np.cos(arg), np.sin(arg))
    
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
    canvas.create_line((p1.x, p1.y), (p2.x, p2.y), width=1, fill=color)

def add(p1, p2):
    return Point(p1.x + p2.x, p1.y + p2.y)

def quit_cb():
    global active
    active = False
    root.after(100, root.destroy())
    
def main():
    fx = [300, 500, 300, 500, 300, 500, 300, 500, 300, 500, 300, 500, 300]
    #fy = [100, 300, 500, 700, 500, 300, 100, 100, 100, 100, 100, 100]

    transform = Transform(fx, len(fx))
    print(transform.frequencies)
    pen = PenTrace(20)

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
        transform.draw()
        pen.append(transform.final)
        pen.draw()
        time.sleep(increment)
        try:
            root.update()
            canvas.delete("all")
        except:
            exit(1)
        
            
main()