import math
import random
import pygame
from simple_pid import PID
from pygame.locals import *

# pygame gui imports
# -----------------------------------------------------
import pygame_gui
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_label import UILabel
from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu
from pygame_gui.windows.ui_message_window import UIMessageWindow
from pygame_gui.elements.ui_text_entry_line import UITextEntryLine

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
c = 3 #scale factor
vertical_shift = 100

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
manual_infusion_rate = 0
new_manual_infusion_rate = 0
frame_counter = 0

#create the bp log
# -----------------------------------------------------
for t in range(0, 80):
    bp_log.append(map)
    
initial_avg = sum(bp_log)/len(bp_log)

# patient response to infusion rate
# -----------------------------------------------------
def response(infusion):
    global map
    global infusion_log
    global map_change
    global previous_map_change
    global medication
    
    # print("infusion: ", infusion)
    
    # print("new infusion: ", infusion)
    infusion_log.append(infusion)
    infusion_log.pop(0)
    map_change = b0 * infusion_log[9 - d]+ bm * infusion_log[9 - d - m] + a1 * previous_map_change + random.randrange(-2, 2)
    map = map - map_change
    bp_log.append(map)
    bp_log.pop(0)

# pygame window setup
# -----------------------------------------------------
pygame.display.set_caption("Ultimate Feedback")
window_surface = pygame.display.set_mode((800, 750)) # overall window
bp_wave = pygame.Surface((470, 180)) # display block for bp wave
dropdown_cover = pygame.Surface((200, 75)) # display block to hide/reset dropdown after selecting option

background = pygame.Surface((800, 750))
background.fill(pygame.Color("#000000"))
# window_surface.blit(background, (0, 0))

manager = pygame_gui.UIManager((800, 750), 'theme.json')

# rectangle containers for display
# -----------------------------------------------------
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(510, 10, 280, 190), 0, 10)
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(510, 210, 280, 240), 0, 10)
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(10, 210, 490, 160), 0, 10)
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(10, 460, 250, 170), 0, 10)
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(270, 460, 230, 170), 0, 10)
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(510, 460, 280, 170), 0, 10)
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(10, 10, 490, 190), 0, 10)
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(10, 380, 490, 70), 0, 10)

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
                        manager=manager, object_id="#med_display")

# target bp selection
# -----------------------------------------------------
target_select_x = 35
target_select_y = 250
target_select_width = 200
target_select_height = 100
target_map_text = UILabel(pygame.Rect((target_select_x, target_select_y - 40), (200, 45)), "Enter Target MAP",
                   manager=manager)
target_bp_display = UITextBox(str(target_bp),
                              pygame.Rect((target_select_x, target_select_y), (target_select_width, target_select_height)),
                              manager=manager)

enter_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((285, 480), (200, 120)), text='UPDATE', manager=manager, object_id="#update_button")
stop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 550), (260, 50)), text='STOP', manager=manager, object_id="#stop_button")
manual_override_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 480), (260, 50)), text='MANUAL OVERRIDE', manager=manager, object_id="#override_button")
up_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((285, 250), (200, 40)), text='UP', manager=manager)
down_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((285, 310), (200, 40)), text='DOWN', manager=manager)

# system info display on the bottom of the interface
system_popup_x = 10
system_popup_y = 640
system_popup = UITextBox("SYSTEM IS RUNNING. AUTOMATIC CONTROL IS ENABLED. SELECT A MEDICATION.",
                         pygame.Rect((system_popup_x, system_popup_y), (780, 100)),
                         manager=manager, object_id="#system_resume_popup")

# manual entry for infusion rate
manual_label = UILabel(pygame.Rect((35, 390), (210, 50)), "Infusion Rate (Manual)",
                   manager=manager)
manual_entry = UITextEntryLine(relative_rect=pygame.Rect((285, 390), (200, 50)), manager=manager)

# med select menu
# -----------------------------------------------------
select_med_x = 35
select_med_y = 460
select_medication_text = UILabel(pygame.Rect((select_med_x, select_med_y), (200, 45)), "Select Medication",
                                 manager=manager)
