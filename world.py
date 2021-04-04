import pygame 
import pickle5.pickle as pickle

tilemaps = {
    "tilemap": pygame.image.load("assets/sprites/characters.png"),
    "overworld": pygame.image.load("assets/sprites/overworld.png")
}

sprites = {
    "g": pygame.image.load("assets/sprites/ground.png"),
    "s": pygame.image.load("assets/sprites/sand.png"),
    "r": pygame.image.load("assets/sprites/rock.png"),
}

def loadSprites(tilemap, pixelSize):
    tilemap = tilemaps[tilemap]
    rows = int(tilemap.get_height() / pixelSize)
    columns = int(tilemap.get_width() / pixelSize)
    a = 0
    for j in range(rows):
        for i in range(columns):
            sprites[a] = tilemap.subsurface(pygame.Rect((i*pixelSize,j*pixelSize), (pixelSize,pixelSize)))
            a += 1

with open('saves/world.save', 'rb') as f:
    world = pickle.load(f)

with open('saves/walls.save', 'rb') as f:
    walls = pickle.load(f)