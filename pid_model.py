import math
import random
import pygame
from simple_pid import PID
from pygame.locals import *
pygame.init()

FPS = 30
clock = pygame.time.Clock()

time_count = 1
#MAP calc
initial_pressure = 115 #P0
noise = 0

#change calc
sensibility = 0.9137            #Ks
transport_delay = 41.2319       #Ti
recirculation_delay = 65.0625   #Tc
recirculation_const = 0.3736    #alpha
t = 31.6185                     #time constant

# #specific eg
# sensibility = 0.25            #Ks
# transport_delay = 20       #Ti
# recirculation_delay = 30   #Tc
# recirculation_const = 0    #alpha
# t = 30                     #time constant

pressure_change = 0
mean_arterial_pressure = 115

def heaviside(num):
    if num > 0: return 1
    else: return 0

#reads current bp, outputs calculated bp for the next timestep
#infusion rate ranges from 0 to 180 ml/h
def calculate_bp(time, infusion_rate):
    pressure_change =  heaviside(time - 41.2319)*infusion_rate*0.9137*(0.03162*math.exp(-0.03162*(time - 41.2319)) + 0.01181*math.exp(-0.03162*(time - 106.2944))*heaviside(time - 106.2944))
    global mean_arterial_pressure
    mean_arterial_pressure = initial_pressure - pressure_change + noise
    if (mean_arterial_pressure < 0): mean_arterial_pressure = 0

    return mean_arterial_pressure

#create bp array with starting bp of 60
bp = [115]

#create the bp log
# for t in range(1, 250):
#     bp.append(calculate_bp(time_count, 0))
#     time_count += 1

initial_avg = sum(bp)/len(bp)

#set up pygame and constants
pygame.init()
screen = pygame.display.set_mode((500, 500))
done = False
c = 1 #scale factor

#define pid 
target_bp = 100
P = 0.7500
I = 0.0140
D = 0

def calc_error(bp):
    return target_bp - bp

pid = PID(P, I, D, setpoint = 0)
pid.error_map = calc_error
pid.sample_time = 1/FPS  # Update every 0.01 seconds
pid.output_limits = (0, 180)
#''' COMMENT THIS OUT WHEN YOU WANT TO QUICKSIM, ELSE UNCOMMENT FOR VISUALIZATION
for i in range(500):
    #update bp
    infusion_rate = pid(bp[-1], dt=time_count)
    control = calculate_bp(time_count, infusion_rate)
    time_count += 1
    bp.append(mean_arterial_pressure) #append calculated bp to end of array
    bp.pop(0) #remove first element from array

    mean = sum(bp)/len(bp)
    variance = sum([((x - mean) ** 2) for x in bp]) / len(bp)
    res = variance ** 0.5
    print("MAP: " + str(mean_arterial_pressure))
    print("Infusion rate: " + str(infusion_rate))
    #print("-------------------------------------------")        



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
        #pygame.draw.line(screen, (0, 0, 255), (0,(500-c*avg)), ((500, (500-c*avg))))
        #target
        pygame.draw.line(screen, (0, 255, 0), (0,(500-c*target_bp)), ((500, (500-c*target_bp))))
        

        #iterates and draws line between bp points
        for i in range(int((len(bp)-1))):
            #line(surface, color, start_pos, end_pos)
            pygame.draw.line(screen, (0, 128, 255), (int(i*2*c),(500-c*bp[i])), (int((i+1)*2*c), (500-c*bp[i+1])))
        
        #update bp
        control = calculate_bp(time_count, pid(bp[-1], dt=time_count))
        bp.append(control) #append calculated bp to end of array
        bp.pop(0) #remove first element from array
        time_count += 1
        pygame.display.flip()
#'''