import math
import random
# Import and initialize the pygame library
import pygame
from pygame.locals import *
pygame.init()

def calculate_bp(cur_bp):
    t = cur_bp
    return (20*math.sin(t) + 5*math.sqrt(t) +10*random.randrange(-1000, 1000, 1)/1000 + 50)


bp = [60];
#create the function
for t in range(0, 250):
    bp.append(calculate_bp(bp[-1]))

print(bp)

pygame.init()
screen = pygame.display.set_mode((500, 500))
done = False

c = 1

while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
        #lower boundary
        pygame.draw.line(screen, (0, 128, 255), (0,c*(500-60)), ((500, c*(500-60))))
        #upper boundary
        pygame.draw.line(screen, (0, 128, 255), (0,c*(500-80)), ((500, c*(500-80))))

        #very high boundary
        pygame.draw.line(screen, (0, 128, 255), (0,c*(500-120)), ((500, c*(500-120))))

        for i in range(len(bp)-1):
            #line(surface, color, start_pos, end_pos)
            pygame.draw.line(screen, (0, 128, 255), (i*2,c*(500-bp[i])), ((i+1)*2, c*(500-bp[i+1])))
        

        pygame.display.flip()