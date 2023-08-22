import math
import random

# pygame imports
# -----------------------------------------------------
import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_label import UILabel
from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu
from pygame_gui.windows.ui_message_window import UIMessageWindow
from pygame_gui.elements.ui_text_entry_line import UITextEntryLine

# pygame set up
# -----------------------------------------------------
pygame.init()
clock = pygame.time.Clock()

# pid tuning parameters
# -----------------------------------------------------
P = 0.5 # coefficient of proportional term in pid equation
I = 0.014 # coefficient of integral term
D = 0.01 # coefficient of derivative term

# map model constants (see: https://www.proquest.com/docview/230725657?fromopenview=true&parentSessionId=W1kMUlbGIOWNRCDnOmr7ZIiBreMlbr1k0L7jFS3UGzY%3D&pq-origsite=gscholar)
# -----------------------------------------------------
b0 = 0.18661
bm = 0.07464
a1 = 0.74082
m = 3
d = 3

# variables for current and previous map change
# -----------------------------------------------------
previous_map_change = 0
map_change = 0

# store 100 most recent infusion rates
# -----------------------------------------------------
infusion_log = []
for i in range(0, 100):
    infusion_log.append(0)

# constants
# -----------------------------------------------------
done = False
c = 1 # scale factor for map graph
vertical_shift = 0 # vertical shift for map graph

# gui variables
# -----------------------------------------------------
bp_log = [] # array of past map values
initial_map = 80
current_map = 80
target_map = 65
new_target_bp = target_map # temporary var for target bp
low_bound = target_map - 5 # lower bound of target bp range
high_bound = target_map + 5 # upper bound of target bp range
medication = "n/a"
new_medication = medication # temporary var for medication selected
in_range = False
manual_mode = False
manual_infusion_rate = 0
new_manual_infusion_rate = 0
frame_counter = 0
locked = True
max_infusion = 140 # in ml/hr
fps = 10

#create the bp log
# -----------------------------------------------------
for t in range(0, 378):
    bp_log.append(current_map + random.randrange(-2, 2))
    
initial_avg = sum(bp_log)/len(bp_log) # find initial average map

# patient response to infusion rate
# -----------------------------------------------------
def response(infusion):
    global current_map
    global infusion_log
    global map_change
    global previous_map_change
    global medication
    global initial_map
    
    # update infusion log
    infusion_log.append(infusion)
    infusion_log.pop(0)
    # recursive map model from https://www.proquest.com/docview/230725657?fromopenview=true&parentSessionId=W1kMUlbGIOWNRCDnOmr7ZIiBreMlbr1k0L7jFS3UGzY%3D&pq-origsite=gscholar
    map_change = (b0 * infusion_log[len(infusion_log) - 1 - d]+ bm * infusion_log[len(infusion_log) - 1 - d - m] + a1 * previous_map_change)
    previous_map_change = map_change
    current_map = initial_map - map_change + random.randrange(-2, 2)
    # update map log
    bp_log.append(current_map)
    bp_log.pop(0)

# pygame window setup
# -----------------------------------------------------
pygame.display.set_caption("Ultimate Feedback")
window_surface = pygame.display.set_mode((800, 750)) # overall window

bp_wave_y = 200
bp_wave = pygame.Surface((760, 200)) # display block for bp wave

background = pygame.Surface((800, 750))
background.fill(pygame.Color("#000000"))

manager = pygame_gui.UIManager((800, 750), 'theme.json') # set up ui manager with theme file

# rectangle containers for display
# -----------------------------------------------------
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(10, 10, 780, 210), 0, 10) # bp wave box
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(10, 230, 410, 160), 0, 10) # current map box
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(430, 230, 360, 160), 0, 10) # target map box
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(10, 400, 410, 160), 0, 10) # med info box
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(430, 400, 360, 160), 0, 10) # manual override box
pygame.draw.rect(window_surface, pygame.Color('#2b2b2b'), pygame.Rect(10, 570, 780, 60), 0, 10) # buttons box

# current MAP label
# -----------------------------------------------------
bp_display_x = 20
bp_display_y = 270
bp_display_width = 200
bp_display_height = 100
bp_text = UILabel(pygame.Rect((bp_display_x, bp_display_y - 40), (200, 45)),
                  "Current MAP (mmHg)",
                  manager=manager)

# current MAP display
# -----------------------------------------------------
bp_display = UITextBox(str(0),
                       pygame.Rect((bp_display_x, bp_display_y), (bp_display_width, bp_display_height)),
                       manager=manager)

# status indicator label
# -----------------------------------------------------
status_x = 250
status_y = 270
status_width = 150
status_height = 60
status_text = UILabel(pygame.Rect((status_x, status_y - 40), (status_width, 45)),
                      "Status",
                      manager=manager)

