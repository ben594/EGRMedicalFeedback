import math
import random
import pygame
from simple_pid import PID
from pygame.locals import *
pygame.init()

FPS = 20
clock = pygame.time.Clock()

active_medication = 0
taken_medication = 0

#reads current bp, outputs calculated bp for the next timestep
def calculate_bp(cur_bp, dose):
    t = cur_bp
    #return (20*math.sin(t) + 5*math.sqrt(t) +10*random.randrange(-1000, 1000, 1)/1000 + 50)
    dose_effect = effect_of_dose(dose)
    # print("dose_effect: ", dose_effect)
    return (10*math.sin(t) + 40 + dose_effect)
    # return 1.001 * cur_bp + dose

def effect_of_dose(dose):
    # dose is in terms of amount per minute
    global active_medication
    global taken_medication
    global max_effect
    taken_medication = taken_medication + dose / 60
    active_medication = active_medication + taken_medication / 10
    taken_medication = taken_medication - taken_medication / 10
    active_medication = active_medication - 1/10
    return active_medication/10


#create bp array with starting bp of 60
bp = [40]

# dose
dose = 0

#create the bp log
for t in range(0, 250):
    bp.append(calculate_bp(bp[-1], 0))

initial_avg = sum(bp)/len(bp)

#set up pygame and constants
pygame.init()
screen = pygame.display.set_mode((500, 500))
done = False
c = 3 #scale factor

#define pid 
target_bp = 65
# pid = PID(1, 0, 0, setpoint = target_bp)
pid = PID(1, 0, 0, setpoint = target_bp - bp[len(bp) - 1])

'''
for i in range(250):
    #update bp
    control = pid(calculate_bp(bp[-1])) 
    bp.append(control) #append calculated bp to end of array
    bp.pop(0) #remove first element from array

mean = sum(bp)/len(bp)
variance = sum([((x - mean) ** 2) for x in bp]) / len(bp)
res = variance ** 0.5

print(mean)
print(res)
print(max(bp) - min(bp))

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
        control = pid(effect_of_dose(dose))
        print(control)
        dose = control
        bp.append(calculate_bp(bp[len(bp)-1], control)) #append calculated bp to end of array
        pid.setpoint = target_bp - bp[len(bp) - 1]
        bp.pop(0) #remove first element from array

        pygame.display.flip()
#'''