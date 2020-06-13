import pygame
import pymunk
from pygame.locals import *
from pygame.color import *
import math
import sys


pygame.init() #initializes all imported pygame modules
pygame.display.set_mode()
pygame.display.set_caption("Capture The Flag - Level Editor")

import gameobjects
import ui
import images

font_20 = pygame.font.SysFont(None,20)

gray =(200, 200, 200)
white=(255, 255, 255)
black=(0, 0, 0)

placeable_objects = []
editor_object_list = [
{"sprite": images.grass, "boxtype_id": None, "type": "box"},
{"sprite": images.rockbox, "boxtype_id": 1, "type": "box"},
{"sprite": images.woodbox, "boxtype_id": 2, "type": "box"},
{"sprite": images.metalbox, "boxtype_id": 3, "type": "box"},
{"sprite": images.flag, "type": "flag"},
{"sprite": images.bases[0], "base_id": 0, "type": "base"},
{"sprite": images.bases[1], "base_id": 1, "type": "base"},
{"sprite": images.bases[2], "base_id": 2, "type": "base"},
{"sprite": images.bases[3], "base_id": 3, "type": "base"},
{"sprite": images.bases[4], "base_id": 4, "type": "base"},
{"sprite": images.bases[5], "base_id": 5, "type": "base"},
]

def map_editor_object_menu(map_pixel_width, map_pixel_height):
    """Adds a placeable object to the object selection menu"""
    max_selection_height = (map_pixel_height/images.TILE_SIZE) - 2 #remove one at top and one at bottom
    selection_menu_width = 4 #Initial width tiles for selection menu
    object_button_index = 0 #Current objects index from object_data list
    current_menu_button_height = 0 #Current added tiles in y-column
    current_menu_button_width = 0 #Current added tiles in x-row
    for object in editor_object_list:
        object_x_pos = images.TILE_SIZE * current_menu_button_width
        object_y_pos = images.TILE_SIZE * (current_menu_button_height+1)
        button = ui.Sprite_button("placeable", map_pixel_width + object_x_pos, object_y_pos, images.TILE_SIZE, images.TILE_SIZE, object["sprite"], object_button_index)
        placeable_objects.append(button)
        object_button_index = object_button_index + 1
        current_menu_button_height = current_menu_button_height + 1
        if current_menu_button_height == max_selection_height: #When we reach max y add 1 to x instead, then reset y
            current_menu_button_height = 0
            current_menu_button_width = current_menu_button_width + 1
    return images.TILE_SIZE * selection_menu_width

