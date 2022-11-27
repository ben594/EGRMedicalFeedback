import math
import random
import pygame
from simple_pid import PID
from pygame.locals import *

import pygame
import pygame_gui

from pygame_gui.elements.ui_text_box import UITextBox

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
y_const = 200
screen = pygame.display.set_mode((500, y_const))
done = False
c = 2 #scale factor

#define pid 
target_bp = 65
# pid = PID(1, 0, 0, setpoint = target_bp)
pid = PID(1, 0, 0, setpoint = target_bp - bp[len(bp) - 1])

current_map = 65

###########################
# GUI
# pygame gui documentation: https://pygame-gui.readthedocs.io/en/v_060/index.html
pygame.init()

pygame.display.set_caption('Ultimate Feedback')
window_surface = pygame.display.set_mode((800, 600))

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#FFFFFF'))

manager = pygame_gui.UIManager((800, 600))

bp_wave = pygame.Surface((500, 150))

# hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text='Say Hello', manager=manager)
# bp_display = UITextBox(str(current_map),
#                         pygame.Rect((520, 0), (280, 200)),
#                         manager=manager)

clock = pygame.time.Clock()
is_running = True

while is_running:
    # time_delta = clock.tick(60)/1000.0
    time_delta = clock.tick(5)
    manager.update(time_delta)

    bp_wave.fill((0,0,0))
    window_surface.fill(pygame.Color('#FFFFFF'))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        # if event.type == pygame_gui.UI_BUTTON_PRESSED:
        #     if event.ui_element == hello_button:
        #         print('Hello World!')

        manager.process_events(event)


    # window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)
    manager.draw_ui(bp_wave)
    # bp_wave.blit(background, (0, 0))
    # window_surface.blit(background, (0, 0))
    window_surface.blit(bp_wave, (0, 0))

    
    # clock.tick(FPS); #set framerate
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    done = True

    #avg bp in given frame
    avg = sum(bp)/len(bp)
    
    # draw lines
    #lower boundary
    pygame.draw.line(screen, (255, 0, 0), (0,(y_const-c*60)), ((500, (y_const-c*60))))
    #upper boundary
    pygame.draw.line(screen, (255, 0, 0), (0,(y_const-c*80)), ((500, (y_const-c*80))))
    #mean
    pygame.draw.line(screen, (0, 0, 255), (0,(y_const-c*avg)), ((500, (y_const-c*avg))))
    #target
    pygame.draw.line(screen, (0, 255, 0), (0,(y_const-c*target_bp)), ((500, (y_const-c*target_bp))))

    #iterates and draws line between bp points
    for i in range(125):
        # line(surface, color, start_pos, end_pos)
        pygame.draw.line(screen, (0, 128, 255), (int(i*2*c),(y_const-c*bp[i])), (int((i+1)*2*c), (y_const-c*bp[i+1])))

    #update bp
    control = pid(effect_of_dose(dose))
    bp_display = UITextBox(str(avg),
                        pygame.Rect((520, 0), (280, 150)),
                        manager=manager)
    print(control)
    dose = control
    bp.append(calculate_bp(bp[len(bp)-1], control)) #append calculated bp to end of array
    pid.setpoint = target_bp - bp[len(bp) - 1]
    bp.pop(0) #remove first element from array

    # pygame.display.update()

    pygame.display.flip()