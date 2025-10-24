import pygame
from pygame import mixer
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# Define fps
clock = pygame.time.Clock()
fps = 60

# Screen settings
screen_width = 600
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invaders')

# Define fonts
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)

# Load sounds
explosion_fx = pygame.mixer.Sound("explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("laser.wav")
laser_fx.set_volume(0.25)

# Define colors
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

# Load background image
bg = pygame.image.load("bg.png")

# Load heart image
heart_img = pygame.image.load("heart.jpg")
heart_img = pygame.transform.scale(heart_img, (20, 20))


def draw_bg():
    screen.blit(bg, (0, 0))


# Function to draw text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Create Explosion class
class Explosion(pygame.sprite.Sprite):
    def _init_(self, x, y, size):
        pygame.sprite.Sprite._init_(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"exp{num}.png")
            img = pygame.transform.scale(img, (20 * size, 20 * size))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


# Create Bullets class
class Bullets(pygame.sprite.Sprite):
    def _init_(self, x, y):
        pygame.sprite.Sprite._init_(self)
        self.image = pygame.image.load("bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)


# Create Spaceship class
class Spaceship(pygame.sprite.Sprite):
    def _init_(self, x, y, health):
        pygame.sprite.Sprite._init_(self)
        self.image = pygame.image.load("spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        speed = 8
        cooldown = 500  # milliseconds
        global game_over  # Use the global game_over variable

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        time_now = pygame.time.get_ticks()
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            laser_fx.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        self.mask = pygame.mask.from_surface(self.image)

        pygame.draw.rect(screen, red, (self.rect.x, self.rect.bottom + 10, self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (
                self.rect.x, self.rect.bottom + 10, int(self.rect.width * (self.health_remaining / self.health_start)),
                15))
        else:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = True  # Set game over to True
        return game_over


# Create Aliens class
class Aliens(pygame.sprite.Sprite):
    def _init_(self, x, y):
        pygame.sprite.Sprite._init_(self)
        self.image = pygame.image.load("alien" + str(random.randint(1, 5)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

        time_now = pygame.time.get_ticks()
        if time_now - self.last_shot > random.randint(1000, 3000):
            bullet = Alien_Bullets(self.rect.centerx, self.rect.bottom)
            alien_bullet_group.add(bullet)
            self.last_shot = time_now


# Create Alien Bullets class
class Alien_Bullets(pygame.sprite.Sprite):
    def _init_(self, x, y):
        pygame.sprite.Sprite._init_(self)
        self.image = pygame.image.load("alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)


# Create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

level = 1
max_levels = 5


def create_aliens():
    alien_group.empty()
    for row in range(level + 2):
        for col in range(level + 2):
            alien = Aliens(100 + col * 100, 100 + row * 70)
            alien_group.add(alien)


spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)

create_aliens()

# Get Ready Timer
get_ready_time = 3  # seconds
start_time = pygame.time.get_ticks()
game_started = False
countdown_number = 3

# Game Over Variable
game_over = False

run = True
while run:
    clock.tick(fps)
    draw_bg()

    # Get Ready Timer Logic
    if not game_started and not game_over:
        current_time = pygame.time.get_ticks()
        time_elapsed = (current_time - start_time) / 1000
        if time_elapsed < get_ready_time:
            countdown_number = int(get_ready_time - time_elapsed)
            if countdown_number > 0:
                draw_text(str(countdown_number), font40, white, screen_width // 2 - 10, screen_height // 2 - 50)
            else:
                draw_text("Go!", font40, white, screen_width // 2 - 30, screen_height // 2 - 50)
        else:
            game_started = True
    elif game_over:
        draw_text("Game Over", font40, white, screen_width // 2 - 100, screen_height // 2 - 50)  # Draw game over text
    else:
        draw_text(f'Level {level}', font40, white, screen_width // 2 - 50, 30)

        if len(alien_group) == 0 and level < max_levels:
            level += 1
            create_aliens()

        spaceship.update()
        bullet_group.update()
        alien_group.update()
        alien_bullet_group.update()
        explosion_group.update()

        spaceship_group.draw(screen)
        bullet_group.draw(screen)
        alien_group.draw(screen)
        alien_bullet_group.draw(screen)
        explosion_group.draw(screen)

        # Draw Hearts for Remaining Life
        for i in range(spaceship.health_remaining):
            screen.blit(heart_img, (10 + i * 30, 10))  # Position of the hearts
        if spaceship.health_remaining <= 0:
            game_over = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
