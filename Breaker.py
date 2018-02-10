# Brick Breaker in pygame
# (c) 2017 Tingda Wang

import pygame, sys, random
from pygame.locals import *

# Window dimensions
WIN_W = 640
WIN_H = 480

# performance
FPS = 50

# object dimensions
BRICK_W = 55
BRICK_H = 15
PADDLE_W = 60
PADDLE_H = 12
BALL_SIZE = 16

# so paddle doesn't go to the right forever
MAX_PADDLE_X = WIN_W - PADDLE_W

MAX_BALL_X = WIN_W - BALL_SIZE
MAX_BALL_Y = WIN_H - BALL_SIZE

# paddle location (we set it later so doesn't matter what is here, might as well be 0)
PADDLE_X = int((WIN_W - PADDLE_W) / 2)
PADDLE_Y = WIN_H - PADDLE_H - 10

# Difficulty
LIVES = 3
SPEED = 5
SCORE_INCREMENT = 3

# Hip Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ROYAL_BLUE = (72, 118, 255)
PLUM = (255, 187, 255)

# states
BALL_ON_PADDLE = 0
PLAYING = 1
GAME_OVER = 2
WON = 3

class Breaker:

    def __init__(self): # constructor, creates window
        pygame.init()

        random.seed(1998) # seed for pseudo randomness

        self.display = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Brick Breaker - wtingda")
        
        self.clock = pygame.time.Clock()

        # Create font for displaying text
        font_size = 30
        if pygame.font:
            self.font = pygame.font.Font(None, font_size)
        else:
            self.font = None
        
        self.setup()

    # sets up game
    def setup(self): 
        self.lives = LIVES
        self.score = 0
        self.state = BALL_ON_PADDLE

        self.paddle = pygame.Rect(PADDLE_X, PADDLE_Y, PADDLE_W, PADDLE_H)
        self.ball = pygame.Rect(PADDLE_X, PADDLE_Y - BALL_SIZE, BALL_SIZE, BALL_SIZE)

        self.ball_speed = [SPEED, -SPEED]
        
        self.bricks = [] # stores all the bricks in here

        while not self.bricks: # makes sure we at least have 1 brick
            self.build_bricks()

    # generates the bricks
    def build_bricks(self): 
        y = 35
        for i in range(9):
            x = 25
            for j in range (9):
                put = random.randint(0, 1)
                if put:
                    self.bricks.append(pygame.Rect(x, y, BRICK_W, BRICK_H))
                x += BRICK_W + 10
            y += BRICK_H + 5

    # random colors for maximum hip
    def rand_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # draws bricks
    def display_bricks(self):
        for brick in self.bricks:
            color = self.rand_color()
            pygame.draw.rect(self.display, color, brick) 

    # draws paddle
    def display_paddle(self):
        pygame.draw.rect(self.display, ROYAL_BLUE, self.paddle)
    
    # draws ball
    def display_ball(self):
        pygame.draw.circle(self.display, WHITE, (self.ball.left + int(BALL_SIZE / 2), self.ball.top + int(BALL_SIZE / 2)), int(BALL_SIZE / 2))

    # keyboard inputs
    def input(self):
        keys = pygame.key.get_pressed() # get keys pressed
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: # go left
            self.paddle.left -= 5
            if self.paddle.left <= 0:
                self.paddle.left = 0

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: # go right
            self.paddle.left += 5
            if self.paddle.left >= MAX_PADDLE_X:
                self.paddle.left = MAX_PADDLE_X

        if keys[pygame.K_SPACE] and (self.state == BALL_ON_PADDLE): # launch ball
            self.ball_speed = [SPEED, -SPEED]
            self.state = PLAYING
        elif keys[pygame.K_RETURN] and (self.state == GAME_OVER or self.state == WON):
            self.setup() # restart game

    # tracks ball coordinates around screen
    def move_ball(self):
        self.ball.left += self.ball_speed[0]
        self.ball.top += self.ball_speed[1]

        if self.ball.left <= 0: # hit left wall
            self.ball.left = 0
            self.ball_speed[0] *= -1
        elif self.ball.left >= MAX_BALL_X: # hit right wall
            self.ball.left = MAX_BALL_X
            self.ball_speed[0] *= -1 

        if self.ball.top < 0: # hit top wall
            self.ball.top = 0
            self.ball_speed[1] *= -1

    # handles ball collision with bricks and paddle
    def collide(self):
        for brick in self.bricks:
            if self.ball.colliderect(brick): # colliderect checks for collisions so we don't have to
                self.score += SCORE_INCREMENT
                self.ball_speed[1] *= -1
                self.bricks.remove(brick)
                break
        
        if len(self.bricks) == 0: # all bricks broken
            self.state = WON
        
        # paddle collisions
        if self.ball.colliderect(self.paddle): # bounce
            self.ball.top = PADDLE_Y - BALL_SIZE
            self.ball_speed[1] *= -1
        elif self.ball.top > self.paddle.top: # all is lost
            self.lives -= 1
            if self.lives > 0: # restart ball
                self.state = BALL_ON_PADDLE
            else: # doomed
                self.state = GAME_OVER
        
    # displays the player score and lives
    def display_stats(self):
        if self.font:
            display_surface = self.font.render('Score: %s   Lives: %s' %(self.score, self.lives), True, BLACK) 
            self.display.blit(display_surface, (10, 5))

    # prints str in middle of screen
    def display_string(self, str):
        if self.font:
            size = self.font.size(str)
            display_surface = self.font.render(str, True, WHITE)
            x = (WIN_W - size[0]) / 2
            y = (WIN_H - size[1]) / 2
            self.display.blit(display_surface, (x, y))
    
    # determines state of the game
    def check_state(self):
        if self.state == PLAYING:
            self.move_ball()
            self.collide()
        elif self.state == BALL_ON_PADDLE:
            self.ball.left = self.paddle.left + int(self.paddle.width / 2) - 7  # 7 handles the casting round down
            self.ball.top = self.paddle.top - self.ball.height
            self.display_string("PRESS SPACE TO FIRE BALL")
        elif self.state == GAME_OVER:
            self.display_string("GAME OVER! PRESS ENTER TO PLAY AGAIN")
        elif self.state == WON:
            self.display_string("YIPEE YOU WON! PRESS ENTER TO PLAY AGAIN")
    
    # facilitates game
    def play(self):
        while True: # game loop
            
            pygame.mouse.set_visible(0)

            # determine event type
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()  
                elif event.type == MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                    self.paddle.x = mouse_x
                    if self.paddle.left >= MAX_PADDLE_X:
                        self.paddle.left = MAX_PADDLE_X

            self.clock.tick(FPS)
            self.display.fill(PLUM)

            self.input()
            
            self.check_state()

            # display items on screen
            self.display_bricks()
            self.display_paddle()
            self.display_ball()
            self.display_stats()
            
            pygame.display.flip() # Update the full display Surface to the screen

if  __name__ == "__main__":
    Breaker().play()
