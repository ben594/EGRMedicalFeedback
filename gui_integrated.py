import math
import random
import pygame
import pygame_widgets
from simple_pid import PID
from pygame.locals import *

# pygame gui imports
# -----------------------------------------------------
import pygame_gui
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_label import UILabel
from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu
from pygame_gui.windows.ui_message_window import UIMessageWindow

# set up pid stuff
# -----------------------------------------------------
pygame.init()
clock = pygame.time.Clock()

# pid tuning parameters
# -----------------------------------------------------
P = 0.75
I = 0.0140
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
for i in range(0, 10):
    infusion_log.append(0)

# constants
# -----------------------------------------------------
bp_wave_y = 200
done = False
c = 2 #scale factor

# gui variables
# -----------------------------------------------------
bp_log = [] # initial bp
map = 80
target_bp = map
new_target_bp = target_bp # temporary var for target bp
low_bound = target_bp - 5 # lower bound of target bp range
high_bound = target_bp + 5 # upper bound of target bp range
medication = "n/a"
new_medication = medication # temporary var for medication selected
in_range = False
manual_mode = False
frame_counter = 0

#create the bp log
# -----------------------------------------------------
for t in range(0, 125):
    bp_log.append(map)
    
initial_avg = sum(bp_log)/len(bp_log)

# patient response to infusion rate
# -----------------------------------------------------
def response(infusion):
    global map
    global infusion_log
    global map_change
    global previous_map_change
    
    # print("new infusion: ", infusion)
    infusion_log.append(infusion)
    infusion_log.pop(0)
    map_change = b0 * infusion_log[9 - d]+ bm * infusion_log[9 - d - m] + a1 * previous_map_change
    map = map - map_change
    bp_log.append(map)
    bp_log.pop(0)

# pygame window setup
# -----------------------------------------------------
pygame.display.set_caption('Ultimate Feedback')
window_surface = pygame.display.set_mode((800, 600)) # overall window
bp_wave = pygame.Surface((480, 200)) # display block for bp wave
dropdown_cover = pygame.Surface((200, 75)) # display block to hide/reset dropdown after selecting option

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#4d5052'))
window_surface.blit(background, (0, 0))

manager = pygame_gui.UIManager((800, 600), 'theme.json')

# rectangle containers for display
# -----------------------------------------------------
pygame.draw.rect(window_surface, pygame.Color('white'), pygame.Rect(510, 10, 280, 190), 2, 10)
pygame.draw.rect(window_surface, pygame.Color('white'), pygame.Rect(510, 210, 280, 190), 2, 10)

# target MAP label
# -----------------------------------------------------
target_display_x = 600
target_display_y = 90
target_display_width = 150
target_display_height = 60
target_text = UILabel(pygame.Rect((target_display_x - 75, target_display_y), (75, 45)), "Target",
                  manager=manager)

# target MAP display
# -----------------------------------------------------
target_display = UITextBox(str(target_bp),
                           pygame.Rect((target_display_x, target_display_y), (target_display_width, target_display_height)),
                           manager=manager)

# current MAP label
# -----------------------------------------------------
bp_display_x = 600
bp_display_y = 20
bp_display_width = 150
bp_display_height = 60
bp_text = UILabel(pygame.Rect((bp_display_x - 75, bp_display_y), (75, 45)), "MAP",
                  manager=manager)

# current MAP display
# -----------------------------------------------------
bp_display = UITextBox(str(0),
                       pygame.Rect((bp_display_x, bp_display_y), (bp_display_width, bp_display_height)),
                       manager=manager)

# status label
# -----------------------------------------------------
status_x = 600
status_y = 150
status_width = 150
status_height = 30
status_text = UILabel(pygame.Rect((status_x - 75, status_y), (75, 45)), "Status",
                      manager=manager)

# status indicator display
# -----------------------------------------------------
pygame.draw.rect(window_surface, pygame.Color('white'), pygame.Rect(status_x, status_y + 10, 60, status_height), 0, 10)
pygame.draw.rect(window_surface, pygame.Color('black'), pygame.Rect(status_x, status_y + 10, 60, status_height), 1, 10)

# infusion rate label
# -----------------------------------------------------
infusion_display_x = 600
infusion_display_y = 250
infusion_display_width = 150
infusion_display_height = 60
infusion_text = UILabel(pygame.Rect((infusion_display_x - 75, infusion_display_y), (75, 45)), "Rate",
                        manager=manager)
