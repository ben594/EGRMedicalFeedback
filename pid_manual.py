import math
import random
import pygame
from pygame.locals import *

#set up pygame and constants
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((500, 600))
c = 2 # scale factor

# pid tuning parameters
P = 0.75
I = 0.0140
D = 0

# map model parameters
b0 = 0.18661
bm = 0.07464
a1 = 0.74082
m = 3
d = 3

# stores 10 most recent infusion rates
infusion_log = []
for i in range(0, 10):
    infusion_log.append(0)
    
# define variables for blood pressure
bp_log = []
map = 100
target_map = 70
previous_map_change = 0
map_change = 0

# store 100 most recent map values
for i in range(0, 100):
    bp_log.append(map)

# patient response to infusion rate
def response(infusion):
    global map
    global infusion_log
    global map_change
    global previous_map_change
    
    print("new infusion: ", infusion)
    infusion_log.append(infusion)
    infusion_log.pop(0)
    map_change = b0 * infusion_log[9 - d]+ bm * infusion_log[9 - d - m] + a1 * previous_map_change + random.randrange(-5, 5)
    map = map - map_change
    bp_log.append(map)
    bp_log.pop(0)
    
integral = 0
derivative = 0
timestep = 2
t = 0
done = False
while not done:
    clock.tick(timestep)
    screen.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                done = True
    # t is in seconds
    error = map - target_map
    integral += error * timestep
    derivative = (bp_log[len(bp_log) - 1] - bp_log[len(bp_log) - 2]) / timestep
    control = P * error + I * integral + D * derivative
    response(control)
    print("time: ", t)
    print("map: ", map)
    print("most recent bp: ", bp_log[len(bp_log) - 1])
    t += 1
    
    #lower boundary
    pygame.draw.line(screen, (255, 0, 0), (0,(500-c*60)), ((500, (500-c*60))))
    #upper boundary
    pygame.draw.line(screen, (255, 0, 0), (0,(500-c*80)), ((500, (500-c*80))))
    
    #iterates and draws line between bp points
    for i in range(len(bp_log) - 1):
        pygame.draw.line(screen, (0, 128, 255), (int(i * 2 * c),(500-c * bp_log[i])), (int((i + 1) * 2 * c), (500-c * bp_log[i+1])))
        
    pygame.display.flip()