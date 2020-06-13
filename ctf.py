
"""
This file initialise the game by loading in all the different modules, it also
manages the game logic and events in the game loop.
"""

import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import math
import sys


#-- Import from the ctf framework
from globals import *
import ctf_editor
from menu import *


def add_score_player(player_id, point_amount):
    """
    Adds given points to given player
    """
    current_score = player_list[player_id]["score"] #Current score
    player_list[player_id]["score"] = current_score + point_amount #Add given points to players score

    def sort_by_score(index): #Inner function for sorting
        return player_list[index]["score"] #Sort by score
    scoreboard_order.sort(key=sort_by_score, reverse=True) #Reverse makes the board in right order
    print("Player: " + str(player_id + 1) + " has scored")
    print("Current score:")
    for tank in tanks_list:
        print("Player " + str(tank.id + 1) + ": " + str(player_list[tank.id]["score"]))
    check_winning_condition(player_id) #Inputs player that recently scored


def check_winning_condition(player_id):
    """Checks if given player has enough score to win"""
    global finished_game
    if player_list[player_id]["score"] >= winning_score:
        finished_game = player_list[player_id]
        print("Player " + str(player_id + 1) + " has won the game.")
        for tank in tanks_list:
            tank.stop_moving()
            tank.stop_turning()


def check_tank_flag_status(tanks_list, sp_tank, flag):
    """
        Handles tanks interaction with flag and updates the score
    """
    for tank in tanks_list:
        tank.try_grab_flag(flag)

        if sp_tank and sp_tank.flag != None: #If singleplayer tanks grabs flag make fog
            sp_tank.fog_of_war = True
        if tank.has_scored(): #When tank returnes to base with flag
            if sp_tank:
                sp_tank.fog_of_war = False
            flag.respawn()
            add_score_player(tank.id, 100) #Add 100 score to player


def create_static_borders(space):
    """
        Create invisible walls so that tanks cant drive out of screen
    """
    static_body = space.static_body
    static_lines = [pymunk.Segment(static_body, (0, 0), (current_map.width, 0), 0),
                    pymunk.Segment(static_body, (current_map.width, 0), (current_map.width, current_map.height), 0),
                    pymunk.Segment(static_body, (current_map.width, current_map.height), (0, current_map.height), 0),
                    pymunk.Segment(static_body, (0, current_map.height), (0, 0), 0)]
    space.add(static_lines)


def create_background(current_map, background):
    """
        Creates a background filled with grass tiles
    """
    for x in range(0, current_map.width):
        for y in range(0,  current_map.height):
            background.blit(images.grass,  (x*images.TILE_SIZE, y*images.TILE_SIZE))


def remove_object(shape):
    """Removes given object if it exists"""
    object = shape.parent
    if object in game_objects_list:
        space.remove(shape, shape.body)
        game_objects_list.remove(object)


def collision_bullet_tank(arb, space, data):
    """
    Collision handler for bullet and tank
    """
    bullet = arb.shapes[0].parent #.parent returnar bullet objektet
    tank = arb.shapes[1].parent
    id = tank.id
    if bullet.shot_by != arb.shapes[1].parent: #So the tank doesnt shot itself, the bullet is created in the middle of the tank
        if tank.respawn_delay < 1 and tank.check_tank_hp():
            explosion = gameobjects.Explosion((tank.body.position - 0.5) * images.TILE_SIZE)
            game_objects_list.append(explosion)
            if tank.flag: #If the tank killed has the flag
                flag.is_on_tank = False
                tank.flag = None
                add_score_player(bullet.shot_by.id, 10)
            else:
                add_score_player(bullet.shot_by.id, 5)

            sounds.play_tank_explosion()

            pos = current_map.start_positions[id]
            respawned_tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[id], space, id, 2) #The tank that was killed
            player_list[id]["tank"] = respawned_tank

            game_objects_list.append(respawned_tank)
            tanks_list[id] = respawned_tank

            if player_list[id]["ai"] != None: #if the killed tank is an AI
                player_list[id]["ai"].update_on_death(respawned_tank)

            respawned_tank.respawn_protection() #The killed tank gets 4 seconds seconds res protection
            remove_object(arb.shapes[1])
        remove_object(arb.shapes[0])
    return True


def collision_bullet_box(arb, space, data):
    ''' Collision handler for bullet and box '''
    bullet = arb.shapes[0].parent #.parent returnar bullet objektet
    box = arb.shapes[1].parent
    destructable = box.boxmodel.destructable #Either True or False
    if destructable and box.check_box_hp(): #True if the box is destructable and the box has less than 1 hp
        explosion = gameobjects.Explosion((box.body.position - 0.5) * images.TILE_SIZE)
        game_objects_list.append(explosion)
        sounds.play_box_break()
        add_score_player(bullet.shot_by.id, 1)
        remove_object(arb.shapes[1])
    remove_object(arb.shapes[0])
    return True


