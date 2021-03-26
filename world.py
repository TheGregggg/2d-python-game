import pygame 
import pickle5.pickle as pickle

sprites = {
    "player": pygame.image.load("sprites/player.png"),
    "tilemap": pygame.image.load("sprites/characters.png"),
    "g": pygame.image.load("sprites/ground.png"),
    "s": pygame.image.load("sprites/sand.png"),
    "r": pygame.image.load("sprites/rock.png")
}

with open('saves/world.save', 'rb') as f:
    world = pickle.load(f)

with open('saves/walls.save', 'rb') as f:
    walls = pickle.load(f)