"""
This file defines all different kind of game objects as classes, for example the tanks, boxes
etc
"""

import pygame
import pymunk
import math
import images

DEBUG = False #Change this to set it in debug mode


def physics_to_display(x):
    """ This function is used to convert coordinates in the physic engine into the display coordinates """
    return x * images.TILE_SIZE


class GameObject:
    """ Mostly handles visual aspects (pygame) of an object.
        Subclasses need to implement two functions:
        - screen_position    that will return the position of the object on the screen
        - screen_orientation that will return how much the object is rotated on the screen (in degrees). """

    def __init__(self, sprite):
        self.sprite         = sprite


    def update(self):
        """ Placeholder, supposed to be implemented in a subclass.
            Should update the current state (after a tick) of the object."""
        return

    def post_update(self):
        """ Should be implemented in a subclass. Make updates that depend on
            other objects than itself."""
        return


    def update_screen(self, screen):
        """ Updates the visual part of the game. Should NOT need to be changed
            by a subclass."""
        sprite = self.sprite

        p = self.screen_position() #Get the position of the object (pygame coordinates)
        sprite = pygame.transform.rotate(sprite, self.screen_orientation()) #Rotate the sprite using the rotation of the object

        #The position of the screen correspond to the center of the object,
        #but the function screen.blit expect to receive the top left corner
        #as argument, so we need to adjust the position p with an offset
        #which is the vector between the center of the sprite and the top left
        #corner of the sprite
        offset = pymunk.Vec2d(sprite.get_size()) / 2.
        p = p - offset
        screen.blit(sprite, p) #Copy the sprite on the screen



class GamePhysicsObject(GameObject):
    """ This class extends GameObject and it is used for objects which have a
        physical shape (such as tanks and boxes). This class handle the physical
        interaction of the objects.
    """

    def __init__(self, x, y, orientation, sprite, space, movable):
        """ Takes as parameters the starting coordinate (x,y), the orientation, the sprite (aka the image
            representing the object), the physic engine object (space) and whether the object can be
            moved (movable).
        """

        super().__init__(sprite)

        #Half dimensions of the object converted from screen coordinates to physic coordinates
        half_width          = 0.5 * self.sprite.get_width() / images.TILE_SIZE
        half_height         = 0.5 * self.sprite.get_height() / images.TILE_SIZE

        #Physical objects have a rectangular shape, the points correspond to the corners of that shape.
        points              = [[-half_width, -half_height],
                            [-half_width, half_height],
                            [half_width, half_height],
                            [half_width, -half_height]]
        self.points = points
        #Create a body (which is the physical representation of this game object in the physic engine)
        if(movable):
            #Create a movable object with some mass and moments
            #(considering the game is a top view game, with no gravity,
            #the mass is set to the same value for all objects)."""
            if hasattr(self, 'boxmodel') and self.boxmodel.movable == True and self.boxmodel.destructable == False:
                mass = 5
            elif hasattr(self, 'boxmodel') and self.boxmodel.movable == True and self.boxmodel.destructable == True:
                mass = 2
            else:
                mass = 10
            moment = pymunk.moment_for_poly(mass, points)
            self.body         = pymunk.Body(mass, moment)
        else:
            self.body         = pymunk.Body(body_type=pymunk.Body.STATIC) #Create a non movable (static) object

        self.body.position  = x, y
        self.body.angle     = math.radians(orientation)       #orientation is provided in degress, but pymunk expects radians.
        self.shape          = pymunk.Poly(self.body, points)  #Create a polygon shape using the corner of the rectangle

        #Set some value for friction and elasticity, which defines interraction in case of a colision
        self.shape.friction = 0.5
        self.shape.elasticity = 0.1
        self.shape.parent = self

        #Add the object to the physic engine
        if(movable):
            space.add(self.body, self.shape)
        else:
            space.add(self.shape)


    def screen_position(self):
        """ Converts the body's position in the physics engine to screen coordinates. """
        return physics_to_display(self.body.position)

    def screen_orientation(self):
        """ Angles are reversed from the engine to the display. """
        return -math.degrees(self.body.angle)

    def update_screen(self, screen):
        super().update_screen(screen)
        #debug draw
        if DEBUG:
            ps = [self.body.position+p for p in self.points]

            ps = [physics_to_display(p) for p in ps]
            ps += [ps[0]]
            pygame.draw.lines(screen, pygame.color.THECOLORS["red"], False, ps, 1)

def clamp (minval, val, maxval):
    """ Convenient helper function to bound a value to a specific interval. """
    if val < minval: return minval
    if val > maxval: return maxval
    return val


