"""
This file loads in all the images used by the game and caches them inside variables
"""

import pygame
import os

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(file):
    """ Load an image from the data directory. """
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert_alpha()

def load_animation():
    ''' Creates explosion animation based on 9 png images '''
    animation_list = []
    for image in range(9):
        file_name = 'regularExplosion0{}.png'. format(image)
        explosion_img = pygame.image.load(os.path.join(main_dir, 'data', 'Explosions', file_name)) #Creates a surface object for explosion
        explosion_img.set_colorkey((0, 0, 0)) #Makes black transparent on the explosion surface
        explosion_img = pygame.transform.scale(explosion_img, (40, 40)) #Picture in explosion same size as tile
        animation_list.append(explosion_img)
    return animation_list


TILE_SIZE = 40 # Define the default size of tiles
MINIMAP_TILE_SIZE = 15

explosion = load_animation() #Returns a list of pictures in animation

grass     = load_image('grass.png') # Image of a grass tile
grass_small = pygame.transform.scale(grass, (MINIMAP_TILE_SIZE, MINIMAP_TILE_SIZE))

rockbox   = load_image('rockbox.png') # Image of a rock box (wall)
rockbox_small = pygame.transform.scale(rockbox, (MINIMAP_TILE_SIZE, MINIMAP_TILE_SIZE))

metalbox  = load_image('metalbox.png') # Image of a metal box
metalbox_small = pygame.transform.scale(metalbox, (MINIMAP_TILE_SIZE, MINIMAP_TILE_SIZE))

woodbox   = load_image('woodbox.png') # Image of a wood box
woodbox_small = pygame.transform.scale(woodbox, (MINIMAP_TILE_SIZE, MINIMAP_TILE_SIZE))

flag      = load_image('flag.png') # Image of flag
flag_small = pygame.transform.scale(flag, (MINIMAP_TILE_SIZE, MINIMAP_TILE_SIZE))

title      = load_image('title.png')
title_small = pygame.transform.scale(title, (210, 210))

menu_background      = load_image('menu_background.png')

bullet = load_image('bullet.png')
bullet = pygame.transform.scale(bullet, (10, 10))
bullet = pygame.transform.rotate(bullet, -90)

# List of image of tanks of different colors
tanks     = [load_image('tank_orange.png'), load_image('tank_blue.png'), load_image('tank_white.png'),
             load_image('tank_yellow.png'), load_image('tank_red.png'),  load_image('tank_gray.png')]

# List of image of bases corresponding to the color of each tank
bases     = [load_image('base_orange.png'), load_image('base_blue.png'), load_image('base_white.png'),
             load_image('base_yellow.png'), load_image('base_red.png'),  load_image('base_gray.png')]