# status indicator
# -----------------------------------------------------
pygame.draw.rect(window_surface, pygame.Color('white'), pygame.Rect(status_x, status_y, status_width, status_height), 0, 10)
pygame.draw.rect(window_surface, pygame.Color('black'), pygame.Rect(status_x, status_y, status_width, status_height), 1, 10)


# status in medication select box
# -----------------------------------------------------
med_status_x = 20
med_status_y = 510
med_status_width = 390
med_status_height = 40
med_status = UITextBox("SELECT MED TO BEGIN INFUSION", pygame.Rect((med_status_x, med_status_y), (med_status_width, med_status_height)), 
                  manager=manager, object_id="#med_status")

# infusion rate label
# -----------------------------------------------------
infusion_display_x = 20
infusion_display_y = 440
infusion_display_width = 150
infusion_display_height = 60
infusion_text = UILabel(pygame.Rect((infusion_display_x, infusion_display_y - 40), (infusion_display_width, 45)), "Rate (ml/hr)",
                        manager=manager)

# infusion rate display
# -----------------------------------------------------
infusion_display = UITextBox(str(infusion_log[len(infusion_log) - 1]),
                             pygame.Rect((infusion_display_x, infusion_display_y), (infusion_display_width, infusion_display_height)),
                             manager=manager)

# target map selection
# -----------------------------------------------------
target_select_x = 440
target_select_y = 270
target_select_width = 200
target_select_height = 100
target_map_text = UILabel(pygame.Rect((target_select_x, target_select_y - 40), (200, 45)), "Target MAP (mmHg)",
                   manager=manager)
target_bp_display = UITextBox(str(target_map),
                              pygame.Rect((target_select_x, target_select_y), (target_select_width, target_select_height)),
                              manager=manager)

# up and down buttons for target map
# -----------------------------------------------------
up_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((target_select_x+220, target_select_y), (100, 40)), text='UP', manager=manager)
down_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((target_select_x+220, target_select_y+60), (100, 40)), text='DOWN', manager=manager)

# lock/unlock input button
# -----------------------------------------------------
lock_button_x = 20
lock_button_y = 580
lock_button_width = 240
lock_button_height = 40
lock_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((lock_button_x, lock_button_y), (lock_button_width, lock_button_height)), text='UNLOCK INPUT', manager=manager, object_id="#unlock_button")

# system stop button
# -----------------------------------------------------
stop_button_x = 530
stop_button_y = 580
stop_button_width = 250
stop_button_height = 40
stop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((stop_button_x, stop_button_y), (stop_button_width, stop_button_height)), text='STOP', manager=manager, object_id="#stop_button")

# manual override button
# -----------------------------------------------------
manual_override_x = 270
manual_override_y = 580
manual_override_width = 250
manual_override_height = 40
manual_override_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((manual_override_x, manual_override_y), (manual_override_width, manual_override_height)), text='MANUAL OVERRIDE', manager=manager, object_id="#override_button")

# overall system info display on the bottom of the interface
# -----------------------------------------------------
system_popup_x = 10
system_popup_y = 640
system_popup = UITextBox("",
                         pygame.Rect((system_popup_x, system_popup_y), (780, 100)),
                         manager=manager, object_id="#system_resume_popup")

# manual info display under manual override input
# -----------------------------------------------------
manual_info_x = 450
manual_info_y = 510
manual_info_width = 300
manual_info_height = 40
manual_info = UITextBox("MANUAL MODE IS NOT ENABLED", pygame.Rect((manual_info_x, manual_info_y), (manual_info_width, manual_info_height)), 
                                   manager=manager, object_id="#med_status")

# manual entry for infusion rate
# -----------------------------------------------------
manual_x = 450
manual_y = 440
manual_width = 300
manual_height = 45
manual_label = UILabel(pygame.Rect((manual_x, manual_y-40), (manual_width+10, 50)), "Infusion Rate (ml/hr) (Manual)",
                   manager=manager)
manual_entry = UITextEntryLine(relative_rect=pygame.Rect((manual_x, manual_y), (manual_width, manual_height)), manager=manager)

# med select menu
# -----------------------------------------------------
select_med_x = 200
select_med_y = 440
select_med_width = 200
select_med_height = 45
select_medication_text = UILabel(pygame.Rect((select_med_x, select_med_y-40), (select_med_width, 45)), "Select Medication",
                                 manager=manager)
menu = UIDropDownMenu(options_list={"n/a", "Sodium nitroprusside"},
                      starting_option=medication,
                      relative_rect=pygame.Rect((select_med_x, select_med_y), (select_med_width, select_med_height)),
                      manager=manager)