class Tank(GamePhysicsObject):
    """ Extends GamePhysicsObject and handles aspects which are specific to our tanks. """

    #Constant values for the tank, acessed like: Tank.ACCELERATION
    ACCELERATION = 0.4
    NORMAL_MAX_SPEED = 2.0
    FLAG_MAX_SPEED = NORMAL_MAX_SPEED * 0.5

    def __init__(self, x, y, orientation, sprite, space, id, hp):
        super().__init__(x, y, orientation, sprite, space, True)
        #Define variable used to apply motion to the tanks
        self.acceleration         = 0.0
        self.velocity             = 0.0
        self.angular_acceleration = 0.0
        self.angular_velocity     = 0.0
        self.next_shoot = 0
        self.tile_dist = 0
        self.id = id
        self.respawn_delay = 0
        self.tank_hitpoints = hp
        self.fog_of_war = False

        self.shape.collision_type = 2

        self.flag                 = None                      # This variable is used to access the flag object, if the current tank is carrying the flag
        self.maximum_speed        = Tank.NORMAL_MAX_SPEED     # Impose a maximum speed to the tank
        self.start_position       = pymunk.Vec2d(x, y)        # Define the start position, which is also the position where the tank has to return with the flag

    def accelerate(self):
        """ Call this function to make the tank move forward. """
        self.acceleration = Tank.ACCELERATION


    def decelerate(self):
        """ Call this function to make the tank move backward. """
        self.acceleration = -Tank.ACCELERATION

    #
    def turn_left(self):
        """ Makes the tank turn left (counter clock-wise). """
        self.angular_acceleration = -Tank.ACCELERATION


    def turn_right(self):
        """ Makes the tank turn right (clock-wise). """
        self.angular_acceleration = Tank.ACCELERATION

    def update(self):
        """ A function to update the objects coordinates. Gets called at every tick of the game. """

        #Update the velocity of the tank in function of the physic simulation (in case of colision, the physic simulation will change the speed of the tank)
        if(math.fabs(self.velocity) > 0 ):
            self.velocity         *= self.body.velocity.length  / math.fabs(self.velocity)
        if(math.fabs(self.angular_velocity) > 0 ):
            self.angular_velocity *= math.fabs(self.body.angular_velocity / self.angular_velocity)

        #Update the velocity in function of the acceleration
        self.velocity         += self.acceleration
        self.angular_velocity += self.angular_acceleration

        #Make sure the velocity is not larger than a maximum speed
        self.velocity         = clamp(-self.maximum_speed, self.velocity,         self.maximum_speed)
        self.angular_velocity = clamp(-self.maximum_speed, self.angular_velocity, self.maximum_speed)

        #Update the physic velocity
        self.body.velocity = pymunk.Vec2d((0, self.velocity)).rotated(self.body.angle)
        self.body.angular_velocity = self.angular_velocity

    def stop_moving(self):
        """ Call this function to make the tank stop moving. """
        self.velocity     = 0
        self.acceleration = 0

    def stop_turning(self):
        """ Call this function to make the tank stop turning. """
        self.angular_velocity     = 0
        self.angular_acceleration = 0

    def post_update(self):
        #If the tank carries the flag, then update the positon of the flag
        if(self.flag != None):
            self.flag.x           = self.body.position[0]
            self.flag.y           = self.body.position[1]
            self.flag.orientation = -math.degrees(self.body.angle)
        #Else ensure that the tank has its normal max speed
        else:
            self.maximum_speed = Tank.NORMAL_MAX_SPEED

        if self.next_shoot > 0:
            self.next_shoot = self.next_shoot - 20

        if self.respawn_delay > 0:
            self.respawn_delay = self.respawn_delay - 20


    def try_grab_flag(self, flag):
        """ Call this function to try to grab the flag, if the flag is not on other tank
            and it is close to the current tank, then the current tank will grab the flag.
        """
        #Check that the flag is not on other tank
        if(not flag.is_on_tank):
            #Check if the tank is close to the flag
            flag_pos = pymunk.Vec2d(flag.x, flag.y)
            if((flag_pos - self.body.position).length < 0.5):
                #Grab the flag !
                self.flag           = flag
                flag.is_on_tank     = True
                self.maximum_speed  = Tank.FLAG_MAX_SPEED

    def has_scored(self):
        """ Check if the current tank has won (if it is has the flag and it is close to its start position). """
        if self.flag != None and (self.start_position - self.body.position).length < 0.2:
            self.flag.is_on_tank = False
            self.flag = None
            return True

    def shoot(self, space):
        """ Call this function to shoot a missile (current implementation does nothing ! you need to implement it yourself) """
        return Bullet(self, self.body.position[0], self.body.position[1], self.body.angle, space)

    def respawn_protection(self):
        """Activates respawn protection"""
        self.respawn_delay = 4000 #Four seconds res protection

    def check_tank_hp(self):
        """Checks tanks hp, if 0hp left return True"""
        if self.tank_hitpoints > 1:
            self.tank_hitpoints -= 1
            return False
        else:
            return True

    def make_fog(self, screen, current_map):
        ''' When victory awaits and the heart raises, why not make it harder with a black fog...'''
        screen_width = current_map.width * images.TILE_SIZE
        screen_height = current_map.height * images.TILE_SIZE
        tank_pos = physics_to_display(self.body.position).int_tuple
        fog_of_war = pygame.Surface((screen_width, screen_height))
        fog_of_war.fill((0, 0, 0)) #Makes whole screen black
        pygame.draw.circle(fog_of_war, (60, 60, 60), tank_pos, 100, 0) #Draws a circle around the tank with the color (60,60,60)
        fog_of_war.set_colorkey((60, 60, 60)) #Makes that color transparent
        screen.blit(fog_of_war, (0,0))