def collision_bullet_bullet(arb, space, data):
    """Collision handler for bullet and bullet"""
    remove_object(arb.shapes[0])
    remove_object(arb.shapes[1])
    return False


def collision_bullet_other(arb, space, data):
    """Collision handler for bullet and other objects"""
    remove_object(arb.shapes[0])
    return True


def initialize_collision_handlers(space):
    """
        Defines how game handles collisions with bullets and other game objects
    """
    bullet_tank_handler = space.add_collision_handler(1, 2) #1 is bullet and 2 tank
    bullet_tank_handler.pre_solve = collision_bullet_tank #If False, dont calculate collision

    bullet_box_handler = space.add_collision_handler(1, 3) #1 is bullet and  3 box
    bullet_box_handler.pre_solve = collision_bullet_box #If False, dont calculate collision

    bullet_bullet_handler = space.add_collision_handler(1, 1) #1 stands for bullet
    bullet_bullet_handler.pre_solve = collision_bullet_bullet #If False, dont calculate collision

    bullet_other_handler = space.add_collision_handler(1, 0) #1 stands for bullet
    bullet_other_handler.pre_solve = collision_bullet_other #If False, dont calculate collision


def create_flag():
    """
        Spawns a flag on the map
    """
    flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
    game_objects_list.append(flag)
    return flag


def put_humanply_in_list(player_list, human_players):
    """
        Puts all human players ids in a list
    """
    for ply_data in player_list:
        if ply_data["ai"] == None:
            human_players.append(ply_data["id"])


def create_boxes_on_map(current_map):
    """
        Creates all the different boxes on the map
    """
    for x in range(0, current_map.width):
        for y in range(0,  current_map.height):
            box_type  = current_map.boxAt(x, y)
            box_model = boxmodels.get_model(box_type)

            if(box_model != None):
                box = gameobjects.Box(x + 0.5, y + 0.5, box_model, space, 2)
                game_objects_list.append(box)


def create_tanks_on_map(current_map):
    """
        Spawns that right amount of tanks on the map
    """
    for i in range(0, len(current_map.start_positions)):
        #-- Bases --#
        pos = current_map.start_positions[i]
        base = gameobjects.GameVisibleObject(pos[0], pos[1], images.bases[i])
        game_objects_list.append(base)

        #-- Tanks --#
        tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[i], space, i, 2)
        game_objects_list.append(tank)
        tanks_list.append(tank)

        #--Ai --#
        ai_agent = None
        if selected_players[i] == 0: #If not 0 it is human
            ai_agent = Ai(tanks_list[i], game_objects_list, tanks_list, space, current_map)
            ai_list.append(ai_agent)
        player_list.insert(i, {"tank": tank, "id": i, "ai": ai_agent, "score": 0}) #Add to player list data
        scoreboard_order.append(i) #Add player to scoreboard


def game_event_handler(event):
    """
        Decides how the game handles user input
    """
    global mouse_clicked
    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
        running = False
        pygame.quit()
        quit()
    if event.type == KEYDOWN and finished_game == False:
        for id in human_players: #Goes through all the human players and their chosen controls
            ply_data = player_list[id] #Ply_data is dictionary for player
            if ply_data["ai"] == None:
                controls = player_controls[ply_data["id"]] #Retrieves the controls for the player
                ply_tank = ply_data["tank"] #The player's tank
                if event.key == controls["shoot"] and ply_tank.next_shoot < 1:
                    ply_tank.next_shoot = 1000 #1 second delay of shooting
                    sounds.play_tank_shot()
                    bullet = ply_tank.shoot(space)
                    game_objects_list.append(bullet)
                if event.key == controls["up"]:
                    ply_tank.accelerate()
                if event.key == controls["down"]:
                    ply_tank.decelerate()
                if event.key == controls["left"]:
                    ply_tank.turn_left()
                if event.key == controls["right"]:
                    ply_tank.turn_right()
    if event.type == KEYUP:
        for id in human_players:
            ply_data = player_list[id]
            controls = player_controls[ply_data["id"]]
            ply_tank = ply_data["tank"]
            if event.key == controls["up"] or event.key == controls["down"]:
                ply_tank.stop_moving()
            if event.key == controls["right"] or event.key == controls["left"]:
                ply_tank.stop_turning()
    elif event.type == pygame.MOUSEBUTTONUP: #When the user has released the left click
        mouse_clicked = True


def update_physic_object_list(skip_update, space):
    """
        Returns integer and updates the game objects space
    """
    if skip_update == 0:
        for obj in game_objects_list:
            obj.update()
        skip_update = 2
    else:
        skip_update -= 1

    space.step(1 / FRAMERATE)
    return skip_update


