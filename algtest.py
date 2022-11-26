import math
import random
import pygame
from simple_pid import PID
from pygame.locals import *
pygame.init()

FPS = 30
clock = pygame.time.Clock()

active_medication = 0
taken_medication = 0

#reads current bp, outputs calculated bp for the next timestep
def calculate_bp(cur_bp, infusion_rate):
    #return (5*math.sin(t) + t+ 0.5 random.randrange(-1000, 1000, 1)/1000 + 50)
    
    return (5*math.sin(cur_bp) - infusion_rate + 100)

#create bp array with starting bp of 60
bp = [115]

#create the bp log
for t in range(0, 250):
    bp.append(calculate_bp(bp[-1], 0.01))

initial_avg = sum(bp)/len(bp)

#set up pygame and constants
pygame.init()
screen = pygame.display.set_mode((500, 500))
done = False
c = 3 #scale factor

#define pid 
target_bp = 65
P = -0.009*2
I = -0.003
D = -0.001

#for sin, Kp = -0.017, Tu = 125

# P = -0.017*0.33
# I = (2/3)*(-0.017/125)
# D = (2/3)*(-0.017*125)

pid = PID(P, I, D, setpoint = (target_bp - bp[-1]))
pid.sample_time = 1/FPS  # Update every 0.01 seconds
#pid.auto_mode = False
pid.output_limits = (0, None)
''' COMMENT THIS OUT WHEN YOU WANT TO QUICKSIM, ELSE UNCOMMENT FOR VISUALIZATION
for i in range(1500):
    #update bp
    control = calculate_bp(bp[-1], pid(bp[-1]))
    bp.append(control) #append calculated bp to end of array
    bp.pop(0) #remove first element from array

    if(i % 250 == 0):
        
        mean = sum(bp)/len(bp)
        print(bp.count(max(bp)))
        variance = sum([((x - mean) ** 2) for x in bp]) / len(bp)
        res = variance ** 0.5
        print("Mean after " + str(i) + " iterations: " + str(mean))
        print("Standard deviation after "+ str(i) + " iterations: " + str(res))
        print("Range after "+ str(i) + " iterations: " + str(max(bp) - min(bp)))
        print("-------------------------------------------")




'''

while not done:
        clock.tick(FPS); #set framerate
        screen.fill((0,0,0))
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True

        #avg bp in given frame
        avg = sum(bp)/len(bp)
        #lower boundary
        pygame.draw.line(screen, (255, 0, 0), (0,(500-c*60)), ((500, (500-c*60))))
        #upper boundary
        pygame.draw.line(screen, (255, 0, 0), (0,(500-c*80)), ((500, (500-c*80))))
        #mean
        pygame.draw.line(screen, (0, 0, 255), (0,(500-c*avg)), ((500, (500-c*avg))))
        #target
        pygame.draw.line(screen, (0, 255, 0), (0,(500-c*target_bp)), ((500, (500-c*target_bp))))
        

        #iterates and draws line between bp points
        for i in range(int((len(bp)-1))):
            # line(surface, color, start_pos, end_pos)
            pygame.draw.line(screen, (0, 128, 255), (int(i*2*c),(500-c*bp[i])), (int((i+1)*2*c), (500-c*bp[i+1])))
    
        #update bp
        control = calculate_bp(bp[-1], pid(bp[-1]))
        #control = calculate_bp(bp[-1], 0)
        bp.append(control) #append calculated bp to end of array
        bp.pop(0) #remove first element from array
        pid.setpoint = target_bp - bp[-1]

        pygame.display.flip()
#'''