def call_editor(width, height, map_name, map = None):
    """Initializes a map with given width and height, if map argument is provided
    it will modify given map"""

    import boxmodels
    import maps

    #-- Initialise the display
    pygame.display.set_caption("Capture The Flag - Level Editor")

    #-- Initialise the physics engine
    space = pymunk.Space()
    space.gravity = (0.0,  0.0)

    box_list = []
    flag_list = []
    base_list = []

    if map != None: #Generate objects for given map (if given)
        #Initialize the boxes for the given map
        for x in range(0, map.width):
            for y in range(0,  map.height):
                box_type  = map.boxAt(x, y)
                box_model = boxmodels.get_model(box_type)

                if box_model != None:
                    box = gameobjects.Box(x + 0.5, y + 0.5, box_model, space, 2)
                    box_list.append(box)

        #Initalize the bases
        for i in range(0, len(map.start_positions)):
            #-- Bases --#
            pos = map.start_positions[i]
            base = gameobjects.GameVisibleObject(pos[0], pos[1], images.bases[i])
            base_list.append(base)

        #Creates the flag
        flag = gameobjects.Flag(map.flag_position[0], map.flag_position[1])
        flag_list.append(flag)

    #Values for textfile
    box_value_list = []
    start_pos_value_list = []
    flag_pos_value_list = []

    object_selected = 0 #object selected from object selector
    button_last_selected = None #Button for last selected object from selection menu for drawing
    mouse_clicked = False #When mouse is clicked

    screen_active = True

    chosen_screen_width = width * images.TILE_SIZE
    chosen_screen_height = height * images.TILE_SIZE


    placeable_objects.clear() #Empty the list of buttons before adding new
    extra_width = map_editor_object_menu(chosen_screen_width, chosen_screen_height) # Initializes all buttons for the object selection menu and returns the extra width tiles we require
    finish_button = ui.Button("finish", chosen_screen_width, chosen_screen_height - images.TILE_SIZE, extra_width, images.TILE_SIZE, font_20, "Finish", black, white, gray)

    screen = pygame.display.set_mode((chosen_screen_width + extra_width, chosen_screen_height))

    background = pygame.Surface(screen.get_size())

    #Copy the grass tile all over the level area
    for x in range(0, width):
        for y in range(0, height):
            #The call to the function "blit" will copy the image
            #contained in "images.grass" into the "background"
            #image at the coordinates given as the second argument
            background.blit(images.grass,  (x*images.TILE_SIZE, y*images.TILE_SIZE))


    def add_object_on_map(x, y, object_list_index):
        """Adds object of input id (checks object_data for object) at x,y coordinates"""
        object_dict = editor_object_list[object_list_index] #dict for given list index
        remove_object_location(x, y)
        if object_dict["type"] == "box":
            if object_dict["boxtype_id"] != None:
                box = gameobjects.Box(x + 0.5, y + 0.5, boxmodels.get_model(object_dict["boxtype_id"]), space, 2)
                box_list.append(box)
        elif object_dict["type"] == "flag":
            add_flag_on_map(x + 0.5, y + 0.5)
        elif object_dict["type"] == "base":
            add_base_on_map(x + 0.5, y + 0.5, object_dict["base_id"])

    def remove_object_location(x_pos, y_pos):
        """Removes object at given coordinates"""
        for box in box_list: #Loops through box_list too see if the x- and y-position the user clicked on matches a box
            if box.x == (x_pos + 0.5) and box.y == (y_pos + 0.5):
                box_list.remove(box)
        for flag in flag_list: #Loops through box_list too see if the x- and y-position the user clicked on matches a box
            if flag.x == (x_pos + 0.5) and flag.y == (y_pos + 0.5):
                flag_list.remove(flag)
        for base in base_list:
            if base.x == (x_pos + 0.5) and base.y == (y_pos + 0.5):
                base_list.remove(base)
        return True #The user didnt click on an existing box

    def add_flag_on_map(x_pos, y_pos):
        """Adds a flag on the map or moves an already existing one to a new location"""
        for box in box_list:
            if box.x == (x_pos) and box.y == (y_pos): #If the user tries to place the flag on a box, return False
                return False
        if flag_list == []:
            flag = gameobjects.Flag(x_pos, y_pos)
            flag_list.append(flag)
        else: #If the flag_list is not empty, then remove the existing flag from flag_list and a new flag on a new location
            flag_list.pop(0)
            flag = gameobjects.Flag(x_pos, y_pos)
            flag_list.append(flag)

    def add_base_on_map(x_pos, y_pos, base_num):
        """Adds a base on the map"""
        for base in base_list:
            if base.sprite == images.bases[base_num]:
                base_list.remove(base)
        base = gameobjects.GameVisibleObject(x_posfinished, y_pos, images.bases[base_num])
        base_list.append(base)

    def retrieve_boxtype(x_pos, y_pos):
        """Retrieves a box object's boxtype at a specific x- and y-value"""
        for box in box_list:
            if box.x == (x_pos + 0.5) and box.y == (y_pos + 0.5):
                return box.boxmodel.boxtype
        return 0


    def retrieve_startposition(x_pos, y_pos, max_y):
        """Retrieves a base object's x-position, y-position, oritentation and True if found at a specific x- and y-value"""
        for base in base_list:
            if base.x == (x_pos + 0.5) and base.y == (y_pos + 0.5):
                if base.y > (max_y / 2):
                    return base.x, base.y, 180, True
                else:
                    return base.x, base.y, 0, True
        return 0,0,0, False


    def retrieve_flagposition(x_pos, y_pos):
        """Retrieves a flag object's x-position, y-position and True if found at a specific x- and y-value"""
        for flag in flag_list:
            if flag.start_x == (x_pos + 0.5) and flag.start_y == (y_pos + 0.5):
                return flag.start_x, flag.start_y, True
        return 0,0,False


    def convert_map_to_txt(the_list):
        """Converts a list containing map informatfinishedion to a string, that will later be saved in a txt file, to right format"""
        formatted_str = ""
        for info in the_list: #Goes through each list/row in the_list
            row = str(info).strip("[]") #[0,1,0,0,0,0,0,1,0] becomes 0,1,0,0,0,0,0,1,
            if info == "*":
                formatted_str = formatted_str + row
            else:
                formatted_str = formatted_str + row + "\n"
        formatted_str = formatted_str.replace(" ","") #Removes all spaces in the strin
        return formatted_str #Returns the formatted string

    finished = False
    while screen_active:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                screen_active = False
            if event.type == pygame.MOUSEBUTTONUP:
                x = math.floor(pygame.mouse.get_pos()[0] / images.TILE_SIZE) #Rounds down the x-pos of a tile the user pressed on
                y = math.floor(pygame.mouse.get_pos()[1] / images.TILE_SIZE) #Rounds down the y-pos of a tile the user pressed on

                mouse_clicked = True
                if x < width and y < height: #limit to the map size
                    add_object_on_map(x, y, object_selected)

        placeable = font_20.render("Objects", True, white)
        text_width, text_height = font_20.size("Placeable")
        screen.blit(placeable, (chosen_screen_width + text_width, images.TILE_SIZE/4))

        mouse_click = pygame.mouse.get_pressed() #What button on mouse is pressed

        if button_last_selected != None: #If an object from selection menu is selected, draw a white background
            pygame.draw.rect(screen, (255, 255, 255), (button_last_selected.x, button_last_selected.y, button_last_selected.w, button_last_selected.h)) #Border around button


        for button in placeable_objects: #placeable_objects contains all selectable objects from selection menu
            button.draw(screen)
            if button.hovering() and mouse_clicked:
                object_selected = button.val #Set selected object to last clicked button object from selection menu
                button_last_selected = button #sets last clicked button

        finish_button.draw(screen)
        if finish_button.hovering() and mouse_clicked and len(base_list) > 0 and len(flag_list) > 0:
            #If finish button is clicked, save map and exit editor
            for y in range(height):
                map_row = []
                for x in range(width):
                    map_row.append(retrieve_boxtype(x, y)) #Add box type id in list
                box_value_list.append(map_row)
                if y == height - 1: #Reached the final row of the map
                    box_value_list.append("*")

            for y in range(height):
                map_row = []
                for x in range(width):
                    x_value, y_value, ori, bool = retrieve_startposition(x, y, height)
                    flag_x_value, flag_y_value, boolean = retrieve_flagposition(x, y)
                    if bool: #bool True if function retrieve_startposition found a base at inputted x and y-value
                        map_row = [x_value, y_value, ori]
                        start_pos_value_list.append(map_row)
                    if boolean: #boolean True if function retrieve_startposition found the flag at inputted x and y-value
                        flag_pos_value_list = [flag_x_value, flag_y_value]
                if y == height - 1: #Reached the final row of the map
                    start_pos_value_list.append("*")
                    flag_pos_value_list.append("*")
            maps.map_list[map_name] = maps.Map(width, height, box_value_list, start_pos_value_list, flag_pos_value_list) #Creates a map object
            str_boxes = convert_map_to_txt(box_value_list) #box info in string format
            str_bases = convert_map_to_txt(start_pos_value_list) #bases info in string format
            str_flag = str(flag_pos_value_list[0]) + "," + str(flag_pos_value_list[1]) + "\n*" #Flag info in string format
            mega_str = str(width) + "\n" + str(height) + "\n" + str_boxes + "\n" + str_bases + "\n" + str_flag + "\n" #The whole map info in string format

            f = open("maps/" + map_name + ".txt",'w') #Creates a txt document with the chosen map name
            f.write(mega_str) #Writes the map info into the txt document
            f.close()
            finished = True
            screen_active = False #The editor closes

        mouse_clicked = False
        pygame.display.update()
        #-- Update the screen --#
        screen.blit(background, (0, 0))
        for obj in box_list:
            obj.update_screen(screen)
        for obj in flag_list:
            obj.update_screen(screen)
        for obj in base_list:
            obj.update_screen(screen)
    return finished

if __name__ == '__main__':
    width, height = 1, 1
    if len(sys.argv) > 2:
        width = int(sys.argv[1]) #Input width
        height = int(sys.argv[2]) #Input height
        map_name = sys.argv[3] #Input map name
    call_editor(width, height, map_name)
