import math
import random
import pygame

P = 0.5
I = 0
D = 0

b0 = 0.18661
bm = 0.07464
a1 = 0.74082
m = 3
d = 3

infusion_log = []
for i in range(0, 10):
    infusion_log.append(0)
    
bp_log = []
map = 115
target_map = 65
previous_map_change = 0
map_change = 0

for i in range(0, 10):
    bp_log.append(map)

def plant(infusion):
    global map
    global infusion_log
    global map_change
    global previous_map_change
    
    print("new infusion: ", infusion)
    infusion_log.append(infusion)
    infusion_log.pop(0)
    map_change = b0 * infusion_log[9 - d]+ bm * infusion_log[9 - d - m] + a1 * previous_map_change
    map = map - map_change
    bp_log.append(map)
    bp_log.pop(0)
    
def calc_error(map):
    return target_map - map

integral = 0
derivative = 0
for t in range(0, 100):
    # t is in seconds
    error = map - target_map
    integral += error
    derivative = bp_log[9] - bp_log[8]
    control = P * error + I * integral + D * derivative
    plant(control)
    print("time: ", t)
    print("map: ", map)