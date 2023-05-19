import os
import tempfile
import time

import pygame

class State:
    WAIT = 0
    ANIM = 1

class Sorter:
    NAME = "insertion"
    
    WAIT_DUR = 0.2
    ANIM_DUR = 0.2
    
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
        self.INTERVAL = 40

        self.W = 2*self.MARGIN + len(self.original)*self.TOT_SIZE - self.SPACE
        self.H = 2*self.MARGIN + self.NUM_SIZE*2 + self.INTERVAL
    
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
    
    def sort(self):
        self.result = [""]*len(self.list)
        
        for i, n in enumerate(self.list):
            insert_at = -1
            for j in range(i-1, -1, -1):
                val = self.result[j]
                
                if val <= n:
                    insert_at = j
                    break
                
                self.result[j] = ""
                r1 = list(self.result)
                self.result[j+1] = val
                r2 = list(self.result)
                
                step = {
                    "result_start": r1,
                    "result_end": r2,
                    "n": val,
                    "type": "shift",
                    "ia": j,
                    "ib": j+1
                }
                self.steps.append(step)
            
            self.list[i] = ""
            step = {
                "list": list(self.list),
                "result_start": list(self.result),
                "n": n,
                "type": "insert",
                "ia": i,
                "ib": insert_at+1
            }
            self.result[insert_at+1] = n
            step["result_end"] = list(self.result)
            
            self.steps.append(step)
    
    def next_step(self):
        self.step_i += 1
        self.step = self.steps[min(self.step_i, len(self.steps)-1)]
        self.t1 = self.time()
        self.state = State.ANIM
        if "list" in self.step.keys():
            self.list = self.step["list"]
        self.result = self.step["result_start"]
    
    def end_step(self):
        self.t1 = self.time()
        self.state = State.WAIT
        self.result = self.step["result_end"]
    
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
        self.list = self.original
        self.result = [""]*len(self.list)
        
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
            
            # Draw current list
            for i, val in enumerate(self.list):
                if val == "": continue
                
                x = self.MARGIN + i*self.TOT_SIZE
                y = self.MARGIN
                
                self.draw_num(val, x, y)
            
            # Draw current result
            for i, val in enumerate(self.result):
                if val == "": continue
                
                x = self.MARGIN + i*self.TOT_SIZE
                y = self.MARGIN + self.NUM_SIZE + self.INTERVAL
                
                self.draw_num(val, x, y)
            
            t = self.time()
            if self.state == State.WAIT:
                if t-self.t1 >= self.WAIT_DUR:
                    self.next_step()
            
            elif self.state == State.ANIM:
                r = (t-self.t1)/self.ANIM_DUR
                r = max(0, min(1, r))
                
                ia, ib = self.step["ia"], self.step["ib"]
                x1 = self.MARGIN + ia*self.TOT_SIZE
                x2 = self.MARGIN + ib*self.TOT_SIZE
                
                if self.step["type"] == "insert":
                    y1 = self.MARGIN
                    y2 = self.MARGIN + self.NUM_SIZE + self.INTERVAL
                    y = (y2-y1)*r + y1
                
                elif self.step["type"] == "shift":
                    y = self.MARGIN + self.NUM_SIZE + self.INTERVAL
                
                x = (x2-x1)*r + x1
                
                self.draw_num(self.step["n"], x, y)
                
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
