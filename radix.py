from math import sqrt, ceil, log10
import os
import tempfile
import time

import pygame

class State:
    WAIT = 0
    ANIM = 1

class Sorter:
    NAME = "radix"
    
    WAIT_DUR_SORT = 0.2
    ANIM_DUR_SORT = 0.4
    
    WAIT_DUR_REV = 0.1
    ANIM_DUR_REV = 0.1
    
    WAIT_DUR = WAIT_DUR_SORT
    ANIM_DUR = ANIM_DUR_SORT
    
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
        
        self.VALS_IN_BUCK_W = int(sqrt(len(self.original)))
        self.VALS_IN_BUCK_H = int(ceil(len(self.original)/self.VALS_IN_BUCK_W))
        
        self.BUCKET_W = self.VALS_IN_BUCK_W * self.TOT_SIZE + self.SPACE
        self.BUCKET_H = self.VALS_IN_BUCK_H * self.TOT_SIZE + self.SPACE

        self.BUCKETS_HOR = 5
        self.BUCKETS_VER = 10//self.BUCKETS_HOR

        self.W = 2*self.MARGIN + max(
            len(self.original)*self.TOT_SIZE - self.SPACE,
            (self.BUCKET_W + self.SPACE) * self.BUCKETS_HOR - self.SPACE
        )
        self.H = 2*self.MARGIN + self.TOT_SIZE + (self.BUCKET_H + self.TOT_SIZE) * self.BUCKETS_VER
        
        self.OX_list = self.W/2 - (len(self.original)*self.TOT_SIZE - self.SPACE)/2
        self.OX_buckets = self.W/2 - ((self.BUCKET_W + self.SPACE)*self.BUCKETS_HOR - self.SPACE)/2
        self.OY_list = self.MARGIN
        self.OY_buckets = self.OY_list + self.TOT_SIZE
    
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
    
    def cp_bckts(self):
        r = []
        for b in self.buckets:
            r.append(list(b))
        return r
    
    def sort(self):
        max_order = ceil(log10(max(self.list)))
        
        l_ = list(self.list)
        
        for order in range(max_order):
            self.buckets = [[] for i in range(10)]
            
            temp = list(l_)
            
            for i in range(len(l_)):
                n = (temp[i]//(10**order)) % 10
                
                temp[i] = ""
                step = {
                    "list_start": list(temp),
                    "list_end": list(temp),
                    "buckets_start": self.cp_bckts(),
                    "list_i": i,
                    "bucket": n,
                    "bucket_i": len(self.buckets[n]),
                    "n": l_[i],
                    "order": 10**order,
                    "reverse": False
                }
                
                self.buckets[n].append(l_[i])
                
                step["buckets_end"] = self.cp_bckts()
                self.steps.append(step)
            
            l_ = list(temp)
            
            j = 0
            for b in range(10):
                bucket = self.buckets[b]
                for i in range(len(bucket)):
                    n = bucket[i]
                    bucket[i] = ""
                    step = {
                        "list_start": list(l_),
                        "buckets_start": self.cp_bckts(),
                        "buckets_end": self.cp_bckts(),
                        "list_i": j,
                        "bucket": b,
                        "bucket_i": i,
                        "n": n,
                        "order": 10**order,
                        "reverse": True
                    }
                    l_[j] = n
                    step["list_end"] = list(l_)
                    self.steps.append(step)
                    j += 1
    
    def next_step(self):
        self.step_i += 1
        self.step = self.steps[min(self.step_i, len(self.steps)-1)]
        self.t1 = self.time()
        self.state = State.ANIM
        self.list = self.step["list_start"]
        self.buckets = self.step["buckets_start"]
        
        if self.step["reverse"]:
            self.WAIT_DUR = self.WAIT_DUR_REV
            self.ANIM_DUR = self.ANIM_DUR_REV
        else:
            self.WAIT_DUR = self.WAIT_DUR_SORT
            self.ANIM_DUR = self.ANIM_DUR_SORT
    
    def end_step(self):
        self.t1 = self.time()
        self.state = State.WAIT
        self.list = self.step["list_end"]
        self.buckets = self.step["buckets_end"]
    
    def render(self):
        pygame.init()
        if self.display:
            self.win = pygame.display.set_mode([self.W, self.H])
        else:
            self.win = pygame.Surface([self.W, self.H])

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("ubuntu", 16)

        self.state = State.WAIT

        self.step_i = -1
        self.step = self.steps[0]
        self.list = self.original
        self.buckets = [[] for i in range(10)]
        
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
                
                x = self.OX_list + i*self.TOT_SIZE
                y = self.OY_list
                
                self.draw_num(val, x, y)
            
            # Draw current buckets
            for bx in range(self.BUCKETS_HOR):
                for by in range(self.BUCKETS_VER):
                    bi = by*self.BUCKETS_HOR + bx
                    bucket = self.buckets[bi]
                    
                    ox = self.OX_buckets + bx*(self.BUCKET_W + self.SPACE)
                    oy = self.OY_buckets + by*(self.BUCKET_H + self.TOT_SIZE)
                    
                    pygame.draw.lines(self.win, (255,255,255), False, [
                        [ox, oy],
                        [ox, oy+self.BUCKET_H],
                        [ox+self.BUCKET_W, oy+self.BUCKET_H],
                        [ox+self.BUCKET_W, oy]
                    ])
                    n = self.step["order"] * bi
                    t = self.font.render(str(n), True, (255,255,255))
                    self.win.blit(t, [ox + self.BUCKET_W/2 - t.get_width()/2, oy + self.BUCKET_H + self.NUM_SIZE/2 - t.get_height()/2])
                    
                    for i, val in enumerate(bucket):
                        if val == "": continue
                        
                        x = i % self.VALS_IN_BUCK_W
                        y = i // self.VALS_IN_BUCK_W
                        
                        X = ox + x * self.TOT_SIZE + self.SPACE
                        Y = oy + y * self.TOT_SIZE
                        
                        self.draw_num(val, X, Y)
            
            t = self.time()
            if self.state == State.WAIT:
                if t-self.t1 >= self.WAIT_DUR:
                    self.next_step()
            
            elif self.state == State.ANIM:
                r = (t-self.t1)/self.ANIM_DUR
                r = max(0, min(1, r))
                
                li = self.step["list_i"]
                b = self.step["bucket"]
                bi = self.step["bucket_i"]
                
                x1 = self.OX_list + li*self.TOT_SIZE
                y1 = self.OY_list
                
                Bx = b % self.BUCKETS_HOR
                By = b // self.BUCKETS_HOR
                
                bx = bi % self.VALS_IN_BUCK_W
                by = bi // self.VALS_IN_BUCK_W
                
                x2 = self.OX_buckets + Bx*(self.BUCKET_W + self.SPACE) + bx * self.TOT_SIZE + self.SPACE
                y2 = self.OY_buckets + By*(self.BUCKET_H + self.TOT_SIZE) + by * self.TOT_SIZE
                
                if self.step["reverse"]:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                
                x = (x2-x1)*r + x1
                y = (y2-y1)*r + y1
                
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
    sorter = Sorter([1687, 923, 2180, 1272, 1812, 505, 1618, 968, 1673, 1976])
    sorter.render()
