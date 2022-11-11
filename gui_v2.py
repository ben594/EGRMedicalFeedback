# not too cluttered
# function to zoom in on BP monitoring
# emergency stop important, but sometimes a problem
# stop: turn off automation, start manual infusion

import math
import random
import pygame
import pygame_widgets
from simple_pid import PID
from pygame.locals import *

import pygame_gui

from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_label import UILabel
from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu
from pygame_widgets.dropdown import Dropdown

pygame.init()

clock = pygame.time.Clock()

#reads current bp, outputs calculated bp for the next timestep
def calculate_bp(cur_bp):
    t = cur_bp
    return (10*math.sin(t) + 53)
    
# constants
bp_wave_y = 200
done = False
c = 2 #scale factor
FPS = 20

# variables
bp = [53] # initial bp
target_bp = 50
new_target_bp = target_bp # temporary var for target bp
low_bound = target_bp - 5 # lower bound of target bp range
high_bound = target_bp + 5 # upper bound of target bp range
medication = "n/a"
new_medication = medication # temporary var for medication selected

#create the bp log
for t in range(0, 250):
    bp.append(calculate_bp(bp[-1]))

initial_avg = sum(bp)/len(bp)

pygame.display.set_caption('Ultimate Feedback')
window_surface = pygame.display.set_mode((800, 600)) # overall window
bp_wave = pygame.Surface((500, 200)) # display block for bp wave
dropdown_cover = pygame.Surface((200, 75)) # display block to hide/reset dropdown after selecting option

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#FFFFFF'))
window_surface.blit(background, (0, 0))

manager = pygame_gui.UIManager((800, 600), 'theme.json')

pygame.draw.rect(window_surface, pygame.Color('#000000'), pygame.Rect(510, 10, 280, 190), 2)
pygame.draw.rect(window_surface, pygame.Color('#000000'), pygame.Rect(510, 210, 280, 190), 2)
# text box for target MAP label
target_display_x = 600
target_display_y = 90
target_display_width = 150
target_display_height = 60
target_text = UILabel(pygame.Rect((target_display_x - 75, target_display_y), (75, 45)), "Target",
                  manager=manager)
# text box for target MAP
target_display = UITextBox(str(target_bp),
                       pygame.Rect((target_display_x, target_display_y), (target_display_width, target_display_height)),
                       manager=manager)

# text box for MAP label
bp_display_x = 600
bp_display_y = 20
bp_display_width = 150
bp_display_height = 60
bp_text = UILabel(pygame.Rect((bp_display_x - 75, bp_display_y), (75, 45)), "MAP",
                  manager=manager)
# text box for MAP
bp_display = UITextBox(str(0),
                       pygame.Rect((bp_display_x, bp_display_y), (bp_display_width, bp_display_height)),
                       manager=manager)

# text box for status label
status_x = 600
status_y = 150
status_width = 150
status_height = 30
status_text = UILabel(pygame.Rect((status_x - 75, status_y), (75, 45)), "Status",
                      manager=manager)
# box for status indicator
pygame.draw.rect(window_surface, pygame.Color('white'), pygame.Rect(status_x, status_y + 10, 60, status_height), 0, 10)
pygame.draw.rect(window_surface, pygame.Color('black'), pygame.Rect(status_x, status_y + 10, 60, status_height), 1, 10)

# text box for infusion rate label
infusion_display_x = 600
infusion_display_y = 250
infusion_display_width = 150
infusion_display_height = 60
infusion_text = UILabel(pygame.Rect((infusion_display_x - 75, infusion_display_y), (75, 45)), "Rate",
                        manager=manager)
# text box for infusion rate display
infusion_display = UITextBox(str(0),
                             pygame.Rect((infusion_display_x, infusion_display_y), (infusion_display_width, infusion_display_height)),
                             manager=manager)

# text box for medication label
med_display_x = 600
med_display_y = 325
med_display_width = 150
med_display_height = 60
med_text = UILabel(pygame.Rect((med_display_x - 75, med_display_y), (80, 45)), "Med",
                   manager=manager)
# text box for medication display
med_display = UITextBox(medication,
                        pygame.Rect((med_display_x, med_display_y), (med_display_width, med_display_height)),
                        manager=manager)

# target bp selection
target_select_x = 50
target_select_y = 250
target_select_width = 200
target_select_height = 100
med_text = UILabel(pygame.Rect((target_select_x, target_select_y - 40), (200, 45)), "Enter Target MAP",
                   manager=manager)
target_bp_display = UITextBox(str(target_bp),
                              pygame.Rect((target_select_x, target_select_y), (target_select_width, target_select_height)),
                              manager=manager)

# select_medication_display = UITextBox("Select medication:",
#                               pygame.Rect((select_med_x, select_med_y), (200, 100)),
#                               manager=manager)

