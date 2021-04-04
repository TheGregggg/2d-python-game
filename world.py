import pygame 
import pickle5.pickle as pickle

sprites = {
    "player": pygame.image.load("assets/sprites/player.png"),
    "tilemap": pygame.image.load("assets/sprites/characters.png"),
    "g": pygame.image.load("assets/sprites/ground.png"),
    "s": pygame.image.load("assets/sprites/sand.png"),
    "r": pygame.image.load("assets/sprites/rock.png")
}

with open('saves/world.save', 'rb') as f:
    world = pickle.load(f)

with open('saves/walls.save', 'rb') as f:
    walls = pickle.load(f)