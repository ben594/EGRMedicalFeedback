import math
import random
import pygame
from simple_pid import PID
from pygame.locals import *

import pygame
import pygame_gui
import pygame_menu

from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu

pygame.init()

FPS = 10
clock = pygame.time.Clock()

#reads current bp, outputs calculated bp for the next timestep
def calculate_bp(cur_bp):
    t = cur_bp
    return (10*math.sin(t) + 40)
    
bp = [40]
target_bp = 50
new_target_bp = target_bp
low_bound = target_bp - 5
high_bound = target_bp + 5

#create the bp log
for t in range(0, 250):
    bp.append(calculate_bp(bp[-1]))

initial_avg = sum(bp)/len(bp)

bp_wave_y = 200

done = False
c = 2 #scale factor

pygame.display.set_caption('Ultimate Feedback')
window_surface = pygame.display.set_mode((800, 600))
bp_wave = pygame.Surface((500, 200))

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#FFFFFF'))
window_surface.blit(background, (0, 0))

manager = pygame_gui.UIManager((800, 600))

bp_display = UITextBox("MAP: " + str(0),
                        pygame.Rect((520, 0), (280, 90)),
                        manager=manager)

infusion_display = UITextBox("Infusion rate: " + str(0),
                        pygame.Rect((520, 110), (280, 90)),
                        manager=manager)

target_bp_display = UITextBox("Target MAP: " + str(target_bp),
                              pygame.Rect((50, 250), (200, 100)),
                              manager=manager)

select_medication_display = UITextBox("Select medication:",
                              pygame.Rect((50, 400), (200, 100)),
                              manager=manager)

enter_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 250), (200, 100)), text='UPDATE', manager=manager)
stop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 400), (200, 100)), text='STOP', manager=manager)
up_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 250), (200, 40)), text='UP', manager=manager)
down_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 310), (200, 40)), text='DOWN', manager=manager)
menu = pygame_gui.elements.UIDropDownMenu(options_list={"Medication A", "Medication B"},
                                          starting_option="Medication A",
                                          relative_rect=pygame.Rect((300, 400), (200, 100)),
                                          manager=manager)

while not done:
    time_delta = clock.tick(60)/1000.0
    manager.update(time_delta)
    clock.tick(FPS); #set framerate

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == enter_button:
                print("Update button pressed")
                target_bp = new_target_bp
                low_bound = target_bp - 5
                high_bound = target_bp + 5
            if event.ui_element == stop_button:
                print("Stop button pressed")
            if event.ui_element == up_button:
                new_target_bp = new_target_bp + 1
                target_bp_display = UITextBox("Target MAP: " + str(new_target_bp),
                                              pygame.Rect((50, 250), (200, 100)),
                                              manager=manager)
                print("Up button pressed")
            if event.ui_element == down_button:
                new_target_bp = new_target_bp - 1
                target_bp_display = UITextBox("Target MAP: " + str(new_target_bp),
                                              pygame.Rect((50, 250), (200, 100)),
                                              manager=manager)
                print("Down button pressed")

        manager.process_events(event)
        
    manager.update(FPS) # needed for button press to be registered


    manager.draw_ui(window_surface)
    # window_surface.blit(background, (0, 0))
    bp_wave.fill(pygame.Color("#000000"))

    #avg bp in given frame
    avg = sum(bp)/len(bp)
    
    # draw lines
    #lower boundary
    pygame.draw.line(bp_wave, (255, 0, 0), (0,(bp_wave_y-c*low_bound)), ((500, (bp_wave_y-c*low_bound))))
    #upper boundary
    pygame.draw.line(bp_wave, (255, 0, 0), (0,(bp_wave_y-c*high_bound)), ((500, (bp_wave_y-c*high_bound))))
    #mean
    pygame.draw.line(bp_wave, (0, 0, 255), (0,(bp_wave_y-c*avg)), ((500, (bp_wave_y-c*avg))))
    #target
    pygame.draw.line(bp_wave, (0, 255, 0), (0,(bp_wave_y-c*target_bp)), ((500, (bp_wave_y-c*target_bp))))

    #iterates and draws line between bp points
    for i in range(125):
        pygame.draw.line(bp_wave, (0, 128, 255), (int(i*2*c),(bp_wave_y-c*bp[i])), (int((i+1)*2*c), (bp_wave_y-c*bp[i+1])))
        
    window_surface.blit(bp_wave, (0, 0))
    
    bp_display = UITextBox("MAP: " + str(avg),
                        pygame.Rect((520, 0), (280, 90)),
                        manager=manager)
    
    infusion_display = UITextBox("Infusion rate: " + str(0),
                        pygame.Rect((520, 110), (280, 90)),
                        manager=manager)

    #update bp    
    bp.append(calculate_bp(bp[len(bp)-1])) #append calculated bp to end of array
    bp.pop(0) #remove first element from array

    pygame.display.flip()