# dropdown_display = pygame.Surface((200, 100))
# dropdown_display.fill(pygame.Color('#000000'))

enter_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((280, 500), (200, 50)), text='UPDATE', manager=manager)
stop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((510, 500), (280, 50)), text='STOP', manager=manager)
manual_override_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((510, 430), (280, 50)), text='OVERRIDE', manager=manager)
up_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((280, 250), (75, 40)), text='UP', manager=manager)
down_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((280, 310), (75, 40)), text='DOWN', manager=manager)

# med select menu
select_med_x = 50
select_med_y = 370
select_medication_text = UILabel(pygame.Rect((select_med_x, select_med_y), (200, 45)), "Select Medication",
                                 manager=manager)
menu_x = 50
menu_y = 410
menu_width = 200
menu_height = 80
menu = pygame_gui.elements.UIDropDownMenu(options_list={"n/a", "A", "B"},
                                          starting_option=medication,
                                          relative_rect=pygame.Rect((menu_x, menu_y), (menu_width, menu_height)),
                                          manager=manager)

# dropdown = Dropdown(
#     dropdown_display, 0, 0, 100, 50, name='Select Color',
#     choices=[
#         'Red',
#         'Blue',
#         'Yellow',
#     ],
#     borderRadius=3, colour=pygame.Color('green'), values=[1, 2, 'true'], direction='down', textHAlign='left'
# )

in_range = False
frame_counter = 0

while not done:
    time_delta = clock.tick(60)/1000.0
    manager.update(time_delta)
    clock.tick(FPS); #set framerate
    
    frame_counter = frame_counter + 1
    if not in_range:
        if frame_counter == 5:
            pygame.draw.rect(window_surface, pygame.Color('white'), pygame.Rect(status_x, status_y + 10, 60, status_height), 0, 10)
        if frame_counter == 10:
            pygame.draw.rect(window_surface, pygame.Color('red'), pygame.Rect(status_x, status_y + 10, 60, status_height), 0, 10)
            frame_counter = 0
    else:
        frame_counter = 0
        pygame.draw.rect(window_surface, pygame.Color('green'), pygame.Rect(status_x, status_y + 10, 60, status_height), 0, 10)
    pygame.draw.rect(window_surface, pygame.Color('black'), pygame.Rect(status_x, status_y + 10, 60, status_height), 1, 10)

    
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == enter_button:
                print("Update button pressed")
                target_bp = new_target_bp
                low_bound = target_bp - 5
                high_bound = target_bp + 5
                target_display = UITextBox(str(target_bp),
                                           pygame.Rect((target_display_x, target_display_y), (target_display_width, target_display_height)),
                                           manager=manager)
                # adjust medication display
                medication = new_medication
                med_display = UITextBox(medication,
                                        pygame.Rect((med_display_x, med_display_y), (med_display_width, med_display_height)),
                                        manager=manager)
                print("in range: ", in_range)
            if event.ui_element == stop_button:
                print("Stop button pressed")
            if event.ui_element == up_button:
                new_target_bp = new_target_bp + 1
                target_bp_display = UITextBox(str(new_target_bp),
                                              pygame.Rect((50, 250), (200, 100)),
                                              manager=manager)
                print("Up button pressed")
            if event.ui_element == down_button:
                new_target_bp = new_target_bp - 1
                target_bp_display = UITextBox(str(new_target_bp),
                                              pygame.Rect((50, 250), (200, 100)),
                                              manager=manager)
                print("Down button pressed")
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            print("Selected option:", event.text)
            new_medication = event.text
            # hide/reset dropdown options
            dropdown_cover.fill(pygame.Color("#ffffff"))
            window_surface.blit(dropdown_cover, (menu_x, menu_y + menu_height))

        manager.process_events(event)
        
    manager.update(FPS) # needed for button press to be registered


    manager.draw_ui(window_surface)
    # window_surface.blit(background, (0, 0))
    bp_wave.fill(pygame.Color("#000000"))

    #avg bp in given frame
    avg = sum(bp)/len(bp)
    if avg >= low_bound and avg <= high_bound:
        in_range = True
    else:
        in_range = False
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
    
    bp_display = UITextBox(str(int(avg)),
                           pygame.Rect((bp_display_x, bp_display_y), (bp_display_width, bp_display_height)),
                           manager=manager)
    
    infusion_display = UITextBox(str(0),
                        pygame.Rect((infusion_display_x, infusion_display_y), (infusion_display_width, infusion_display_height)),
                        manager=manager)
    
    # window_surface.blit(dropdown_display, (300, 400))
    # dropdown_display.fill(pygame.Color('#000000'))

    #update bp    
    bp.append(calculate_bp(bp[len(bp)-1])) #append calculated bp to end of array
    bp.pop(0) #remove first element from array
    
    pygame_widgets.update(events)
    pygame.display.flip()