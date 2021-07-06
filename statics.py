import pygame 
from pygame.locals import *

actions = {
	"up":     pygame.K_z,
	"down":   pygame.K_s,
	"right":  pygame.K_d,
	"left":   pygame.K_q,
	"sprint": pygame.K_LSHIFT,
	"attack": pygame.K_SPACE,
	"inventory": pygame.K_i,
	"skillTree": pygame.K_TAB,
	"pause": pygame.K_ESCAPE
}

# Attack Per Sec
weaponTypeAPSMultiplier = {
	'sword': 1,
	'mace': 2
}