dropdown_cover = pygame.Surface((200, 75)) # display block to hide/reset dropdown after selecting option

timestep = 1 # determines how many seconds each loop iteration represents

integral = 0 # track integral of error over time for pid
derivative = 0 # track derivative of error

system_stop = False # var for whether stop button was activated

counter = 0 # count loop iterations

# main loop
while not done:
    time_delta = timestep
    clock.tick(fps)
    
    frame_counter = frame_counter + 1
    
    # if map not in range, status indicator flashes red
    # if map in range, status indicator is steady green
    if not in_range:
        if frame_counter == 5:
            pygame.draw.rect(window_surface, pygame.Color('white'), pygame.Rect(status_x, status_y, status_width, status_height), 0, 10)
        if frame_counter == 10:
            pygame.draw.rect(window_surface, pygame.Color('red'), pygame.Rect(status_x, status_y, status_width, status_height), 0, 10)
            frame_counter = 0
    else:
        frame_counter = 0
        pygame.draw.rect(window_surface, pygame.Color('green'), pygame.Rect(status_x, status_y, status_width, status_height), 0, 10)
    pygame.draw.rect(window_surface, pygame.Color('black'), pygame.Rect(status_x, status_y, status_width, status_height), 1, 10)

    # handle user inputs
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame_gui.UI_BUTTON_PRESSED: 
            # handle stop button
            if event.ui_element == stop_button:
                print("Stop button pressed")
                # if system already stopped, then button is reset button; on press, reset system
                if system_stop:
                    integral = 0 # reset the integral term of the PID controller
                    system_stop = False
                    manual_mode = False
                    stop_button.set_text("STOP")
                    med_status.set_text("SELECT MED TO BEGIN INFUSION")
                    manual_info.set_text("MANUAL MODE IS NOT ENABLED")
                    manual_override_button.set_text("MANUAL OVERRIDE")
                    system_popup.set_text("SYSTEM IS RUNNING. AUTOMATIC CONTROL IS ENABLED.")
                    menu = UIDropDownMenu(options_list={"n/a", "Sodium nitroprusside"},
                      starting_option="n/a",
                      relative_rect=pygame.Rect((select_med_x, select_med_y), (select_med_width, select_med_height)),
                      manager=manager)
                else:
                    # if stop button pressed, stop the system
                    system_stop = True
                    stop_button.set_text("RESET")
                    med_status.set_text("INFUSION STOPPED")
                    manual_info.set_text("INFUSION STOPPED")
                    system_popup.set_text("SYSTEM STOPPED. INFUSION RATE IS 0. PRESS RESET TO RESUME CONTROL.")
                    menu = UIDropDownMenu(options_list={"n/a", "Sodium nitroprusside"},
                      starting_option="n/a",
                      relative_rect=pygame.Rect((select_med_x, select_med_y), (select_med_width, select_med_height)),
                      manager=manager)
                    
            # handle up button press
            if event.ui_element == up_button and not system_stop and not locked:
                integral = 0 # reset the integral term of the PID controller
                new_target_bp = new_target_bp + 1
                target_map = new_target_bp
                low_bound = target_map - 5
                high_bound = target_map + 5
                target_bp_display.set_text(str(new_target_bp))
                print("Up button pressed")
            
            # handle down button press
            if event.ui_element == down_button and not system_stop and not locked:
                integral = 0 # reset the integral term of the PID controller
                new_target_bp = new_target_bp - 1
                target_map = new_target_bp
                low_bound = target_map - 5
                high_bound = target_map + 5
                target_bp_display.set_text(str(new_target_bp))
                print("Down button pressed")
                
            # handle manual override press
            if event.ui_element == manual_override_button and not system_stop:
                print("override button pressed")
                # if not in manual mode, change to manual mode
                if not manual_mode:
                    manual_mode = True
                    manual_info.set_text("INPUT INFUSION RATE")
                    med_status.set_text("Mode: MANUAL INFUSION")
                    system_popup.set_text("MANUAL MODE ENABLED. INPUT THE INFUSION RATE AND PRESS ENTER. PRESS RESUME AUTO TO RESUME AUTOMATIC CONTROL.")
                    manual_override_button.set_text("RESUME AUTO")
                else:
                    # if already in manual mode, then button is resume auto button; on press, resume auto infusion
                    integral = 0 # reset the integral term of the PID controller
                    manual_mode = False
                    print("resume auto mode")
                    manual_info.set_text("MANUAL MODE IS NOT ENABLED")
                    system_popup.set_text("SYSTEM IS RUNNING. AUTOMATIC CONTROL IS ENABLED.")
                    manual_override_button.set_text("MANUAL OVERRIDE")
            # handle input lock button
            if event.ui_element == lock_button and not system_stop:
                print("unlock button pressed")
                # if locked, then unlock input
                if locked:
                    locked = False
                    lock_button.set_text("LOCK INPUT")
                else:
                    # if unlocked, then lock input
                    locked = True
                    lock_button.set_text("UNLOCK INPUT")
                    
        # handle drop down menu selection: set new medication         
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if not system_stop and not locked:
                print("Selected option:", event.text)
                new_medication = event.text
                medication = new_medication
                if medication != "n/a":
                    integral = 0 # reset the integral term of the PID controller
                    med_status.set_text("Mode: AUTO INFUSION")
            
            # hide/reset dropdown options
            dropdown_cover.fill(pygame.Color("#2b2b2b"))
            window_surface.blit(dropdown_cover, (select_med_x, select_med_y + select_med_height))

        # handle manual infusion rate entry
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and not system_stop and not locked:
            print("Entered text:", event.text)
            manual_infusion_rate_string = event.text
            # check if manual infusion is a valid input (float)
            try:
                float(manual_infusion_rate_string)
                new_manual_infusion_rate = float(event.text)
                if new_manual_infusion_rate < 0 or new_manual_infusion_rate > max_infusion:
                    print("invalid infusion rate")
                else:
                    manual_infusion_rate = new_manual_infusion_rate
                    print("new manual_infusion_rate: ", new_manual_infusion_rate)
                    manual_entry.set_text("") 
            except:
                print("invalid infusion rate")

        manager.process_events(event)
        
    manager.update(1/fps) # needed for button press to be registered
    
    counter += 1
    
    # PID controller (run every timestep)
    if counter % fps == 0:
        error = current_map - target_map
        # only run pid if auto infusion is activated
        if medication != "n/a":
            integral += error * timestep
        derivative = ((bp_log[len(bp_log) - 1] - target_map) - (bp_log[len(bp_log) - 2] - target_map)) / timestep
        control = P * error + I * integral + D * derivative # control is new infusion rate
        
        # check infusion rate within valid range, check whether system stopped or in manual mode
        if control < 0 or current_map < low_bound:
            control = 0
        if control > max_infusion:
            control = max_infusion
        if system_stop:
            control = 0
            medication = "n/a"        
        if manual_mode:
            control = manual_infusion_rate
        if medication == "n/a":
            control = 0
            
        response(control) # input infusion rate into patient model

    manager.draw_ui(window_surface)
    bp_wave.fill(pygame.Color("#2b2b2b"))

    #avg bp in last 10 seconds
    sum = 0
    for i in range(1, 11):
        sum += bp_log[len(bp_log) - i]
    avg = sum / 10
    if avg >= low_bound and avg <= high_bound:
        in_range = True
    else:
        in_range = False

    #draw axes
    pygame.draw.line(bp_wave, (255, 255, 255), (0, 0), (0, 200), width=2)
    for i in range (200):
        if (i % 20 == 0):
            pygame.draw.line(bp_wave, (255, 255, 255), (0, 200-i), (10, 200-i), width=1)            

    # draw lines
    #lower boundary
    pygame.draw.line(bp_wave, (203, 76, 78), (0,(bp_wave_y-c*low_bound+vertical_shift)), ((760, (bp_wave_y-c*low_bound+vertical_shift))), width=2)
    #upper boundary
    pygame.draw.line(bp_wave, (203, 76, 78), (0,(bp_wave_y-c*high_bound+vertical_shift)), ((760, (bp_wave_y-c*high_bound+vertical_shift))), width=2)
    #mean
    pygame.draw.line(bp_wave, (0, 0, 255), (0,(bp_wave_y-c*avg+vertical_shift)), ((760, (bp_wave_y-c*avg+vertical_shift))), width=3)
    #target
    pygame.draw.line(bp_wave, (150, 210, 148), (0,(bp_wave_y-c*target_map+vertical_shift)), ((760, (bp_wave_y-c*target_map+vertical_shift))), width=2)

    #iterates and draws line between bp points
    for i in range(len(bp_log) - 1):
        pygame.draw.line(bp_wave, (4, 217, 255), (int(i*2*c),(bp_wave_y-c*bp_log[i]+vertical_shift)), (int((i+1)*2*c), (bp_wave_y-c*bp_log[i+1]+vertical_shift)), width=3)
        
    window_surface.blit(bp_wave, (20, 20))

    # update current map display
    bp_display.set_text(str(round(bp_log[len(bp_log) - 1], 2)))
    
    # update current infusion rate display
    infusion_display.set_text(str(round(infusion_log[len(infusion_log) - 1], 2)))
    
    pygame.display.flip()