menu_x = 35
menu_y = select_med_y + 40
menu_width = 200
menu_height = 50
menu = UIDropDownMenu(options_list={"n/a", "Sodium nitroprusside", "B"},
                      starting_option=medication,
                      relative_rect=pygame.Rect((menu_x, menu_y), (menu_width, menu_height)),
                      manager=manager)

timestep = 1/10
integral = 0
derivative = 0

system_stop = False


# main loop
while not done:
    time_delta = clock.tick(1/timestep)
    manager.update(time_delta)
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
            if event.ui_element == enter_button and not system_stop:
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
                                        manager=manager, object_id="#med_display")
                print("in range: ", in_range)
                print("medication: ", medication)
                
                if manual_mode:
                    print("manual infusion rate updated: ", manual_infusion_rate)
                    manual_infusion_rate = new_manual_infusion_rate
                    
            if event.ui_element == stop_button:
                print("Stop button pressed")
                if system_stop:
                    system_stop = False
                    manual_mode = False
                    resume_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 550), (260, 50)), text='STOP', manager=manager, object_id="#stop_button")
                    resume_auto_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 480), (260, 50)), text='OVERRIDE', manager=manager, object_id="#override_button")
                    system_popup = UITextBox("SYSTEM IS RUNNING. AUTOMATIC CONTROL IS ENABLED. SELECT A MEDICATION.",
                                        pygame.Rect((system_popup_x, system_popup_y), (780, 100)),
                                        manager=manager, object_id="#system_resume_popup")
                else:
                    system_stop = True
                    resume_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 550), (260, 50)), text='RESET', manager=manager, object_id="#reset_button")
                    med_display = UITextBox("n/a",
                                            pygame.Rect((med_display_x, med_display_y), (med_display_width, med_display_height)),
                                            manager=manager, object_id="#med_display")
            if event.ui_element == up_button and not system_stop:
                new_target_bp = new_target_bp + 1
                target_bp_display = UITextBox(str(new_target_bp),
                                              pygame.Rect((target_select_x, target_select_y), (target_select_width, target_select_height)),
                                              manager=manager)
                print("Up button pressed")
            if event.ui_element == down_button and not system_stop:
                new_target_bp = new_target_bp - 1
                target_bp_display = UITextBox(str(new_target_bp),
                                              pygame.Rect((target_select_x, target_select_y), (target_select_width, target_select_height)),
                                              manager=manager)
                print("Down button pressed")
            if event.ui_element == manual_override_button and not system_stop:
                print("override button pressed")
                if not manual_mode:
                    manual_mode = True
                    system_popup = UITextBox("MANUAL MODE ENABLED. SELECT A MEDICATION. INPUT THE INFUSION RATE AND PRESS ENTER. PRESS RESUME AUTO TO RESUME AUTOMATIC CONTROL.",
                                            pygame.Rect((system_popup_x, system_popup_y), (780, 100)),
                                            manager=manager, object_id="#system_manual_popup")
                    resume_auto_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 480), (260, 50)), text='RESUME AUTO', manager=manager, object_id="#resume_auto_button")
                    # manual_override_button.set_text("RESUME AUTO")
                else:
                    manual_mode = False
                    print("resume auto mode")
                    system_popup = UITextBox("SYSTEM IS RUNNING. AUTOMATIC CONTROL IS ENABLED. SELECT A MEDICATION.",
                                             pygame.Rect((system_popup_x, system_popup_y), (780, 100)),
                                             manager=manager, object_id="#system_resume_popup")
                    resume_auto_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 480), (260, 50)), text='MANUAL OVERRIDE', manager=manager, object_id="#override_button")
                    # manual_override_button.set_text("MANUAL OVERRIDE")
                
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and not system_stop:
            print("Selected option:", event.text)
            new_medication = event.text
            # hide/reset dropdown options
            dropdown_cover.fill(pygame.Color("#2b2b2b"))
            window_surface.blit(dropdown_cover, (menu_x, menu_y + menu_height))

        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and not system_stop:
             print("Entered text:", event.text)
             new_manual_infusion_rate = float(event.text)
             print("new manual_infusion_rate: ", new_manual_infusion_rate)
             manual_entry.set_text("")
                 
            #  manual_entry = UITextEntryLine(relative_rect=pygame.Rect((285, 390), (200, 50)), manager=manager)

        manager.process_events(event)
        
    manager.update(timestep) # needed for button press to be registered
    
    error = map - target_bp
    integral += error * timestep
    derivative = (bp_log[len(bp_log) - 1] - bp_log[len(bp_log) - 2]) / timestep
    control = P * error + I * integral + D * derivative
    if control < 0:
        control = 0
    if system_stop:
        # print("stop pressed")
        control = 0
        medication = "n/a"
        # popup 
        system_popup = UITextBox("SYSTEM STOPPED. INFUSION IS NOW 0. PRESS RESET TO RESUME CONTROL.",
                                    pygame.Rect((system_popup_x, system_popup_y), (780, 100)),
                                    manager=manager, object_id="#system_stop_popup")
    if manual_mode:
        control = manual_infusion_rate
    # print("control: ", control)
    
    if medication == "n/a":
        # print("infusion is 0, medication is: ", medication)
        control = 0
    response(control)

    manager.draw_ui(window_surface)
    bp_wave.fill(pygame.Color("#2b2b2b"))

    #avg bp in given frame
    avg = sum(bp_log)/len(bp_log)
    if avg >= low_bound and avg <= high_bound:
        in_range = True
    else:
        in_range = False
        
    # draw lines
    #lower boundary
    pygame.draw.line(bp_wave, (203, 76, 78), (0,(bp_wave_y-c*low_bound+vertical_shift)), ((500, (bp_wave_y-c*low_bound+vertical_shift))), width=2)
    #upper boundary
    pygame.draw.line(bp_wave, (203, 76, 78), (0,(bp_wave_y-c*high_bound+vertical_shift)), ((500, (bp_wave_y-c*high_bound+vertical_shift))), width=2)
    #mean
    pygame.draw.line(bp_wave, (0, 0, 255), (0,(bp_wave_y-c*avg+vertical_shift)), ((500, (bp_wave_y-c*avg+vertical_shift))), width=3)
    #target
    pygame.draw.line(bp_wave, (150, 210, 148), (0,(bp_wave_y-c*target_bp+vertical_shift)), ((500, (bp_wave_y-c*target_bp+vertical_shift))), width=2)

    #iterates and draws line between bp points
    for i in range(len(bp_log) - 1):
        pygame.draw.line(bp_wave, (4, 217, 255), (int(i*2*c),(bp_wave_y-c*bp_log[i]+vertical_shift)), (int((i+1)*2*c), (bp_wave_y-c*bp_log[i+1]+vertical_shift)), width=3)
        
    window_surface.blit(bp_wave, (20, 20))
    
    bp_display = UITextBox(str(round(avg, 2)),
                           pygame.Rect((bp_display_x, bp_display_y), (bp_display_width, bp_display_height)),
                           manager=manager)
    
    if not system_stop:
        med_text = UILabel(pygame.Rect((med_display_x - 75, med_display_y), (80, 45)), "Med",
                           manager=manager)
        med_display = UITextBox(medication,
                                pygame.Rect((med_display_x, med_display_y), (med_display_width, med_display_height)),
                                manager=manager, object_id="#med_display")
        infusion_text = UILabel(pygame.Rect((infusion_display_x - 75, infusion_display_y), (75, 45)), "Rate",
                                manager=manager)
        infusion_display = UITextBox(str(round(infusion_log[len(infusion_log) - 1], 2)),
                            pygame.Rect((infusion_display_x, infusion_display_y), (infusion_display_width, infusion_display_height)),
                            manager=manager)
    
    pygame.display.flip()