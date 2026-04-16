import pygame
import sys
import random
import mmap
import struct
import subprocess
import ctypes
import os
import time

# =========================
# Shared Memory Setup (Zero-Copy)
# =========================
class PhysicsData(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("vx", ctypes.c_float),
        ("vy", ctypes.c_float),
        ("ax", ctypes.c_float),
        ("ay", ctypes.c_float)
    ]

SIZE = ctypes.sizeof(PhysicsData)
TAG_NAME = "MySharedMemory"


shm = mmap.mmap(-1, SIZE, tagname=TAG_NAME)


particle_data = PhysicsData.from_buffer(shm)



# =========================
# Fix path for EXE
# =========================
def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

image_path = resource_path("Goodsw.png")

# =========================
# Particle System
# =========================
YELLOW, ORANGE, RED, BLACK = (255,255,0), (255,165,0), (255,0,0), (0,0,0)
COLOR_GRADIENT = [YELLOW, ORANGE, RED, BLACK]

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = random.randint(2,4)
        self.lifespan = random.randint(4,6)
        self.age = 0
        self.image = pygame.Surface((self.size,self.size))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity_x = random.uniform(-2,2)
        self.velocity_y = random.uniform(-140,-100)

    def get_color(self):
        idx = min(self.age // max(1,(self.lifespan // len(COLOR_GRADIENT))), len(COLOR_GRADIENT)-1)
        return COLOR_GRADIENT[idx]

    def update(self):
        self.age += 1
        if self.age >= self.lifespan: self.kill()
        self.rect.x += self.velocity_x * self.size / 20
        self.rect.y -= self.velocity_y * self.size / 20
        self.image.fill(self.get_color())

# =========================
# Window Setup
# =========================
pygame.init()
wind = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()

try:
    image = pygame.image.load(image_path)
    scaled_image = pygame.transform.scale(image, (image.get_width(), image.get_height()))
except:
    print("Image error"); sys.exit()

particle_group = pygame.sprite.Group()


try:
    process = subprocess.Popen([resource_path("physics.exe")])
except:
    print("C++ EXE not found")

power = 0.2
stop = False


particle_data.x, particle_data.y = 100.0, 100.0

# =========================
# Game Loop
# =========================
while True:
    clock.tick(60)
    wind.fill((175, 175, 175))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            process.terminate()
            shm.close()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d: particle_data.ax = power
            elif event.key == pygame.K_a: particle_data.ax = -power
            elif event.key == pygame.K_w: particle_data.ay = -power
            elif event.key == pygame.K_s: particle_data.ay = power
            elif event.key == pygame.K_SPACE: stop = True
            elif event.key == pygame.K_LSHIFT: power = 1.0

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_d, pygame.K_a): particle_data.ax = 0
            elif event.key in (pygame.K_w, pygame.K_s): particle_data.ay = 0
            elif event.key == pygame.K_SPACE: stop = False
            elif event.key == pygame.K_LSHIFT: power = 0.2

    if stop:
        particle_data.vx *= 0.9
        particle_data.vy *= 0.9

 
    for i in range(10):
        particle_group.add(Particle(particle_data.x + 13, particle_data.y + 70))
        particle_group.add(Particle(particle_data.x + 125, particle_data.y + 70))

    particle_group.update()
    particle_group.draw(wind)

    wind.blit(scaled_image, (particle_data.x, particle_data.y))

    # Debug
    font = pygame.font.SysFont("Arial", 20)
    text = font.render(f"x={int(particle_data.x)} y={int(particle_data.y)}", True, (0,0,0))
    wind.blit(text, (20,20))

    pygame.display.update()