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

# label for infusion mode
# mode_x = 500
# mode_y = 20
# mode_width = 100
# mode_height = 45
# mode_text = UILabel(pygame.Rect((mode_x, mode_y), (75, 45)), "Mode",
#                     manager=manager)

# text box for target MAP label
target_display_x = 675
target_display_y = 50
target_display_width = 100
target_display_height = 45
target_text = UILabel(pygame.Rect((target_display_x, target_display_y - 40), (75, 45)), "Target",
                  manager=manager)
# text box for target MAP
target_display = UITextBox(str(target_bp),
                       pygame.Rect((target_display_x, target_display_y), (target_display_width, target_display_height)),
                       manager=manager)

# text box for MAP label
bp_display_x = 530
bp_display_y = 50
bp_display_width = 100
bp_display_height = 45
bp_text = UILabel(pygame.Rect((bp_display_x - 10, bp_display_y - 40), (75, 45)), "MAP",
                  manager=manager)
# text box for MAP
bp_display = UITextBox(str(0),
                       pygame.Rect((bp_display_x, bp_display_y), (bp_display_width, bp_display_height)),
                       manager=manager)

# text box for infusion rate label
infusion_display_x = 530
infusion_display_y = 140
infusion_display_width = 100
infusion_display_height = 45
infusion_text = UILabel(pygame.Rect((infusion_display_x - 50, infusion_display_y - 40), (200, 45)), "Infusion Rate",
                        manager=manager)
# text box for infusion rate display
infusion_display = UITextBox(str(0),
                             pygame.Rect((infusion_display_x, infusion_display_y), (infusion_display_width, infusion_display_height)),
                             manager=manager)

# text box for medication label
med_display_x = 675
med_display_y = 140
med_display_width = 100
med_display_height = 45
med_text = UILabel(pygame.Rect((med_display_x, med_display_y - 40), (100, 45)), "Medication",
                   manager=manager)
# text box for medication display
med_display = UITextBox(medication,
                        pygame.Rect((med_display_x, med_display_y), (med_display_width, med_display_height)),
                        manager=manager)


target_bp_display = UITextBox("Target MAP: " + str(target_bp),
                              pygame.Rect((50, 250), (200, 100)),
                              manager=manager)

select_medication_display = UITextBox("Select medication:",
                              pygame.Rect((50, 400), (200, 100)),
                              manager=manager)

# dropdown_display = pygame.Surface((200, 100))
# dropdown_display.fill(pygame.Color('#000000'))

enter_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 250), (200, 100)), text='UPDATE', manager=manager)
stop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((520, 400), (200, 100)), text='STOP', manager=manager)
up_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 250), (200, 40)), text='UP', manager=manager)
down_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 310), (200, 40)), text='DOWN', manager=manager)
menu = pygame_gui.elements.UIDropDownMenu(options_list={"n/a", "A", "B"},
                                          starting_option=medication,
                                          relative_rect=pygame.Rect((300, 400), (200, 100)),
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

while not done:
    time_delta = clock.tick(60)/1000.0
    manager.update(time_delta)
    clock.tick(FPS); #set framerate

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
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            print("Selected option:", event.text)
            new_medication = event.text
            # hide/reset dropdown options
            dropdown_cover.fill(pygame.Color("#ffffff"))
            window_surface.blit(dropdown_cover, (300, 500))

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