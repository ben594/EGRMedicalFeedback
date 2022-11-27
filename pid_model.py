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

b0 = 0.18661
bm = 0.07464
a1 = 0.74082
m = 3
d = 3
previous_pressure_change = 0
infusion_rate = 40

pressure_change = 0
mean_arterial_pressure = 115

def heaviside(num):
    if num > 0: return 1
    else: return 0

def calc_infusion_rate(time):
    global infusion_rate, time_count
    return pid(infusion_rate, dt=time_count)

def calculate_pressure(time):
    global previous_pressure_change
    pressure_change = b0*calc_infusion_rate(time-d)+ bm*calc_infusion_rate(time-d-m )+ a1*previous_pressure_change
    previous_pressure_change = pressure_change
    return pressure_change

#reads current bp, outputs calculated bp for the next timestep
#infusion rate ranges from 0 to 180 ml/h
def calculate_bp(time):
    #pressure_change =  heaviside(time - 41.2319)*infusion_rate*0.9137*(0.03162*math.pow(math.e, -0.03162*(time-41.2319)) + 0.01181*math.pow(math.e, -0.03162*(time - 106.2944)*heaviside(time - 106.2944)))
    #pressure_change =  infusion_rate*0.9137*(0.03162*math.pow(math.e, -0.03162*(time-41.2319)) + 0.01181*math.pow(math.e, -0.03162*(time - 106.2944)))
    mean_arterial_pressure = initial_pressure - calculate_pressure(time) + noise
    if (mean_arterial_pressure < 0): mean_arterial_pressure = 0

    return mean_arterial_pressure

#create bp array with starting bp of 60
bp = [115]
#define pid 
target_bp = 100
P = 0.7500
I = 0.0140
D = 0
c = 1 #scale factor

initial_avg = sum(bp)/len(bp)

#set up pygame and constants
pygame.init()
screen = pygame.display.set_mode((500, 500))
done = False

#iterates and draws line between bp points
for i in range(int((len(bp)-1))):
    pygame.draw.line(screen, (0, 128, 255), (int(i*2*c),(500-c*bp[i])), (int((i+1)*2*c), (500-c*bp[i+1])))

def calc_error(bp):
    return target_bp - bp

pid = PID(P, I, D, setpoint = 40)
pid.error_map = calc_error
pid.sample_time = 1/FPS  # Update every 0.01 seconds
pid.output_limits = (0, 180)

#create the bp log
for t in range(1, 250):
    control = calculate_bp(time_count)
    bp.append(control) #append calculated bp to end of array
    time_count += 1

#''' COMMENT THIS OUT WHEN YOU WANT TO QUICKSIM, ELSE UNCOMMENT FOR VISUALIZATION
for i in range(100):
    #update bp
    control = calculate_bp(time_count)
    time_count += 1
    bp.append(control) #append calculated bp to end of array
    #bp.pop(0) #remove first element from array

    # mean = sum(bp)/len(bp)
    # variance = sum([((x - mean) ** 2) for x in bp]) / len(bp)
    # res = variance ** 0.5
    #if (i % 250 == 0):
    print("MAP: " + str(control))
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