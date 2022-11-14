import math
import random
import pygame
from simple_pid import PID

FPS = 30
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
target_bp = 70

prev_infusion_rate = initial_pressure - target_bp

#create bp array with starting bp of 60
bp = [115]
#define pid 
P = 0.7500
I = 0.0140
D = 0

def calc_error(bp):
    global mean_arterial_pressure
    print(target_bp - mean_arterial_pressure)
    return target_bp - mean_arterial_pressure

pid = PID(P, I, D, setpoint = initial_pressure-target_bp)
pid.error_map = calc_error
#pid.sample_time = 1
pid.output_limits = (0, 180)

def calc_infusion_rate(time):
    global infusion_rate, time_count, prev_infusion_rate
    #infusion_rate =  pid(prev_infusion_rate, dt=time_count)
    #return infusion_rate
    return initial_pressure - target_bp

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
    print("MAP "+ str(control))
    #print("infusion rate "+ str(infusion_rate))
    time_count += 1