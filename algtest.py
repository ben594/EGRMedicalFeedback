import math
import random
# Import and initialize the pygame library
import pygame
from pygame.locals import *
pygame.init()

FPS = 10
clock = pygame.time.Clock()

def calculate_bp(cur_bp):
    t = cur_bp
    return (20*math.sin(t) + 5*math.sqrt(t) +10*random.randrange(-1000, 1000, 1)/1000 + 50)

bp = [60];

#create the bp log
for t in range(0, 250):
    bp.append(calculate_bp(bp[-1]))

#set up pygame and constants
pygame.init()
screen = pygame.display.set_mode((500, 500))
done = False
c = 3

while not done:
        clock.tick(FPS); #set framerate
        screen.fill((0,0,0))
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True

        #avg bp
        avg = sum(bp)/len(bp)
        #lower boundary
        pygame.draw.line(screen, (255, 0, 0), (0,(500-c*60)), ((500, (500-c*60))))
        #upper boundary
        pygame.draw.line(screen, (255, 0, 0), (0,(500-c*80)), ((500, (500-c*80))))
        #mean
        pygame.draw.line(screen, (0, 255, 0), (0,(500-c*avg)), ((500, (500-c*avg))))

        for i in range(int((len(bp)-1))):
            #line(surface, color, start_pos, end_pos)
            pygame.draw.line(screen, (0, 128, 255), (int(i*2*c),(500-c*bp[i])), (int((i+1)*2*c), (500-c*bp[i+1])))
        
        #update bp
        bp.append(calculate_bp(bp[-1]))
        bp.pop(0)

        pygame.display.flip()