from math import radians, cos, sin
import os
import tempfile
import time

import pygame

class State:
    WAIT = 0
    ANIM = 1

class Sorter:
    NAME = "quick"
    
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
        
        self.init_sizes()
        self.sort()
    
    def init_sizes(self):
        self.NUM_SIZE = 40
        self.SPACE = 10
        self.TOT_SIZE = self.NUM_SIZE + self.SPACE
        self.MARGIN = 20

        self.W = 2*self.MARGIN + len(self.original)*self.TOT_SIZE - self.SPACE
        self.H = 2*self.MARGIN + len(self.original)*self.TOT_SIZE - self.SPACE
        
        self.OX = self.MARGIN
        self.OY = self.H/2 - self.NUM_SIZE/2
    
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
    
    def sort(self, start=0, end=None):
        if end is None:
            end = len(self.original)-1
        
        if start < end:
            pivot = (end-start)//2 + start
            
            list_start = list(self.list)
            list_start[pivot] = ""
            list_start[end] = ""
            step = {
                "list_start": list_start,
                "start": start,
                "end": end,
                "ia": pivot,
                "ib": end,
                "a": self.list[pivot],
                "b": self.list[end],
                "pivot_start": pivot,
                "pivot_end": end,
                "pivot": 0
            }
            self.list[end], self.list[pivot] = self.list[pivot], self.list[end]
            step["list_end"] = list(self.list)
            self.steps.append(step)
            
            j = start
            
            for i in range(start, end):
                if self.list[i] <= self.list[end]:
                    list_start = list(self.list)
                    list_start[i] = ""
                    list_start[j] = ""
                    step = {
                        "list_start": list_start,
                        "start": start,
                        "end": end,
                        "ia": j,
                        "ib": i,
                        "a": self.list[j],
                        "b": self.list[i],
                        "sep_start": j,
                        "sep_end": j+1,
                        "pivot_start": end,
                        "pivot_end": end
                    }
                    self.list[i], self.list[j] = self.list[j], self.list[i]
                    step["list_end"] = list(self.list)
                    self.steps.append(step)
                    j += 1
            
            list_start = list(self.list)
            list_start[j] = ""
            list_start[end] = ""
            step = {
                "list_start": list_start,
                "start": start,
                "end": end,
                "ia": j,
                "ib": end,
                "a": self.list[j],
                "b": self.list[end],
                "pivot_start": end,
                "pivot_end": j,
                "pivot": 1
            }
            self.list[end], self.list[j] = self.list[j], self.list[end]
            step["list_end"] = list(self.list)
            self.steps.append(step)
            pivot = j
            
            self.sort(start, pivot-1)
            self.sort(pivot+1, end)
    
    def next_step(self):
        self.step_i += 1
        self.step = self.steps[min(self.step_i, len(self.steps)-1)]
        self.t1 = self.time()
        self.state = State.ANIM
        self.list = self.step["list_start"]
        if "sep_start" in self.step.keys():
            self.sep = self.step["sep_start"]
        else:
            self.sep = None
        
        if "pivot_start" in self.step.keys():
            self.pivot = self.step["pivot_start"]
        else:
            self.pivot = None
    
    def end_step(self):
        self.t1 = self.time()
        self.state = State.WAIT
        self.list = self.step["list_end"]
        if "sep_end" in self.step.keys():
            self.sep = self.step["sep_end"]
        else:
            self.sep = None
        
        if "pivot_end" in self.step.keys():
            self.pivot = self.step["pivot_end"]
        else:
            self.pivot = None
    
    def render(self):
        pygame.init()
        if self.display:
            self.win = pygame.display.set_mode([self.W, self.H])
        else:
            self.win = pygame.Surface([self.W, self.H])

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("ubuntu", 20)
        P = self.font.render("Pivot", True, (255,0,0))

        self.state = State.WAIT

        self.step_i = -1
        self.step = self.steps[0]
        self.list = self.original
        self.sep = None
        self.pivot = None
        
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
            
            # Draw separator
            if self.sep is not None:
                x = self.MARGIN - self.SPACE/2 + self.sep*self.TOT_SIZE
                pygame.draw.line(self.win, (255,0,0), [x, self.OY], [x, self.OY+self.NUM_SIZE])
            
            # Draw current list
            for i, val in enumerate(self.list):
                if val == "": continue
                
                x = self.OX + i*self.TOT_SIZE
                
                col = (150,150,150)
                if self.step["start"] <= i <= self.step["end"]:
                    col = (255,255,255)
                    
                    if i == self.pivot:
                        col = (255,0,0)
                
                self.draw_num(val, x, self.OY, col)
            
            # Draw pivot text
            if self.pivot is not None and not ("pivot" in self.step.keys() and self.state == State.ANIM):
                x = self.OX + self.pivot*self.TOT_SIZE
                y = self.OY - self.TOT_SIZE
                self.win.blit(P, [x + self.NUM_SIZE/2 - P.get_width()/2, y + self.NUM_SIZE/2 - P.get_height()/2])
            
            t = self.time()
            if self.state == State.WAIT:
                if t-self.t1 >= self.WAIT_DUR:
                    self.next_step()
            
            elif self.state == State.ANIM:
                r = (t-self.t1)/self.ANIM_DUR
                r = max(0, min(1, r))
                
                ia, ib = self.step["ia"], self.step["ib"]
                xa, xb = self.OX + ia*self.TOT_SIZE, self.OX + ib*self.TOT_SIZE
                y = self.OY
                cx = (xb+xa)/2
                cy = y
                radius = abs(cx-xa)
                
                angle = radians(180*r)
                dx, dy = radius*cos(angle), radius*sin(angle)
                
                Xa, Ya = cx - dx, cy - dy
                Xb, Yb = cx + dx, cy + dy
                
                col_a, col_b = (255,255,255), (255,255,255)
                if "pivot" in self.step.keys():
                    if self.step["pivot"] == 0:
                        col_a = (255,0,0)
                    else:
                        col_b = (255,0,0)
                
                self.draw_num(self.step["a"], Xa, Ya, col_a)
                self.draw_num(self.step["b"], Xb, Yb, col_b)
                
                if "pivot" in self.step.keys():
                    if self.step["pivot"] == 0:
                        x, y = Xa, Ya
                    else:
                        x, y = Xb, Yb
                    
                    y -= self.TOT_SIZE
                    self.win.blit(P, [x + self.NUM_SIZE/2 - P.get_width()/2, y + self.NUM_SIZE/2 - P.get_height()/2])
                
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
