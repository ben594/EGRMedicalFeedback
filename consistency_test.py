import math
import random

# pygame imports
# -----------------------------------------------------
import pygame
from pygame.locals import *

# pid tuning parameters
# -----------------------------------------------------
P = 0.75
I = 0.014
D = 0

# map model vars
# -----------------------------------------------------
b0 = 0.18661
bm = 0.07464
a1 = 0.74082
m = 3
d = 3
previous_map_change = 0
map_change = 0

# stores 10 most recent infusion rates
# -----------------------------------------------------
infusion_log = []
for i in range(0, 100):
    infusion_log.append(0)

# gui variables
# -----------------------------------------------------
initial_map = 80
current_map = 80
target_map = 65
new_target_bp = target_map # temporary var for target bp
low_bound = target_map - 5 # lower bound of target bp range
high_bound = target_map + 5 # upper bound of target bp range
in_range = False
max_infusion = 140 # 140 ml/hr

#create the bp log
# -----------------------------------------------------
bp_log = [] # initial bp
for t in range(0, 380):
    bp_log.append(current_map)
    
initial_avg = sum(bp_log)/len(bp_log)

# patient response to infusion rate
# -----------------------------------------------------
def response(infusion):
    global current_map
    global infusion_log
    global map_change
    global previous_map_change
    global initial_map
    global bp_log
    
    infusion_log.append(infusion)
    infusion_log.pop(0)
    map_change = (b0 * infusion_log[len(infusion_log) - 1 - d]+ bm * infusion_log[len(infusion_log) - 1 - d - m] + a1 * previous_map_change)
    previous_map_change = map_change
    current_map = initial_map - map_change + random.randrange(-1, 1)
    bp_log.append(current_map)
    bp_log.pop(0)

timestep = 1
integral = 0
derivative = 0

system_stop = False

counter = 0

target_map_list = [60, 62, 65, 68, 70]
starting_map_list = [115, 120, 125, 130, 140]
repetitions = 1

total_tests = len(target_map_list) * len(starting_map_list) * repetitions

# main loop
for target in target_map_list:
    for start in starting_map_list:
        for repetition in range(0, repetitions):
            max_out_of_range = 0
            print("target map: ", target, " starting map: ", start)
            # reset things
            derivative = 0
            integral = 0
            target_map = target
            current_map = start
            low_bound = target_map - 5
            high_bound = target_map + 5
            map_change = 0
            previous_map_change = 0
            initial_map = start
            
            infusion_log = []
            for i in range(0, 100):
                infusion_log.append(0)
                
            bp_log = [] # initial bp
            for t in range(0, 380):
                bp_log.append(current_map)
            
            # run algorithm/simulation for 12 hours
            for t in range(0, 43200):
                error = current_map - target_map
                integral += error * timestep
                derivative = (bp_log[len(bp_log) - 1] - bp_log[len(bp_log) - 2]) / timestep
                control = P * error + I * integral + D * derivative
                if control < 0 or current_map < low_bound:
                    control = 0
                if control > max_infusion:
                    control = max_infusion
                
                response(control)

                if ((t > 300) and (current_map < low_bound or current_map > high_bound)):
                    # print("time: ", t, " current map out of range: ", current_map)
                    max_out_of_range = t
                    
            print("last time map was out of range: ", max_out_of_range)
            if max_out_of_range < 300:
                counter = counter + 1
                
            
print("total tests passed: ", counter, " out of " , total_tests)
print("pass rate: ", counter/total_tests)