# infusion rate display
# -----------------------------------------------------
infusion_display = UITextBox(str(infusion_log[len(infusion_log) - 1]),
                             pygame.Rect((infusion_display_x, infusion_display_y), (infusion_display_width, infusion_display_height)),
                             manager=manager)

# current medication label
# -----------------------------------------------------
med_display_x = 600
med_display_y = 325
med_display_width = 150
med_display_height = 60
med_text = UILabel(pygame.Rect((med_display_x - 75, med_display_y), (80, 45)), "Med",
                   manager=manager)

# current medication display
# -----------------------------------------------------
med_display = UITextBox(medication,
                        pygame.Rect((med_display_x, med_display_y), (med_display_width, med_display_height)),
                        manager=manager)

# target bp selection
# -----------------------------------------------------
target_select_x = 50
target_select_y = 250
target_select_width = 200
target_select_height = 100
med_text = UILabel(pygame.Rect((target_select_x, target_select_y - 40), (200, 45)), "Enter Target MAP",
                   manager=manager)
target_bp_display = UITextBox(str(target_bp),
                              pygame.Rect((target_select_x, target_select_y), (target_select_width, target_select_height)),
                              manager=manager)

enter_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((280, 430), (200, 120)), text='UPDATE', manager=manager, object_id="#update_button")
stop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((510, 500), (280, 50)), text='STOP', manager=manager, object_id="#stop_button")
manual_override_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((510, 430), (280, 50)), text='OVERRIDE', manager=manager, object_id="#override_button")
up_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((280, 250), (200, 40)), text='UP', manager=manager)
down_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((280, 310), (200, 40)), text='DOWN', manager=manager)

# med select menu
# -----------------------------------------------------
select_med_x = 50
select_med_y = 390
select_medication_text = UILabel(pygame.Rect((select_med_x, select_med_y), (200, 45)), "Select Medication",
                                 manager=manager)
menu_x = 50
menu_y = 430
menu_width = 200
menu_height = 50
menu = UIDropDownMenu(options_list={"n/a", "A", "B"},
                      starting_option=medication,
                      relative_rect=pygame.Rect((menu_x, menu_y), (menu_width, menu_height)),
                      manager=manager)

timestep = 1/10
integral = 0
derivative = 0

# main loop
while not done:
    time_delta = clock.tick(1/timestep)
    manager.update(time_delta/1000)
    # clock.tick(FPS); #set framerate
    
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
                popup = UIMessageWindow(pygame.Rect((0, 0), (800, 600)), "hello", manager=manager)
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
            if event.ui_element == manual_override_button:
                manual_mode = True
                
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            print("Selected option:", event.text)
            new_medication = event.text
            # hide/reset dropdown options
            dropdown_cover.fill(pygame.Color("#4d5052"))
            window_surface.blit(dropdown_cover, (menu_x, menu_y + menu_height))

        manager.process_events(event)
        
    manager.update(timestep) # needed for button press to be registered
    
    error = map - target_bp
    integral += error * timestep
    derivative = (bp_log[len(bp_log) - 1] - bp_log[len(bp_log) - 2]) / timestep
    control = P * error + I * integral + D * derivative
    response(control)

    manager.draw_ui(window_surface)
    bp_wave.fill(pygame.Color("#111111"))

    #avg bp in given frame
    avg = sum(bp_log)/len(bp_log)
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
    for i in range(len(bp_log) - 1):
        pygame.draw.line(bp_wave, (0, 128, 255), (int(i*2*c),(bp_wave_y-c*bp_log[i])), (int((i+1)*2*c), (bp_wave_y-c*bp_log[i+1])))
        
    window_surface.blit(bp_wave, (0, 0))
    
    bp_display = UITextBox(str(round(avg, 2)),
                           pygame.Rect((bp_display_x, bp_display_y), (bp_display_width, bp_display_height)),
                           manager=manager)
    
    infusion_display = UITextBox(str(round(infusion_log[len(infusion_log) - 1], 2)),
                        pygame.Rect((infusion_display_x, infusion_display_y), (infusion_display_width, infusion_display_height)),
                        manager=manager)
    
    pygame_widgets.update(events)
    pygame.display.flip()