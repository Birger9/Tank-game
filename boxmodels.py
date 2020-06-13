"""
This file defines the different types of box models and their attributes
"""

import images

class BoxModel:
  """ This class defines a model of the box, it contains information on the type of box,
      whether it can be moved, destroyed and the sprite.
  """

  def __init__(self, sprite, movable, destructable, boxtype):
    self.sprite         = sprite
    self.movable        = movable
    self.destructable   = destructable
    self.boxtype = boxtype


woodbox  = BoxModel(images.woodbox,  movable=True, destructable=True, boxtype=2)

metalbox = BoxModel(images.metalbox, movable=True, destructable=False, boxtype=3)

rockbox  = BoxModel(images.rockbox, movable=False, destructable=False, boxtype=1)


def get_model(type):
  """ This function is used to select the model of a box in function of a number.
      It is mostly used when initializing the boxes from the information contained in the map.
  """
  if(type == 1):
    return rockbox
  elif(type == 2):
    return woodbox
  elif(type == 3):
    return metalbox
  else:
    return None