class Bullet(GamePhysicsObject):
    '''This class extends the GamePhysicsObject to handle bullet objects '''
    def __init__(self, shot_by, x, y, angle, space):
        super().__init__(x, y, 0, images.bullet, space, True)
        self.shot_by = shot_by #The tank that shot the bullet
        self.shape.friction = 0 # A bullet should not have any friction
        self.body.angle = angle
        self.velocity = 5
        self.shape.collision_type = 1

    def post_update(self):
        """ A function to update the objects coordinates. Gets called at every tick of the game. """
        self.body.velocity = pymunk.Vec2d((0, self.velocity)).rotated(self.body.angle)


class Explosion(pygame.sprite.Sprite):
    """ Sprite of a bullet exploding """
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.explosion_image = images.explosion[0] #Loads the first picture in the list
        self.rect = self.explosion_image.get_rect()
        self.rect.center = center
        self.explosion_frame = -1 #Each picture of the explosion animation is a frame
        self.last_update = pygame.time.get_ticks()
        self.framerate = 50

    def update_screen(self, screen):
        ''' Updates the animation of explosion '''
        screen.blit(self.explosion_image, self.rect.center)

    def post_update(self):
        """ Updates the explosion animation """
        now = pygame.time.get_ticks() #Milliseconds since game started
        if now - self.last_update > self.framerate: #When 50 milliseconds passed
            self.last_update = now #Updates the picture timer
            self.explosion_frame += 1
            if self.explosion_frame > len(images.explosion):
                self.kill() #Removes explosion sprite from game_objects_list
            elif self.explosion_frame < 9: #Index only goes to 8
                center = self.rect.center
                self.explosion_image = images.explosion[self.explosion_frame]
                self.rect = self.explosion_image.get_rect()
                self.rect.center = center



class Box(GamePhysicsObject):
    """ This class extends the GamePhysicsObject to handle box objects. """

    def __init__(self, x, y, boxmodel, space, hitpoints):
        """ It takes as arguments the coordinate of the starting position of the box (x,y) and the box model (boxmodel). """
        self.boxmodel = boxmodel
        super().__init__(x, y, 0, self.boxmodel.sprite, space, self.boxmodel.movable)
        self.shape.collision_type = 3
        self.velocity = 0
        self.angular_acceleration = 0.0
        self.angular_velocity     = 0.0
        self.maximum_speed        = Tank.NORMAL_MAX_SPEED
        self.acceleration = 0
        self.hit_points = hitpoints
        self.x = x
        self.y = y

    def post_update(self):
        self.body.velocity *= 0.5
        self.body.angular_velocity *= 0.5


    def check_box_hp(self):
        """Checks the hp of a box, if hp = 0 return True"""
        if self.hit_points > 1:
            self.hit_points -= 1
            return False
        else:
            return True


class GameVisibleObject(GameObject):
    """ This class extends GameObject for object that are visible on screen but have no physical representation (bases and flag) """

    def __init__(self, x, y, sprite):
        """ It takes argument the coordinates (x,y) and the sprite. """
        self.x            = x
        self.y            = y
        self.orientation  = 0
        super().__init__(sprite)

    def screen_position(self):
        return physics_to_display(pymunk.Vec2d(self.x, self.y))

    def screen_orientation(self):
        return self.orientation


class Flag(GameVisibleObject):
    """ This class extends GameVisibleObject for representing flags."""

    def __init__(self, x, y):
        self.is_on_tank   = False
        self.start_x = x
        self.start_y = y
        super().__init__(x, y,  images.flag)

    def respawn(self):
        self.x            = self.start_x
        self.y            = self.start_y
        self.is_on_tank   = False
