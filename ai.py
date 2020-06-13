"""
This file defines the class A.I and declares its methods.
"""

import math
import pymunk
from pymunk import Vec2d
import gameobjects
from collections import defaultdict, deque

import sounds
# NOTE: use only 'map0' during development!

MIN_ANGLE_DIF = math.radians(3) # 3 degrees, a bit more than we can turn each tick


def angle_between_vectors(vec1, vec2):
    """ Since Vec2d operates in a cartesian coordinate space we have to
        convert the resulting vector to get the correct angle for our space.
    """
    vec = vec1 - vec2
    vec = vec.perpendicular()
    return vec.angle


def periodic_difference_of_angles(angle1, angle2):
    return  (angle1% (2*math.pi)) - (angle2% (2*math.pi))


def turn_decider(rad):
    '''If function returns True -> turn left, if function returns False -> turn right'''
    if (rad >= 0 and rad < (math.pi)) or (rad >= (-3*math.pi/2) and rad <= (-math.pi)):
        return 1 #Left
    else:
        return 2 #Right


class Ai:
    """ A simple ai that finds the shortest path to the target using
    a breadth first search. Also capable of shooting other tanks and or wooden
    boxes. """


    def __init__(self, tank,  game_objects_list, tanks_list, space, currentmap):
        self.tank               = tank
        self.game_objects_list  = game_objects_list
        self.tanks_list         = tanks_list
        self.space              = space
        self.currentmap         = currentmap
        self.flag = None
        self.MAX_X = currentmap.width - 1
        self.MAX_Y = currentmap.height - 1
        self.allow_metalbox = False

        self.path = deque()
        self.move_cycle = self.move_cycle_gen()
        self.update_grid_pos()


    def update_grid_pos(self):
        """ This should only be called in the beginning, or at the end of a move_cycle. """
        self.grid_pos = self.get_tile_of_position(self.tank.body.position)


    def decide(self):
        """ Main decision function that gets called on every tick of the game. """
        next(self.move_cycle)
        self.maybe_shoot()


    def update_on_death(self, tank):
        """Called upon when tank is destroyed"""
        self.tank = tank
        self.allow_metalbox = False#After the tank hase died, it are not allowed to find a path using metalbox
        self.flag = None


    def maybe_shoot(self):
        """ Makes a raycast query in front of the tank. If another tank
            or a wooden box is found, then we shoot.
        """
        angle = self.tank.body.angle + (math.pi/2) #Same angle as tank but added pi/2 because math library and pymunk does not match
        radius = 0.3 #Tank has lengh 0.25 from center to edge. By making radius 0.3 the ray begins at the tip of the tank and doesn't collide with tank
        map_length = self.currentmap.width #The lengh of ray is as long as the map is wide. Could be set to 100 but map width is nicer

        first_x_coord = math.cos(angle) * radius #makes x coordinate with right lenght and angle that can be attached to the tank
        first_y_coord = math.sin(angle) * radius #makes y coordinate with right lenght and angle that can be attached to the tank
        first_x_bullet = self.tank.body.position[0] + first_x_coord #Attaches the x coordinate to tank so the ray always is 0.3 lenght from tank and with the same angle as tank
        first_y_bullet = self.tank.body.position[1] + first_y_coord #Attaches the y coordinate to tank
        ray_start_pos = (first_x_bullet, first_y_bullet) #x and y where ray begins

        second_x_coord = math.cos(angle) * map_length #Same as above
        second_y_coord = math.sin(angle) * map_length
        second_x_bullet = self.tank.body.position[0] + second_x_coord
        second_y_bullet = self.tank.body.position[1] + second_y_coord
        ray_end_pos = (second_x_bullet, second_y_bullet) #x and y where ray ends

        res = self.space.segment_query_first(ray_start_pos, ray_end_pos, 0, pymunk.ShapeFilter()) #0 for radius of ray, returns first object ray hits

        if hasattr(res, 'shape'): #If the returned object from raycast has an attribute named 'shape' we enter if statement
            if not isinstance(res.shape, pymunk.Segment): #As long as ray didn't hit invicible segment enter if statement
                if isinstance(res.shape.parent, gameobjects.Tank) or (isinstance(res.shape.parent, gameobjects.Box) and res.shape.parent.boxmodel.destructable): #If returned object from ray is either a tank or woddenbox
                    if self.tank.next_shoot < 1: #Delay between shots
                        self.tank.next_shoot = 1000
                        sounds.play_tank_shot()
                        bullet = self.tank.shoot(self.space) #Add bullet to space and game_objects_list
                        self.game_objects_list.append(bullet)


    def correct_angle(self):
        '''
        Checks if tank is lined up correctly if not return False,
        Used for pathfinding
        '''
        vector_angle = angle_between_vectors(self.grid_pos, self.next_coord)
        self.angle_btw_vec = periodic_difference_of_angles(self.tank.body.angle, vector_angle)
        if self.angle_btw_vec < MIN_ANGLE_DIF and self.angle_btw_vec > -MIN_ANGLE_DIF:
            return True
        else: #angle_btw_vec > MIN_ANGLE_DIF or angle_btw_vec < -MIN_ANGLE_DIF:
            return False


    def correct_pos(self):
        '''
        Returns True if we are standing on the correct coordinate
        Used for pathfinding
        '''
        if self.tank.tile_dist < self.tank.body.position.get_distance(self.target_coord):
            self.ready_to_turn = True
            return True
        else:
            return False


    def move_cycle_gen (self):
        """
        The brain of the A.I, decides what the A.I should do next, called upon every tick
        """
        while True:
            shortest_path = self.find_shortest_path() #Hitta kortaste vägen till target
            if not shortest_path: #Hittar vi ingen väg så körs loopen om
                self.allow_metalbox = True
                yield
                continue

            self.allow_metalbox = False
            self.next_coord = shortest_path.popleft() #Fösta delmålet för att komma till target
            self.target_coord = self.next_coord + [0.5, 0.5]
            self.tank.tile_dist = self.tank.body.position.get_distance(self.target_coord) #Avståndet mellan target_coord och tankens position
            yield

            self.tank.accelerate()
            if not self.correct_pos():
                self.ready_to_turn = False

            while not self.correct_angle() and self.ready_to_turn == True:
                self.tank.stop_moving()
                direction = turn_decider(self.angle_btw_vec)
                if direction == 1:
                    self.tank.turn_left()
                elif direction == 2:
                    self.tank.turn_right()
                yield

            self.tank.stop_turning()
            yield


    def find_shortest_path(self):
        """ A simple Breadth First Search using integer coordinates as our nodes.
            Edges are calculated as we go, using an external function.
        """
        #-- Initialisation of the things we need --# #Need to update grid_pos for the tank
        self.update_grid_pos()
        source_tile = self.grid_pos
        target_tile = self.get_target_tile()
        visited_set = set()
        deck = deque()
        deck.append(source_tile)

        shortest_path = []
        parent = {} #Maps neighbor to source

        parent[source_tile.int_tuple] = -1 #Stop condition

        while deck: #While deck contains some form of information
            left_tile = deck.popleft() #Removes the first node from the queue
            visited_set.add(left_tile.int_tuple)
            if left_tile == self.get_target_tile(): #Is True if the node removed from the queue is the target tile
                shortest_path.insert(0, left_tile) #Adds the target tile to shortest_path list
                while parent[left_tile.int_tuple] != -1:
                    shortest_path.insert(0, parent[left_tile.int_tuple])
                    left_tile = parent[left_tile.int_tuple]
                shortest_path.remove(left_tile) #Removes the tile the tank started on
                break
            for neighbor in self.get_tile_neighbors(left_tile):
                if not neighbor.int_tuple in visited_set: #If the neighbor node has not already been visited
                    deck.append(neighbor) #Adds it to the queue
                    visited_set.add(neighbor.int_tuple) #Add it to our set of visited nodes
                    parent[neighbor.int_tuple] = left_tile #Saves the path to this node in the dict parent
        return deque(shortest_path)


    def get_target_tile(self):
        """ Returns position of the flag if we don't have it. If we do have the flag,
            return the position of our home base.
        """
        if self.tank.flag != None:
            x, y = self.tank.start_position
        else:
            self.get_flag() # Ensure that we have initialized it.
            x, y = self.flag.x, self.flag.y
        return Vec2d(int(x), int(y))


    def get_flag(self):
        """ This has to be called to get the flag, since we don't know
            where it is when the Ai object is initialized.
        """
        if self.flag == None:
        # Find the flag in the game objects list
            for obj in self.game_objects_list:
                if isinstance(obj, gameobjects.Flag):
                    self.flag = obj
                    break
        return self.flag


    def get_tile_of_position(self, position_vector):
        """ Converts and returns the float position of our tank to an integer position. """
        x, y = position_vector
        return Vec2d(int(x), int(y))


    def get_tile_neighbors(self, coord_vec):
        """ Returns all bordering grid squares of the input coordinate.
            A bordering square is only considered accessible if it is grass
            or a wooden box.
        """
        neighbors = [coord_vec + delta for delta in [(0, 1), (0, -1), (1, 0), (-1, 0)]] # Find the coordinates of the tiles' four neighbors
        return filter(self.filter_tile_neighbors, neighbors) #The built-in python function filter applies the first argument funtion onto the second arguments iterable


    def filter_tile_neighbors (self, coord):
        """
        Checks if the given tile coordinates is a valid path for the tank
        """
        #-- If the coord is out of the maps boundary --#
        if coord[0] >= 0 and coord[0] <= self.MAX_X and coord[1] >= 0 and coord[1] <= self.MAX_Y:
            box = self.currentmap.boxAt(coord[0], coord[1])
            if box == 0 or box == 2 or (box == 3 and self.allow_metalbox == True):
                return True
        return False


SimpleAi = Ai # Legacy
