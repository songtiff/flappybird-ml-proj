import pygame
import neat
import time
import os
import random #randomly set the pipes

#access img folders
os.chdir("C:/Users/Tiffany/Downloads")
#check if current directory is correct
"""cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
print("Files in %r: %s" % (cwd, files))"""

#set the size of screen
WIN_WIDTH = 600
WIN_HEIGHT = 600

#load images
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 #degrees in how much the bird will tilt when moving up/down
    ROT_VEL = 20 #velocity, how much we will be rotating during each frame- everytime flappy moves
    ANIMATION_TIME = 5 #how long we show each bird animation, changing larger/smaller changes how fast bird moves in frames

    def __init__(self, x, y):
        #x,y represents starting position of flappy
        self.x = x
        self.y = y
        self.tilt = 0 #how much the image is tilted, start off zero because flappy will be flat til flappy moves
        self.tick_count = 0 #figure out the physics of the bird
        self.vel = 0 #velocy of 0 because flappy.start doesn't move
        self.height = self.y 
        self.img_count = 0 #to know what img we are on
        self.img = self.IMGS[0] #references the bird images, imgs[0] grabs the first bird img

    def jump(self):
        #(0,0) represents the top left of the screen
        self.vel = -10.5 #if we want to move up, we need a negative velocity in the x-direction if we want to go downwards, we need a positive velocity in the y-direction
        self.tick_count = 0 #keeps track of when we last jumped
        self.height = self.y #keeps track of where flappy started moving/jumping from
