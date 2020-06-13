import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import math
import sys

pygame.init()#initializes all imported pygame modules
pygame.display.set_mode()
pygame.display.set_caption("Capture The Flag")

from ai import *
import boxmodels
import gameobjects
import ui
import maps


#Default value so commandlines are not required
gamemode = "--singleplayer"
chosen_map = "map0"
status = "menu"
menu = True
running = True

finished_game = False


if len(sys.argv) > 1:
    menu = False
    gamemode = sys.argv[1]
    chosen_map = sys.argv[2]
    sounds.play_game_music()

screen_width=800
screen_height=600
clock = pygame.time.Clock()
FRAMERATE = 50
screen = pygame.display.set_mode((screen_width, screen_height)) #Sets the resolution of screen
maps.load_maps() #Loads all saved maps
current_map = maps.map_list[chosen_map] #Sets current map
background = pygame.Surface(screen.get_size())


space = pymunk.Space()
space.gravity = (0.0,  0.0)


# Colors
white=(255, 255, 255)
gray =(200, 200, 200)
black=(0, 0, 0)
green=(9,122,0)

font_20 = pygame.font.SysFont(None,20) #Used in menus
font_30 = pygame.font.SysFont(None,30)
font_40 = pygame.font.SysFont(None,40)

game_objects_list   = [] #Stores boxes, tanks, flag, bullets
tanks_list          = [] #Stores tanks
ai_list             = [] #Stores tanks controlled by A.I.
player_list         = [] #Stores human-controlled tanks
scoreboard_order = [] #Used to sort the scoreboard
human_players = []
selected_players = [1,0,0,0,0,0] #Default players 1 = Human, 0 = A.I
winning_score = 300 #Amount of score required to win
scoreboard_width = 200 #Add scoreboard size

if gamemode == "--hot-multiplayer":
    selected_players[1] = 1


new_controls = {"id": None, "shoot": None, "up": None, "down": None, "left": None, "right": None}
controls_status = None #Next input key
controls_next = {"up": "down", "down": "left", "left": "right", "right": "shoot", "shoot": None} #When setting controls in menu


menu_buttons = {}
#Stores the buttons in dictionary in a list
menu_buttons["menu"] = [
ui.Button("select_map", screen_width / 2 - 100, screen_height - 210, 200, 50, font_20, "New Game", black, white, gray),
ui.Button("editor", screen_width / 2 - 100, screen_height - 155, 200, 50, font_20, "Level Editor", black, white, gray),
ui.Button("quit", screen_width / 2 - 100, screen_height - 100, 200, 50, font_20, "Quit", black, white, gray)
]

#Creates the appearence of buttons in level editor
menu_buttons["level_editor"] = [
ui.Text_entry("map_name", 70, 260, 100, font_30, chosen_map, False),
ui.Text_entry("map_x_size", 70, 290, 100, font_30, "12", True),
ui.Text_entry("map_y_size", 70, 320, 100, font_30, "12", True),
ui.Button("create", screen_width / 2 - 305, screen_height - 55, 200, 50, font_20, "New Map", black, white, gray),
ui.Button("edit", screen_width / 2 - 100, screen_height - 55, 200, 50, font_20, "Edit", black, white, gray),
ui.Button("back_to_main", screen_width / 2 + 105, screen_height - 55, 200, 50, font_20, "Back", black, white, gray),
]

#Creates the appearence of buttons in map selection menu
menu_buttons["map_selection"] = [
ui.Button("start_game", screen_width / 2 - 205, screen_height - 55, 200, 50, font_20, "Start", black, white, gray),
ui.Button("back_to_main", screen_width / 2 + 5, screen_height - 55, 200, 50, font_20, "Back", black, white, gray),
]


start_y = 220
for map in maps.map_list: #map_list is the list containing  all of the maps
    but = ui.Button("map", screen_width / 2 - 75, start_y, 150, 30, font_20, map, black, white, gray, map)
    menu_buttons["map_selection"].append(but)
    menu_buttons["level_editor"].append(but)
    start_y = start_y + 35

player_start_y = 220
for i in range(0, 6):
    text = "AI "
    if selected_players[i] == 1:
        text = "Player "
    but = ui.Button("player", 50, player_start_y, 150, 30, font_20, text + str(i + 1), black, white, gray, i)
    set_control_but = ui.Button("set", 205, player_start_y, 100, 30, font_20, "Set Controls", black, white, gray, i)

    menu_buttons["map_selection"].append(but)
    menu_buttons["map_selection"].append(set_control_but)
    player_start_y = player_start_y + 35



player_controls = [
{"shoot": K_RETURN, "up": K_UP, "down": K_DOWN, "left": K_LEFT, "right": K_RIGHT},
{"shoot": K_SPACE, "up": K_w, "down": K_s, "left": K_a, "right": K_d},
{"shoot": K_SPACE, "up": K_w, "down": K_s, "left": K_a, "right": K_d},
{"shoot": K_SPACE, "up": K_w, "down": K_s, "left": K_a, "right": K_d},
{"shoot": K_SPACE, "up": K_w, "down": K_s, "left": K_a, "right": K_d},
{"shoot": K_SPACE, "up": K_w, "down": K_s, "left": K_a, "right": K_d}
]
