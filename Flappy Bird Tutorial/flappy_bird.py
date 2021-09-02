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
WIN_WIDTH = 500
WIN_HEIGHT = 900

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

    def move(self):
        self.tick_count += 1 #a frame went by, keep track of how many times we've moved since last jump
    
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2 #tells us based on our current birds' velocity how much we're moving up or down
        # - 10. 5 + 1.5 = 9 : we're moving upwards velocity of -9 we are moving 9 pixels upwards etc

        #terminal velocity- make sure we are not moving too far up or down
        if d >= 16:
            d = 16 #limit our velocity to 16
        
        #the little extra inch of jump movement
        if d < 0: 
            d -= 2

        self.y = self.y + d #whatever we calculate in our if loops to figure if we jump up or down

        #figure out the tilt
        if d < 0 or self.y < self.height + 50: #upward tilt
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else: #downward tilt
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    def draw(self, win): #represents the window we will draw the bird on
        self.img_count += 1 #how many times have we shown one image - tracker

        #check what image we should be showing based on the current img count
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        #check when bird is tilted 90 degrees downwards, we don't want it to
        #be flapping its wings/changing images
        if self.tilt <= -80:
            self.img = self.IMGS[1] #get the image where the wings are leveled 
            self.img_count = self.ANIMATION_TIME * 2 #when we jump back up, it doesn't skip frames

        #pygame function that rotates images for us
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft= (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft) #rotate image

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


def draw_window(win, bird): #draw the background image and bird on top of it
    win.blit(BG_IMG, (0,0)) #blit just draws
    bird.draw(win)
    pygame.display.update()

 #main function that runs our loop for the game   
def main():
    bird = Bird(200, 200)
    run = True
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    while run: #boolean flag to break the game later when it is false
        clock.tick(30) #slow down flappy's fall rate
        for event in pygame.event.get(): #keeps track of activities like user interaction
            if event.type == pygame.QUIT: 
                run = False

        #bird.move()
        draw_window(win, bird)

    pygame.quit()
    quit()

main()