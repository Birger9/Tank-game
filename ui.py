
import pygame

white=(255, 255, 255)
gray =(200, 200, 200)
black=(0, 0, 0)
green=(9,122,0)

class Button:
    """ Button object created for menu """
    def __init__(self, id, x, y, w, h, font, text, text_color, button_color, hover_color, val = None):
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.font = font
        self.text = text
        self.text_color = text_color
        self.color = button_color
        self.hover_color = hover_color
        self.hover = False
        self.val = val


    def draw(self, screen):
        """ Function creates the visuals of the buttons """
        color = self.color
        if self.hover:
            color = self.hover_color
        pygame.draw.rect(screen, black, (self.x, self.y, self.w, self.h)) #Border around button
        pygame.draw.rect(screen, color, (self.x + 1, self.y + 1, self.w - 2, self.h - 2)) #Color inside border

        button_surf = self.font.render(self.text, True, self.text_color) #Creates the text
        button_rect = button_surf.get_rect() #Returns a rectangle object of the button surface

        button_rect.center = self.x + (self.w / 2), self.y + (self.h/2) #Used to center the button
        screen.blit(button_surf, button_rect)


    def hovering(self):
        """ Checks if mouse is located on a button """
        mouse = pygame.mouse.get_pos()
        if (self.x + self.w) > mouse[0] > self.x and (self.y + self.h) > mouse[1] > self.y:
            self.hover = True
        else:
            self.hover = False
        return self.hover


class Sprite_button:
    """Button sprite object created for level editor"""
    def __init__(self, id, x, y, w, h, sprite, val = None):
        self.id = id
        self.x = x
        self.y = y
        self.sprite = pygame.transform.scale(sprite, (sprite.get_width()-2, sprite.get_height()-2))
        self.w = w
        self.h = h
        self.hover = False
        self.val = val


    def draw(self, screen):
        """ Function creates the visuals of the buttons """
        screen.blit(self.sprite, (self.x + self.w/2 - self.sprite.get_width()/2, self.y + self.h/2 - self.sprite.get_height()/2))


    def hovering(self):
        """ Checks if mouse is located on a button """
        mouse = pygame.mouse.get_pos()
        if (self.x + self.w) > mouse[0] > self.x and (self.y + self.h) > mouse[1] > self.y:
            self.hover = True
        else:
            self.hover = False
        return self.hover

class Text_entry:
    NUMBERS = "1234567890"
    LETTERS = "abcdefghijklmnopqrstuvwxyz1234567890"

    """A box you can enter text/numbers into"""
    def __init__(self, id, x, y, w, font, default = "", numberic = False, num_max = 20):
        self.id = id
        self.x = x
        self.y = y
        self.font = font
        self.w = w
        self.h = font.get_height() + 4
        self.hover = False
        self.text = default
        self.focus = False
        self.numeric = numberic
        self.num_max = num_max


    def draw(self, screen):
        """ Function creates the visuals of the text entry"""
        color = black
        if self.hover or self.focus:
            color = gray
        pygame.draw.rect(screen, color, (self.x, self.y, self.w, self.h)) #Border around button
        pygame.draw.rect(screen, white, (self.x + 1, self.y + 1, self.w - 2, self.h - 2)) #Color inside border

        button_surf = self.font.render(self.text, True, black) #Creates the text
        button_rect = button_surf.get_rect() #Returns a rectangle object of the button surface

        button_rect.center = self.x + (self.w / 2), self.y + (self.h/2) #Used to center the button
        screen.blit(button_surf, button_rect)


    def update_text(self, key):
        """Updates the text value in the text entry depending on the input key"""
        if key == "return":
            self.focus = False
        elif key == "backspace":
            self.text = self.text[:-1]
        elif self.numeric:
            if key in Text_entry.NUMBERS:
                self.text = self.text + key

                value = int(self.text)
                if self.num_max < value:
                    self.text = str(self.num_max)
        elif key in Text_entry.LETTERS:
            if len(self.text) < 7:
                self.text = self.text + key


    def hovering(self):
        """ Checks if mouse is located on the text entry"""
        mouse = pygame.mouse.get_pos()
        if (self.x + self.w) > mouse[0] > self.x and (self.y + self.h) > mouse[1] > self.y:
            self.hover = True
        else:
            self.hover = False
        return self.hover
