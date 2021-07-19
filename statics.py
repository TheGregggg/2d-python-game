import pygame 
from pygame.locals import *

actions = {
	"up":     pygame.K_z,
	"down":   pygame.K_s,
	"right":  pygame.K_d,
	"left":   pygame.K_q,
	"sprint": pygame.K_LSHIFT,
	"attack": 'mouse;1',
	"inventory": pygame.K_i,
	"skillTree": pygame.K_TAB,
	"pause": pygame.K_ESCAPE
}

crosshair = {
	'length': 4,
	'gap': 4,
	'width': 4,
}

# Attack Per Sec
weaponTypeAPSMultiplier = {
	'sword': 1,
	'mace': 2
}