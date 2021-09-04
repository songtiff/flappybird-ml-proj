import pygame
import neat
import time
import os
import random #randomly set the pipes
pygame.font.init()

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

STAT_FONT = pygame.font.SysFont("comicsans", 50)

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

#green pipes that flappy will dodge
class Pipe:
    GAP = 200 #space between pipes 
    VEL = 5 #and how fast pipes will be moving (flappy doesnt move but screen does)

    def __init__(self, x):
        self.x = x 
        self.height = 0

        #keep track of where the top/bottom of our pipes are going to be drawn
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) #flips pipe
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False #if flappy has already passed the pipe (for collision/AI purposes)
        self.set_height() #randomly defines where top/bottom pipe, height

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height() 
        self.bottom = self.height + self.GAP

    #pipe moves
    def move(self):
        self.x -= self.VEL #move pipe to the left a bit

    #draws our pipe
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    #flappy bird gliding by using masks (an "array" or "list" that contains our pixels)
    #a mask looks at image and figures out where all the pixels are and see if the pixels are transparent or not
    #then it creates a 2d that contains rows (pixels going down) and cols (pixels going up)
    def collide(self, bird):
        bird_mask = bird.get_mask()
        #create a mask for top/bottom pipes
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        #calculate off-set: check how far the masks are away from each other

        top_offset = (self.x - bird.x, self.top - round(bird.y)) #round because can't have negative
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        #find point of collision
        b_point = bird_mask.overlap(bottom_mask, bottom_offset) 
        t_point = bird_mask.overlap(top_mask, top_offset) 

        #check if either point exists, if we arent colling b/t-point will = None
        if t_point or b_point:
            return True

        return False

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    #using two base images by moving it back and forth after it exits the frame
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0: 
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, bird, pipes, base, score): #draw the background image and bird on top of it
    win.blit(BG_IMG, (0,0)) #blit just draws
    for pipe in pipes:
        pipe.draw(win)

    #render font
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    bird.draw(win)
    pygame.display.update()

 #main function that runs our loop for the game   
def main():
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(700)]
    run = True
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    while run: #boolean flag to break the game later when it is false
        clock.tick(30) #slow down flappy's fall rate
        for event in pygame.event.get(): #keeps track of activities like user interaction
            if event.type == pygame.QUIT: 
                run = False

        #bird.move()
        add_pipe = False
        rem = [] #list to remove
        for pipe in pipes:
            if pipe.collide(bird):
                pass
            
            #check if pipe is completely off screen 
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            #check if we have passed the pipe 
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        #increment player score count and show pipes
        if add_pipe:
            score += 1
            pipes.append(Pipe(650)) #distance of pipe spawnning closer/further away

        #iterate through list and remove all the pipes we have passed that
        #we stored in our rem array
        for r in rem:
            pipes.remove(r)

        #if flappy hits the ground, game over
        if bird.y + bird.img.get_height() >= 730:
            pass

        base.move()
        draw_window(win, bird, pipes, base, score)

    pygame.quit()
    quit()

main()