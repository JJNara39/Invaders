import pygame
import os
import random
pygame.font.init()

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0, 255, 0)

# Other info

LIVES_FONT = pygame.font.SysFont('comicsans', 40)
LEVEL_FONT = pygame.font.SysFont('comicsans', 40)
LOST_FONT = pygame.font.SysFont('comicsans', 40)
TITLE_FONT = pygame.font.SysFont('comicsans', 40)

# Window
WIDTH = 600
HEIGHT = 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Invaders of Space-Ness")

# Characters(and dimensions), Background
BKGD = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'background-black.png')), (WIDTH, HEIGHT))
PLAYER = pygame.image.load(os.path.join("Assets", "pixel_ship_yellow.png"))
SHIP_WIDTH, SHIP_HEIGHT = 55, 40

# Enemy Ships
RED_SHIP = pygame.image.load(os.path.join("Assets", "pixel_ship_red_small.png"))
BLUE_SHIP = pygame.image.load(os.path.join("Assets", "pixel_ship_blue_small.png"))
GREEN_SHIP = pygame.image.load(os.path.join("Assets", "pixel_ship_green_small.png"))

# Lasers
BLUE_LASER = pygame.image.load(os.path.join("Assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("Assets", "pixel_laser_green.png"))
RED_LASER = pygame.image.load(os.path.join("Assets", "pixel_laser_red.png"))
YELLOW_LASER = pygame.image.load(os.path.join("Assets", "pixel_laser_yellow.png"))



class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0) # this function checks if its off screen, so if its on screen, we want it to return a false value, hence the not() portion

    def collision(self, obj):
        return collide(obj, self)
            

class Ship: # make a main ship that will control all ships
    COOLDOWN = 30
    # Ship Movements
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None # allows us to draw the ship
        self.laser_img = None # allows us to draw the lasers
        self.lasers = []
        self.cool_down_counter = 0 # makes us unable to spam the shoot button

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None # if we didn't put that, it would have given us the point of intersection


class Player(Ship): # this means we made a player that inherits everything so far from Ship
    def __init__(self,x,y,health=100):
        super().__init__(x, y, health) # super allows us to use all of the initialize stuff from Ship 
        self.ship_img = PLAYER
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health # the health we start with is the maximum

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, RED, (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, GREEN, (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)


class Enemy(Ship):
    COLOR_MAP = { 
                "red": (RED_SHIP, RED_LASER),
                "green": (GREEN_SHIP, GREEN_LASER),
                "blue": (BLUE_SHIP, BLUE_LASER)
    }
    
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel # these enemies will move downward at a steady pace


def main():
    
    level = 0
    lives = 10
    FPS = 60
    enemies = []
    wave_length = 5
    enemy_vel = 1
    SHIP_VEL = 5
    laser_vel = 7

    player = Player(WIDTH//2, HEIGHT*3/4)


    lost = False
    lost_count = 0 # lost_count is keeping track of how many ships made it across, it will come into play in a second

    def draw_win():
        WIN.blit(BKGD, (0,0))
    
        lives_text = LIVES_FONT.render("Lives: " + str(lives), 1, WHITE)
        level_text = LEVEL_FONT.render("Level: " + str(level), 1, WHITE)
        WIN.blit(lives_text, (10, 10))
        WIN.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))
    
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = LOST_FONT.render("You Lost!!", 1, WHITE)
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
    
        pygame.display.update()


    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        draw_win()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3: # so give it a minute, 180 ships pass
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            if level > 1:
                enemy_vel += 0.5
                if Player.COOLDOWN >= 10:
                    Player.COOLDOWN -= 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red","blue","green"])) # this spawns them
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
    
        if keys[pygame.K_a] and player.x - SHIP_VEL > 0:
            player.x -= SHIP_VEL
        if keys[pygame.K_d] and player.x + SHIP_VEL + player.get_width() < WIDTH:
            player.x += SHIP_VEL
        if keys[pygame.K_SPACE]:
            player.shoot()
        

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*FPS) == 1: # randomly, we will check a range between 0 and 2*FPS, and if that value is 1 then they shoot, which will be more common than you think since there are multiple ships on screen
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 25
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

            

        player.move_lasers(-laser_vel, enemies) # the laser vel for the player's move_laser needs to be negative since its moving up, aka in the negative direction

def main_menu():
    run = True
    while run:
        WIN.blit(BKGD, (0,0))
        title_label = TITLE_FONT.render("Press the mouse to begin...", 1, WHITE)
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, HEIGHT/2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()