def draw_scoreboard(screen):
    """
        Draws a scoreboard on screen
    """
    pygame.draw.rect(screen, gray, (screen_width - scoreboard_width + 5, 5, scoreboard_width - 10, screen_height - 10)) #Border around button
    scoreboard_text = font_40.render("Scoreboard", True, black)
    scoreboard_text_rect = scoreboard_text.get_rect(center = (screen_width - scoreboard_width/2, 25))
    screen.blit(scoreboard_text, scoreboard_text_rect)


def draw_player_score(screen):
    """
        Draws the players score on the scoreboard
    """
    height_start = 55
    scoreboard_index = 1
    for player_id in scoreboard_order:
        pygame.draw.rect(screen, white, (screen_width - scoreboard_width + 10, height_start - 15, scoreboard_width - 20, 30)) #Border around button
        current_score = player_list[player_id]["score"]
        scoreboard_position = font_30.render(str(scoreboard_index) + ":", True, black)
        scoreboard_position_rect = scoreboard_position.get_rect(center = (screen_width - scoreboard_width + 25, height_start))
        score_text = font_30.render(str(current_score), True, black)
        score_text_rect = score_text.get_rect(center = (screen_width - scoreboard_width/2, height_start))
        tank_image = pygame.transform.scale(images.tanks[player_id], (19, 19))
        screen.blit(scoreboard_position, scoreboard_position_rect)
        screen.blit(tank_image, (screen_width - scoreboard_width/2 - score_text.get_width()/2 - 2 - tank_image.get_width(), height_start - tank_image.get_height()/2))
        screen.blit(score_text, score_text_rect)
        height_start = height_start + 35
        scoreboard_index = scoreboard_index + 1


def quit_when_finished(finished_game, running):
    """
        Quits the game if a player has reached maximun score
    """
    if finished_game != False:
        winning_player_text = font_30.render("Player " + str(finished_game["id"] + 1) + " has won the game!", True, black)
        winning_player_rect = winning_player_text.get_rect(center = ((screen_width-scoreboard_width)/2, screen_height/2-15))

        screen.blit(winning_player_text, winning_player_rect)

        finish_button.draw(screen)
        if finish_button.hovering() and mouse_clicked:
            running = False
            pygame.quit()
            quit()


screen_width = images.TILE_SIZE*current_map.width + scoreboard_width
screen_height = images.TILE_SIZE*current_map.height
screen = pygame.display.set_mode((screen_width, screen_height))


flag = create_flag()
create_boxes_on_map(current_map)
initialize_collision_handlers(space)
create_background(current_map, background)
create_static_borders(space)
create_tanks_on_map(current_map)
put_humanply_in_list(player_list, human_players)


singleplayer_player_id = None
if len(human_players) == 1: #If it's singleplayer, activate fog of war
    singleplayer_player_id = human_players[0] #Keeps track of what player will get fog

sounds.stop_menu_music() #Stops the menu music so it does not overlap the game music
sounds.play_game_music()
skip_update = 0
mouse_clicked = False
finish_button = ui.Button("finish", (screen_width-scoreboard_width) / 2 - 50, screen_height/2, 100, 40, font_30, "OK", black, white, gray) #Create the finish button
while running:
    for event in pygame.event.get():
        game_event_handler(event)
    #-- Update physicsgame_objects_list
    skip_update = update_physic_object_list(skip_update, space)

    #Saves tank for fog of war, only if singleplayer
    sp_tank = None
    if singleplayer_player_id != None:
        sp_tank = tanks_list[singleplayer_player_id] #Stores the tank object that should get fog for later

    #Check if tanks can grab flag and if they can score
    check_tank_flag_status(tanks_list, sp_tank, flag)

    #-- Loop through all the ai --#
    if finished_game == False:
        for ai in ai_list:
            ai.decide()
    #-- Update object that depends on an other object position (for instance a flag) --#
    for obj in game_objects_list:
        obj.post_update()
    #-- Update the screen --#
    screen.blit(background, (0, 0))
    for obj in game_objects_list:
        obj.update_screen(screen)

    if sp_tank != None and sp_tank.fog_of_war != False: #If singleplayer and player has flag activate fog of war
        sp_tank.make_fog(screen, current_map)

    #Draws the scoreboard
    draw_scoreboard(screen)

    #Draws the players score
    draw_player_score(screen)

    # If game is finished we draw who won and a quit button
    quit_when_finished(finished_game, running)
    
    mouse_clicked = False
    #-- Paint the display with color --#
    pygame.display.flip()
    #-- Control the game framerate (force it to make every tick of the game 20 milliseconds) --#
    clock.tick(FRAMERATE)
