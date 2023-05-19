from math import ceil, log2
import os
import tempfile
import time

import pygame

class State:
    WAIT = 0
    ANIM = 1

class Sorter:
    NAME = "merge"
    
    WAIT_DUR = 0.2
    ANIM_DUR = 0.4
    
    FPS = 30
    
    def __init__(self, list_, display=True, output_video=False):
        self.original = list(list_)
        self.list = list_
        self.display = display
        self.output_video = output_video
        self.start_time = time.time()
        self.time_offset = 0
        self.steps = []
        
        self.depth = int(ceil(log2(len(self.original))))
        
        self.init_sizes()
        self.sort()
    
    def init_sizes(self):
        self.NUM_SIZE = 40
        self.SPACE = 10
        self.TOT_SIZE = self.NUM_SIZE + self.SPACE
        self.MARGIN = 20

        self.W = 2*self.MARGIN + len(self.original)*2*self.TOT_SIZE - self.SPACE
        self.H = 2*self.MARGIN + (self.depth*2 + 1)*self.TOT_SIZE - self.SPACE
    
    def time(self):
        if self.display:
            return time.time()
        
        return self.start_time + self.time_offset
    
    def draw_num(self, val, x, y, col1=(255,255,255), col2=None):
        if col2 is None:
            col2 = col1
        
        pygame.draw.rect(self.win, col1, [x, y, self.NUM_SIZE, self.NUM_SIZE], 1)
        t = self.font.render(str(val), True, col2)
        self.win.blit(t, [x + self.NUM_SIZE/2 - t.get_width()/2, y + self.NUM_SIZE/2 - t.get_height()/2])
    
    def cp_lvls(self):
        r = []
        for i in range(self.depth*2 + 1):
            l = []
            for j in range(len(self.levels[i])):
                _ = None if self.levels[i][j] is None else list(self.levels[i][j])
                l.append(_)
            r.append(l)
        
        return r
    
    def num(self, path):
        lvl = len(path)
        return sum([b * (2**(lvl - i - 1)) for i, b in enumerate(path)])
    
    def sort(self, start=0, end=None, lvl=0, path=None):
        if end is None:
            end = len(self.original)
            self.levels = [
                [None for j in range(2**int(self.depth - abs(self.depth - i)))]
                for i in range(self.depth * 2+1)
            ]
            self.levels[0][0] = list(self.original)
        
        if path is None:
            path = [0]
        
        if end-start == 1:
            return ([self.list[start]], lvl)
        
        mid = (end+start)//2
        step = {
            "levels_start": self.cp_lvls(),
            "animations": [
                {
                    "list": self.list[start:mid],
                    "origin": self.list[start:end],
                    "lvl1": lvl,
                    "i1": self.num(path),
                    "j1": 0,
                    "lvl2": lvl+1,
                    "i2": self.num(path)*2,
                    "j2": 0
                },
                {
                    "list": self.list[mid:end],
                    "origin": self.list[start:end],
                    "lvl1": lvl,
                    "i1": self.num(path),
                    "j1": mid-start,
                    "lvl2": lvl+1,
                    "i2": self.num(path)*2+1,
                    "j2": 0
                }
            ]
        }
        
        self.levels[lvl+1][self.num(path)*2] = self.list[start:mid]
        self.levels[lvl+1][self.num(path)*2+1] = self.list[mid:end]
        
        step["levels_end"] = self.cp_lvls()
        self.steps.append(step)
        
        a, lvl_a = self.sort(start, mid, lvl+1, path+[0])
        b, lvl_b = self.sort(mid, end, lvl+1, path+[1])
        
        result = []
        lvl2 = self.depth*2-lvl
        
        a_, b_ = list(a), list(b)
        ia, ib = 0, 0
        
        for i in range(end-start):
            if len(a):
                if len(b):
                    if a[0] < b[0]:
                        side = 0
                    else:
                        side = 1
                else:
                    side = 0
            else:
                side = 1
            
            s = [a, b][side]
            if side == 0: ia +=1
            else: ib +=1
            step = {
                "levels_start": self.cp_lvls(),
                "animations": [
                    {
                        "list": [s[0]],
                        "origin": list([a_, b_][side]),
                        "lvl1": [lvl_a, lvl_b][side],
                        "i1": self.num(path+[side]),
                        "j1": [ia, ib][side]-1,
                        "lvl2": lvl2,
                        "i2": self.num(path),
                        "j2": len(result),
                        "w2": end-start
                    }
                ],
                "sel_start": {
                    "lvl1": lvl_a,
                    "i1": self.num(path+[0]),
                    "j1": ia-[1,0][side],
                    "lvl2": lvl_b,
                    "i2": self.num(path+[1]),
                    "j2": ib-[0,1][side]
                },
                "sel_end": {
                    "lvl1": lvl_a,
                    "i1": self.num(path+[0]),
                    "j1": ia,
                    "lvl2": lvl_b,
                    "i2": self.num(path+[1]),
                    "j2": ib
                }
            }
            result.append(s.pop(0))
            self.levels[lvl2][self.num(path)] = list(result)+[""]*(end-start - len(result))
            step["levels_end"] = self.cp_lvls()
            self.steps.append(step)
        
        return (result, lvl2)
    
    def next_step(self):
        self.step_i += 1
        self.step = self.steps[min(self.step_i, len(self.steps)-1)]
        self.t1 = self.time()
        self.state = State.ANIM
        self.levels = self.step["levels_start"]
        if "sel_start" in self.step.keys():
            self.selection = self.step["sel_start"]
        else:
            self.selection = None
    
    def end_step(self):
        self.t1 = self.time()
        self.state = State.WAIT
        self.levels = self.step["levels_end"]
        if "sel_end" in self.step.keys():
            self.selection = self.step["sel_end"]
        else:
            self.selection = None
    
    def render(self):
        pygame.init()
        if self.display:
            self.win = pygame.display.set_mode([self.W, self.H])
        else:
            self.win = pygame.Surface([self.W, self.H])

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("ubuntu", 20)

        self.state = State.WAIT

        self.step_i = -1
        self.step = self.steps[0]
        self.levels = self.step["levels_start"]
        self.selection = None
        
        self.t1 = self.time()

        if self.output_video:
            tempdir = tempfile.TemporaryDirectory()
            frame = 0
        
        while self.step_i < len(self.steps):
            if self.display:
                pygame.display.set_caption(f"{self.NAME.capitalize()} Sort - {self.clock.get_fps():.2f}fps")
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        # Skip with SPACE
                        if event.key == pygame.K_SPACE:
                            self.t1 -= max(self.WAIT_DUR, self.ANIM_DUR)
            
            self.win.fill(0)
            
            # Draw current levels
            for l, lvl in enumerate(self.levels):
                y = self.MARGIN + l * self.TOT_SIZE
                
                lists = len(lvl)
                width = (self.W - 2*self.MARGIN) / lists
                
                for i, lst in enumerate(lvl):
                    if lst is None: continue
                    
                    w = len(lst)*self.TOT_SIZE - self.SPACE
                    x = self.MARGIN + width * (i+0.5) - w/2
                    
                    for j, val in enumerate(lst):
                        if val == "": continue
                        xj = x + j * self.TOT_SIZE
                        sel = self.selection
                        col = (255,255,255)
                        if sel:
                            if l == sel["lvl1"] and i == sel["i1"] and j == sel["j1"]:
                                col = (255,0,0)
                            elif l == sel["lvl2"] and i == sel["i2"] and j == sel["j2"]:
                                col = (255,0,0)
                        
                        self.draw_num(val, xj, y, col, (255,255,255))
            
            t = self.time()
            if self.state == State.WAIT:
                if t-self.t1 >= self.WAIT_DUR:
                    self.next_step()
            
            elif self.state == State.ANIM:
                r = (t-self.t1)/self.ANIM_DUR
                r = max(0, min(1, r))
                
                for anim in self.step["animations"]:
                    lvl1, lvl2 = anim["lvl1"], anim["lvl2"]
                    lists1 = 2**int(self.depth - abs(self.depth - lvl1))
                    lists2 = 2**int(self.depth - abs(self.depth - lvl2))
                    
                    width1 = (self.W - 2*self.MARGIN) / lists1
                    width2 = (self.W - 2*self.MARGIN) / lists2
                    
                    list_ = anim["list"]
                    w1 = len(anim["origin"])*self.TOT_SIZE - self.SPACE
                    w2 = len(list_)*self.TOT_SIZE - self.SPACE
                    
                    if "w2" in anim.keys():
                        w2 = anim["w2"]*self.TOT_SIZE - self.SPACE
                    
                    x1 = self.MARGIN + width1 * (anim["i1"]+0.5) - w1/2
                    x1 += anim["j1"] * self.TOT_SIZE
                    
                    x2 = self.MARGIN + width2 * (anim["i2"]+0.5) - w2/2
                    x2 += anim["j2"] * self.TOT_SIZE
                    
                    y1 = self.MARGIN + lvl1 * self.TOT_SIZE
                    y2 = self.MARGIN + lvl2 * self.TOT_SIZE
                    
                    x = (x2-x1)*r + x1
                    y = (y2-y1)*r + y1
                    
                    for i, val in enumerate(list_):
                        if val == "": continue
                        xi = x + i*self.TOT_SIZE
                        
                        self.draw_num(val, xi, y)
                
                if r == 1:
                    self.end_step()
            
            if self.display:
                pygame.display.flip()
            
            if self.output_video:
                pygame.image.save(self.win, os.path.join(tempdir.name, f"{frame}.jpg"))
                frame += 1
            
            if self.display:
                self.clock.tick(self.FPS)
            else:
                self.time_offset += 1/self.FPS
        
        if self.output_video:
            self.make_video(tempdir)
    
    def make_video(self, tempdir):
        outdir = input("Output directory: ")
        path = os.path.join(outdir, self.NAME)
        
        os.system(f"ffmpeg -framerate {self.FPS} -i '{tempdir.name}/%d.jpg' -c:v libx264 -pix_fmt yuv420p {path}.mp4")
        os.system(f"ffmpeg -i {path}.mp4 {path}.gif")

if __name__ == "__main__":
    sorter = Sorter([6, 5, 9, 4, 2, 1, 0, 7, 3, 8])
    sorter.render()
