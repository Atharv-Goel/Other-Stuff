import pygame
import sys
from math import *
from time import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (127,127,127)


timers = [None, None, None, None, None, None]
screen = None
sprites = None
infSprites = None
clock = None
def setup(width, height):
    global screen, sprites, infSprites, clock

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    sprites = pygame.sprite.Group()
    infSprites = pygame.sprite.Group()

def startTimer(index, delete):
    global timers
    
    timers[index] = time()
    timers[index] -= delete

def timer(index):
    global timers

    return time() - timers[index]


def imageLoad(image):
    return pygame.image.load(image)

def music(music, loop):
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(loop)

def group():
    return pygame.sprite.Group()

class Sprite(pygame.sprite.Sprite):

    def __init__(self, color, width, height, x, y):

        super().__init__()
        
        self.orig_image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.orig_image.fill(color)
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.changeX = 0
        self.changeY = 0
        self.angle = 0
        self.rect.x = x
        self.rect.y = y
        self.mask = False
        self.offset = pygame.math.Vector2(0, 0)
        self.barriers = group()

        sprites.add(self)

    def setPic(self, picture, pic_x, pic_y):

        self.orig_image.blit(imageLoad(picture), [pic_x, pic_y])
        self.image = self.orig_image.copy()

    def setMask(self):

        self.mask = pygame.mask.from_surface(self.orig_image)
        self.image = self.orig_image.copy()

    def left(self, change):

        self.changeX = change * cos(radians(180 - self.angle))
        self.changeY = change * sin(radians(self.angle))

    def right(self, change):

        self.changeX = -(change * cos(radians(180 - self.angle)))
        self.changeY = -(change * sin(radians(self.angle)))

    def forward(self, change):

        self.changeX = change * cos(radians(self.angle + 90))
        self.changeY = change * sin(radians(self.angle - 90))

    def backward(self, change):

        self.changeX = -(change * cos(radians(self.angle + 90)))
        self.changeY = -(change * sin(radians(self.angle - 90)))

    def leftX(self, change):

        self.changeX = -change

    def rightX(self, change):

        self.changeX = change

    def stopX(self):

        self.changeX = 0

    def upY(self, change):

        self.changeY = -change

    def downY(self, change):

        self.changeY = change

    def stopY(self):

        self.changeY = 0

    def rotate(self, degrees):

        self.image = pygame.transform.rotate(self.orig_image, self.angle + degrees)
        x, y = self.rect.center
        self.rect = self.image.get_rect()
        offset_rotated = self.offset.rotate(degrees)
        self.rect.center = (x, y) + offset_rotated
        self.angle += degrees
        self.angle %= 360
        if self.mask:
            self.mask = pygame.mask.from_surface(self.image)

    def face(self, x, y):

        relX = x - self.rect.center[0]
        relY = y - self.rect.center[1]
        angle = 90 - degrees(atan2(-relY, relX))
        self.rotate(-(self.angle + angle))

    def collide(self, other, kill=False):

        tempList = pygame.sprite.Group()
        try:
            collisions = []
            for each in other:
                tempList.add(each)
                collision = pygame.sprite.spritecollide(self, tempList, False)
                if collision and self.mask and each.mask:
                    collision = pygame.sprite.spritecollide(self, tempList, kill, pygame.sprite.collide_mask)
                tempList.remove(each)
                for each in collision:
                    collisions.append(each)
            return collisions
                
        
        except TypeError:
            tempList.add(other)
            collision = pygame.sprite.spritecollide(self, tempList, False)
            if collision and self.mask and other.mask:
                collision = pygame.sprite.spritecollide(self, tempList, kill, pygame.sprite.collide_mask)
            tempList.remove(other)
            return collision

    def update(self):
        
        self.rect.x += self.changeX
        barriers = self.collide(self.barriers)
        if barriers:
            for barrier in barriers:
                if self.changeX > 0:
                    while self.collide(self.barriers):
                        self.rect.x -= 1
                else:
                    while self.collide(self.barriers):
                        self.rect.x += 1
                    
        self.rect.y += self.changeY
        barriers = self.collide(self.barriers)
        if barriers:
            for barrier in barriers:
                if self.changeY > 0:
                    while self.collide(self.barriers):
                        self.rect.y -= 1
                else:
                    while self.collide(self.barriers):
                        self.rect.y += 1
                
        
class infSprite(pygame.sprite.Sprite):

    def __init__(self, color, width, height, x, y, angle, speed, distance):

        super().__init__()

        self.orig_image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.orig_image.fill(color)
        self.orig_image = pygame.transform.rotate(self.orig_image, angle)
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.angle = angle
        self.speed = speed
        self.distance = 0
        self.maxDistance = distance
        self.mask = False
        infSprites.add(self)

    def setPic(self, picture, pic_x, pic_y):

        self.orig_image.blit(imageLoad(picture), [pic_x, pic_y])
        self.image = self.orig_image.copy()

    def setMask(self):

        self.mask = pygame.mask.from_surface(self.orig_image)
        self.image = self.orig_image.copy()

    def update(self):

        self.rect.x += self.speed * cos(radians(self.angle + 90))
        self.rect.y += self.speed * sin(radians(self.angle - 90))
        self.distance += self.speed
        if self.distance > self.maxDistance:
            infSprites.remove(self)


def keys():
    return pygame.key.get_pressed()

def mousePos():
    return pygame.mouse.get_pos()

def run(color):
    global screen, sprites, infSprites, clock

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
    screen.fill(color)
    infSprites.update()
    infSprites.draw(screen)
    sprites.update()
    sprites.draw(screen)
    clock.tick(60)
    pygame.display.flip()
