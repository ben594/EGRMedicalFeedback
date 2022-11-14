import math
import random
import pygame
from simple_pid import PID

b0 = 0.18661
bm = 0.07464
a1 = 0.74082
m = 3
d = 3
previous_pressure_change = 0
pressure_change = 0
mean_arterial_pressure = 115
infusion_rate = 40
time_count = 1
initial_pressure = 115 #P0
noise = 0


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
    mean_arterial_pressure = initial_pressure - calculate_pressure(time) + noise
    if (mean_arterial_pressure < 0): mean_arterial_pressure = 0

    return mean_arterial_pressure


#create the bp log
for t in range(1, 250):
    control = calculate_bp(time_count)
    bp.append(control) #append calculated bp to end of array
    time_count += 1