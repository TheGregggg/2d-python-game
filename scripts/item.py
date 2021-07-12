import pygame 
from pygame.locals import *

import json

import gregngine.engine as gregngine

class Item():
	def __init__(self,param):
		"""
		param = {
			"itemRepr" : itemRepr,
			"engine" : engine obj
		}
		"""
	
		self.param = param

		self.engine = param['engine']
		self.param["pixelSize"] = self.engine.param["pixelSize"]
		self.param["scaleMultiplier"] = self.engine.param["scaleMultiplier"]
		self.param['newPixelScale'] = self.engine.param["newPixelScale"]

		if not 'x' in param:
			self.isGrounded = False
			self.x = 0
			self.y = 0
		else:
			self.isGrounded = param['isGrounded']
			self.x = param['x']
			self.y = param['y']


		with open("items/" + param['itemRepr'] + ".json","r") as file:
			self.data = json.load(file)

		self.name = self.data['displayedName']
		
		tilemap = self.data['tilemap']
		self.tilemap = pygame.image.load('assets/sprites/' + self.data["tilemap"]["src"])
		size = self.tilemap.get_size()

		self.tilemapSettings = {
			'start': ((size[0]/tilemap["totalColumns"])*tilemap["colStart"],(size[1]/tilemap["totalRow"])*tilemap["rowStart"]),
			'size': (size[0]/tilemap["totalColumns"],size[1]/tilemap["totalRow"]),
		}
		
		location = (self.tilemapSettings['start'][0], self.tilemapSettings['start'][1])
		self.sprite = self.tilemap.subsurface(pygame.Rect(location, self.tilemapSettings['size']))

		itemScale = (int(self.param['newPixelScale']*tilemap['scaling']/tilemap['ratio']),int(self.param['newPixelScale']*tilemap['scaling']))
		self.groundSprite = pygame.transform.scale(self.sprite,itemScale)

	def drawSprite(self,scale,coords,passThrough):
		tilemap = self.data['tilemap']
		itemScale = (int(coords['width']*scale*tilemap['scaling']/tilemap['ratio']),int(coords['height']*scale*tilemap['scaling']))
		sprite = pygame.transform.scale(self.sprite.convert_alpha(),itemScale)
		if self.data['itemType'] == 'weapon':
			sprite = pygame.transform.rotate(sprite,-45)

		passThrough['window'].blit(sprite, (coords['left']+(tilemap['leftOffset']*scale) , coords['top']+(tilemap['topOffset']*scale)))

	def draw(self, xStart, yStart, passThrough):
		if self.isGrounded:
			xToDraw = self.x - xStart 
			yToDraw = self.y - yStart 

			passThrough['window'].blit(self.groundSprite , (xToDraw*self.param['newPixelScale'], yToDraw*self.param['newPixelScale'] - self.groundSprite.get_height()/4))

	def move(self, dtime):
		pass

	def drawHud(self, xPos, yPos, passThrough):
		pass

	def death(self):
		pass