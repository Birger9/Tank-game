"""
This files defines all the different maps and the map class
"""

import images
import pygame
import os

main_dir = os.path.split(os.path.abspath(__file__))[0] + "//maps//" #The directory to the saved maps, in folder maps
map_list = {} #All maps will be saved here

class Map:
  """ An instance of Map is a blueprint for how the game map will look. """
  def __init__(self,  width,  height,  boxes,  start_positions, flag_position):
    """ Takes as argument the size of the map (width, height), an array with the boxes type,
        the start position of tanks (start_positions) and the position of the flag (flag_position).
    """
    self.width              = width
    self.height             = height
    self.boxes              = boxes
    self.start_positions    = start_positions
    self.flag_position      = flag_position

  def rect(self):
    return pygame.Rect(0, 0, images.TILE_SIZE*self.width,  images.TILE_SIZE*self.height)

  def boxAt(self, x, y):
    """ Return the type of the box at coordinates (x, y). """
    return self.boxes[y][x]

def get_map(path, map_name):
    """Creates map objects from a folder containing text files"""
    map_data = [] #To be filled with map information
    with open(path) as file: #Opens the map with the name file
        for line in file:
            map_data.append(line)
    map_info_list = search_through_textlist(map_data, 0) #map_info_list contains all the information about a map
    map_list[map_name] = Map(map_info_list[0], map_info_list[1], map_info_list[2], map_info_list[3],map_info_list[4][0]) #Saves the maps from textfiles into a dictionary

def search_through_textlist(data, sep_index):
    """Retrieves values from a list and returns a list containing map information in right format"""
    map_list = [] #All the map information is stored here
    sep_index = 0 #To keep track of where you are in the text document. For example sep_index = 2 means that the box type values is being converted to the right format
    map_row = []
    for line in data: #Goes through every line in the text document
        temp_list = []
        if sep_index < 2:
            map_list.append(int(line)) #The width and height from the textdocument is made to ints from a string
            sep_index += 1
        elif line[0] == "*": #* used to seperate arguments to map object
            sep_index += 1
            map_list.append(map_row)
            map_row = []
        elif sep_index >= 2:
            separated_list = line.split(",") #map values without ,
            if sep_index == 2: #Used to separete ints from flotes in map*.txt
                for element in separated_list:
                    elem = int(element)
                    temp_list.append(elem) #List filled with only ints
                map_row.append(temp_list)
            if sep_index > 2:
                for element in separated_list:
                    elem = float(element)
                    temp_list.append(elem) #List filled with only floats
                map_row.append(temp_list)
    return map_list


def load_maps():
    """Loads all map files from the maps directory."""
    filenames = os.listdir(main_dir) #List of all maps names
    for filename in filenames:
        name = filename.split(".")[0] #Cuts out .txt from the name of the map
        try:
            get_map(main_dir + "//" + filename, name) #sends in path to map and name of map to function
        except pygame.error:
            raise SystemExit('Could not load mapfile "%s" %s'%(filename, pygame.get_error()))

def load_map(name):
    """Loads given map file from the maps directory."""
    try:
        get_map(main_dir + "//" + name + ".txt", name)
    except pygame.error:
        raise SystemExit('Could not load mapfile "%s" %s'%(filename, pygame.get_error()))
