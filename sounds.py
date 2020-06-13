import pygame
import os

main_dir = os.path.split(os.path.abspath(__file__))[0]#Path to where the sound fiels are saved

def load_sound(file):
    """ Load a sound from the data directory. """
    file = os.path.join(main_dir, 'data', file)
    try:
            sound = pygame.mixer.Sound(file)
    except pygame.error:
        raise SystemExit('Could not load sound "%s" %s'%(file, pygame.get_error()))
    return sound

#-- Initialise the game music
game_music = load_sound("background_music.wav")

#-- Initialise the menu music
menu_music = load_sound("menu_music.wav")

#-- Initialise the bullet sound
bullet_sound = load_sound("bullet.wav")

#-- Initialise the box break sound
box_break_sound = load_sound("box_break.wav")

#-- Initialise the box break sound
tank_explode_sound = load_sound("tank_explosion.wav")

#-- Initialise the background music
#music = load_sound("music.mp3.mp3")

def play_game_music():
    game_music.set_volume(0.7)#1.0 is standard value of volume
    game_music.play(-1)

def play_menu_music():
    menu_music.set_volume(0.2)#1.0 is standard value of volume
    menu_music.play(-1)

def stop_menu_music():
    menu_music.stop()

def play_tank_shot():
    bullet_sound.play()

def play_box_break():
    box_break_sound.play()

def play_tank_explosion():
    tank_explode_sound.play()
