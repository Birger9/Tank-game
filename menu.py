import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import math
import sys

import images
import maps
import sounds
import ui
import ctf_editor
from globals import *


def add_to_maps(map):
    """
    Adds maps to the list if the map is newly created, if modified it updates the values
    """
    newbut = True
    for but in menu_buttons["level_editor"]: #Checks if map exists
        if isinstance(but, ui.Button) and but.val == map:
            newbut = False
    if newbut == True:
        start_y = 220 + (len(maps.map_list)-1) * 35
        but = ui.Button("map", screen_width / 2 - 75, start_y, 150, 30, font_20, map, black, white, gray, map)
        menu_buttons["map_selection"].append(but)
        menu_buttons["level_editor"].append(but)
    maps.load_map(map)

mouse_clicked = False
sounds.play_menu_music()
text_entry_focus = None
while menu:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            quit()
        if text_entry_focus != None and text_entry_focus.focus:
            if event.type == pygame.MOUSEBUTTONDOWN and not text_entry_focus.hovering():
                text_entry_focus.focus = False
                text_entry_focus = None
            elif event.type == KEYDOWN:
                text_entry_focus.update_text(pygame.key.name(event.key))

        if event.type == KEYDOWN and new_controls["id"] != None: #When setting new controls
            if new_controls[controls_status] == None:
                new_controls[controls_status] = event.key #Pressed button is saved in new_controls
                controls_status = controls_next[controls_status] #Next button to be assigned
                if controls_status == None: #No next key -> ends
                    player_controls[new_controls["id"]] = new_controls #Sets the chosen controls to the selected player
                    new_controls = {"id": None, "shoot": None, "up": None, "down": None, "left": None, "right": None} #Reset the temporary storage
        elif event.type == pygame.MOUSEBUTTONUP: #When the user has released the left click
            mouse_clicked = True

    background = pygame.transform.scale(images.menu_background, (screen_width, screen_height+20)) #Rescales the background to fit screen
    screen.blit(background, (0, 0)) #Blits background first

    mouse_click = pygame.mouse.get_pressed() #What button on mouse is pressed
    if status == "menu":

        screen.blit(images.title, (screen_width/2-210, -50)) #Capture the flag logo

        for button in menu_buttons["menu"]: #menu_buttons contains all the buttons for the different menu screens
            button.draw(screen)
            if button.hovering() and mouse_clicked:
                id = button.id
                if id == "select_map": #Depending on id -> different menu screens
                    status = "map_selector"
                elif id == "editor":
                    status = "editor"
                elif id == "quit":
                    menu = False
                    running = False
    elif status == "map_selector" or status == "editor":
        screen.blit(images.title_small, (screen_width/2-105, 0)) #Title small
        if status == "map_selector":
            for button in menu_buttons["map_selection"]: #menu_buttons contains all the buttons for the different menu screens
                if button.id == "player": #If the user presses player buttons
                    if button.val < len(current_map.start_positions): #For example if 4 players, draw four player buttons
                        button.draw(screen)

                        id_surf = font_20.render(str(button.val + 1), True, white)
                        id_surf_rect = id_surf.get_rect(center = (button.x - 10, button.y + 15))
                        screen.blit(id_surf, id_surf_rect)
                elif button.id == "set": #If the user presses set controls button
                    if selected_players[button.val] == 1 and button.val < len(current_map.start_positions): #Shows only set controls on a player button, not on AI player
                        button.draw(screen)
                else:
                    button.draw(screen)
                if button.hovering() and mouse_clicked: #If user presses a button
                    if button.id == "start_game":
                        menu = False
                    elif button.id == "back_to_main":
                        new_controls = {"id": None, "shoot": None, "up": None, "down": None, "left": None, "right": None}
                        controls_status = None
                        status = "menu"
                    elif button.id == "map":
                        current_map = maps.map_list[button.val] #button.val is the map the user clicked on
                        chosen_map = button.val
                    elif button.id == "set" and selected_players[button.val] == 1: #Byt set till set_controls, fixa funktion till selected_players
                        controls_status = "up"
                        new_controls["id"] = button.val #player id
                    elif button.id == "player" and button.val < len(current_map.start_positions):#
                        if selected_players[button.val] == 1: #If clicked on a player button, set it to a ai
                            selected_players[button.val] = 0
                            button.text = "AI " + str(button.val + 1)
                        else:
                            selected_players[button.val] = 1 #Turns an ai to a player
                            button.text = "Player " + str(button.val + 1)
            if new_controls["id"] != None: #Shows the visual of the set_controls for example down
                pygame.draw.rect(screen, black, (screen_width / 2 - 100, screen_height / 2 - 25, 200, 50))
                pygame.draw.rect(screen, gray, (screen_width / 2 - 99, screen_height / 2 - 24, 198, 48))

                control_input = font_20.render("Select key for: " + controls_status, True, black)
                control_input_rect = control_input.get_rect(center = (screen_width / 2, screen_height / 2))#Centers the text

                screen.blit(control_input, control_input_rect)
        elif status == "editor":
            for button in menu_buttons["level_editor"]:
                button.draw(screen)
                if button.hovering() and mouse_clicked:
                    if button.id == "create":
                        name, x, y = "", 3, 3
                        for element in menu_buttons["level_editor"]: #Loop through all elements to find the text entry elements to set mapname and map size
                            if element.id == "map_name":
                                name = element.text
                            elif element.id == "map_x_size":
                                x = int(element.text)
                            elif element.id == "map_y_size":
                                y = int(element.text)
                        finished = ctf_editor.call_editor(x, y, name)
                        screen = pygame.display.set_mode((screen_width, screen_height))
                        if finished:
                            add_to_maps(name)
                            current_map = maps.map_list[name]
                    elif button.id == "edit":
                        ctf_editor.call_editor(current_map.width,current_map.height,chosen_map, current_map)
                        screen = pygame.display.set_mode((screen_width, screen_height))
                        add_to_maps(chosen_map)
                        current_map = maps.map_list[chosen_map]
                    elif button.id == "map":
                        current_map = maps.map_list[button.val]
                        chosen_map = button.val
                        for element in menu_buttons["level_editor"]: #Loop through all elements to find the text entry elements to set mapname and map size
                            if element.id == "map_name":
                                element.text = chosen_map
                            elif element.id == "map_x_size":
                                element.text = str(current_map.width)
                            elif element.id == "map_y_size":
                                element.text = str(current_map.height)
                    elif button.id == "back_to_main":
                        status = "menu"
                    elif button.focus != None:
                        button.focus = True
                        text_entry_focus = button

            map_name = font_40.render("Map Options", True, white)
            screen.blit(map_name, (30, 223))

            map_name = font_30.render("Name: ", True, white)
            screen.blit(map_name, (5, 263))

            x_text = font_30.render("X: ", True, white)
            screen.blit(x_text, (48, 295))

            y_text = font_30.render("Y: ", True, white)
            screen.blit(y_text, (48, 324))

        w_req, h_req = current_map.width * images.MINIMAP_TILE_SIZE, current_map.height * images.MINIMAP_TILE_SIZE

        mapsize_surf = font_40.render(str(current_map.width) + "x" + str(current_map.height), True, black) #Render the map size as text AxB
        map_start_x, map_start_y = screen_width / 1.25 - w_req / 2, screen_height / 2 - h_req / 2

        mapsize_surf_rect = mapsize_surf.get_rect(center = (screen_width / 1.25, map_start_y - 15))

        screen.blit(mapsize_surf, mapsize_surf_rect) #Width and height is shown to the user for example 9x9

        pygame.draw.rect(screen, black, (map_start_x-1, map_start_y-1, w_req+2, h_req+2))
        for x in range(0, current_map.width): #Creates the minimap that is shown to the user
            tile_x = (images.MINIMAP_TILE_SIZE*x)
            for y in range(0,  current_map.height):
                tile_y = (images.MINIMAP_TILE_SIZE*y)
                #Get the type of boxes
                box_type  = current_map.boxAt(x, y)

                tile_sprite = images.grass_small
                if(box_type == 1):
                    tile_sprite = images.rockbox_small
                elif(box_type == 2):
                    tile_sprite = images.woodbox_small
                elif(box_type == 3):
                    tile_sprite = images.metalbox_small
                screen.blit(tile_sprite, (map_start_x + tile_x, map_start_y + tile_y)) #Blits the boxes on the minimap

        screen.blit(images.flag_small, (map_start_x + (current_map.flag_position[0]-0.5)*images.MINIMAP_TILE_SIZE, map_start_y + (current_map.flag_position[1]-0.5)*images.MINIMAP_TILE_SIZE))#Blits the flag on the minimap

        for i in range(0, len(current_map.start_positions)):
            pos = current_map.start_positions[i]

            start_surf = font_20.render(str(i+1), True, black)

            screen.blit(start_surf, (map_start_x + (pos[0]-0.25)*images.MINIMAP_TILE_SIZE, map_start_y + (pos[1]-0.4)*images.MINIMAP_TILE_SIZE)) #Blits the bases on the minimap

    mouse_clicked = False
    pygame.display.update()
    clock.tick(FRAMERATE)
