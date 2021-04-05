import gregngine.engine as gregngine
import gregngine.functions as gFunction

import world

import math
import time

import shelve
import json

import pygame 
from pygame.locals import *

actions = {
	"up":     pygame.K_w,
	"down":   pygame.K_s,
	"right":  pygame.K_d,
	"left":   pygame.K_a,
	"sprint": pygame.K_LSHIFT,
	"menu": pygame.K_e,
	"pause": pygame.K_ESCAPE
}

class HUDMenuManager(gregngine.HUDMenuManager):
	def __init__(self,engine,hudScale):
		super().__init__(engine,hudScale)

		self.pauseMenuIsOpen = False

		self.param = {
			'margin': 5,
			'fontSize': 20,
			'padding': {
				'height': 6,
				'width': 10
			},
			'radius': 10,
			'alpha': {
				'normal': 50,
				'hover': 150
			},
			'color': (255,255,255,255)
		}

		self.font = pygame.font.Font('./assets/fonts/Pixel Digivolve.otf', self.param['fontSize']*self.hudScale)

		self.huds = {
			"menu": {
				'fonction': self.menu,
				'isOpen': False
			},
			"pauseMenu": {
				'fonction': self.pauseMenu,
				'isOpen': False,
				'buttons': [
					{
						'text': 'retour',
						'fonction': self.btnResume
					},
					{
						'text': 'sauvegarder',
						'fonction': self.btnSave
					},
					{
						'text': 'options',
						'fonction': self.btnOptions
					},
					{
						'text': 'quitter',
						'fonction': self.btnQuit
					}
				]
			}
		}
	
	def menu(self, passThrough):
		print("wsh")
	
	def pauseMenu(self, passThrough):
		screenWidth, screenHeight = passThrough['window'].get_size()

		background = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
		background.fill((0,0,0,75))
		passThrough['window'].blit(background, (0,0))

		scale = self.hudScale
		
		imgWidth, imgHeight = self.font.size('h')
		imgHeight += self.param['padding']['height']*2*scale
		topHeight = len(self.huds["pauseMenu"]['buttons'])*(imgHeight+self.param['margin']*scale)
		top = int(screenHeight/2 - topHeight/2)

		self.mousePos = pygame.mouse.get_pos()

		btns = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)

		for button in self.huds["pauseMenu"]['buttons']:
			height = self.drawButton(button,'centered',top,passThrough,btns)
			top += height*scale

		passThrough['window'].blit(btns, (0,0))

	def drawButton(self,button,rectLeft,rectTop,passThrough,btns):
		scale = self.hudScale

		color = button['color'] if 'color' in button else self.param['color']
		img = self.font.render(button['text'], False, color)

		rectHeight = img.get_height() + self.param['padding']['height']*2*scale
		rectWidth = img.get_width() + self.param['padding']['width']*2*scale

		imgLeft = int(passThrough['window'].get_width()/2 - img.get_width()/2) + scale
		imgTop = int(rectTop + rectHeight/2  - img.get_height()/2) - scale

		if rectLeft == 'centered':
			rectLeft = int(passThrough['window'].get_width()/2 - rectWidth/2)

		collisionRect = Rect((rectLeft,rectTop),(int(rectWidth),int(rectHeight)))
		
		isHover = collisionRect.collidepoint(self.mousePos)
		alpha = self.param['alpha']['hover'] if isHover else self.param['alpha']['normal']

		rects, circles = gFunction.createRectWithRoundCorner(rectLeft,rectTop,rectWidth,rectHeight,self.param['radius'])
		for rect in rects:
			pygame.draw.rect(btns,(0,0,0,alpha),Rect(rect))
		for circle in circles:
			pygame.draw.circle(btns,(0,0,0,alpha),circle,self.param['radius'])
		
		btns.blit(img,(imgLeft, imgTop))

		# handle click requests
		if passThrough['mousePosClick'] is not None:
			if collisionRect.collidepoint(passThrough['mousePosClick']):
				button['fonction']()
		return int(rectHeight/2 + self.param['margin'])
	
	def btnResume(self):
		self.huds['pauseMenu']['isOpen'] = False
		self.engine.currentHUD = 'main'

	def btnSave(self):
		print('Save')

	def btnOptions(self):
		print('Options')

	def btnQuit(self):
		print('Quit')

class Player(gregngine.Entity):
	def __init__(self, param):
		super().__init__(param)
		self.parent = None

		self.speed = 1
		self.running = False

		self.camera = None

	def move(self,dTime):
		x,y = self.velocity['x'],self.velocity['y']

		if self.running:
			x,y = x*2,y*2
		else:
			x,y = x,y

		self.x += x
		self.y += y

		self.camera.move(x,y)

		self.setVelocity(0,0)

	def setCameraOffset(self,x,y):
		self.camera.xOffset = -(x/2) + self.param['x']
		self.camera.yOffset = -(y/2) + self.param['y']

	def draw(self, xStart, yStart, passThrough):
		#uper().draw(xStart, yStart, passThrough)
		pass

class Engine(gregngine.Engine):
	def __init__(self, param):
		super().__init__(param)

		self.world = world
		self.world.loadSprites('overworld',self.param['pixelSize'])

		self.spriteToPlace = 0

		self.newPixelScale = self.param['newPixelScale']
		
		self.HUDMenuManager = HUDMenuManager(self,self.param['HudScale'])
		self.states['play'] = ['main','inventory']
		self.states['pause'] = ['pauseMenu']

		self.rezizeSprites()

		pygame.key.set_repeat(1,20)

		playerParam = {
			"name" : 'player',
			"entityRepr" : 'player',
			"pixelSize": self.param['pixelSize'],
			"scaleMultiplier": self.param['scaleMultiplier'],
			'x':6,
			'y':6}
		self.player = Player(playerParam)
		self.player.parent = self
		self.player.camera = self.mainCamera
		self.mainCamera.setPos(0,0)

		#self.loadSaves()

		self.entitiesManager.addEntity(self.player)

		self.clockTick = 10

	def rezizeSprites(self):
		for sprite in self.world.sprites:
			self.world.sprites[sprite] = pygame.transform.scale(self.world.sprites[sprite].convert_alpha(),(self.newPixelScale,self.newPixelScale))

	def main(self,inputEvent,inputPressed):
		if self.currentHUD in self.states['play']:
			self.playerInputMouvement(inputEvent,inputPressed)
			self.placeSprite()

		self.playerInputMenus(inputEvent,inputPressed)

	def playerInputMouvement(self,inputEvent,inputPressed):
		playerSpeedY,playerSpeedX = 0, 0

		if inputPressed[actions["sprint"]]:
			self.player.running = True
		else:
			self.player.running = False

		if inputPressed[actions["up"]]:
			playerSpeedY -= 1

		if inputPressed[actions["down"]]:
			playerSpeedY += 1

		if inputPressed[actions["left"]]:
			playerSpeedX -= 1

		if inputPressed[actions["right"]]:
			playerSpeedX += 1

		if playerSpeedX != 0 or playerSpeedY != 0:
			self.player.setVelocity(playerSpeedX, playerSpeedY)

	def playerInputMenus(self,inputEvent,inputPressed):
		
		menuPressed = False
		pausePressed = False

		for event in inputEvent:
			if event.type == pygame.KEYDOWN:
				if event.key==actions["menu"]:
					menuPressed = True
				if event.key==actions["pause"]:
					pausePressed = True

		# inventory code
		"""if inventoryPressed:
			#self.player.inventory()
			if not self.player.inventory.isOpen:
				self.player.inventory.isOpen = True
				self.currentHUD = 'inventory'
			else:
				self.player.inventory.isOpen = False
				self.currentHUD = 'main'"""
		
		if menuPressed:
			#self.player.inventory()
			if not self.HUDMenuManager.huds['menu']['isOpen']:
				self.HUDMenuManager.huds['menu']['isOpen'] = True
				self.currentHUD = 'menu'
			else:
				self.HUDMenuManager.huds['menu']['isOpen'] = False
				self.currentHUD = 'main'

		# pause menu code
		if pausePressed:
			#self.player.inventory()
			if not self.HUDMenuManager.huds['pauseMenu']['isOpen']:
				self.HUDMenuManager.huds['pauseMenu']['isOpen'] = True
				self.currentHUD = 'pauseMenu'
			else:
				self.HUDMenuManager.huds['pauseMenu']['isOpen'] = False
				self.currentHUD = 'main'

	def placeSprite(self):
		if pygame.mouse.get_pos() and pygame.mouse.get_pressed()[0]:
			self.getTilesOnScreen()
			coords = self.ScreenToWorldCoords
			size = self.newPixelScale
			x, y = pygame.mouse.get_pos()
			x = int((x + ((coords['xStart']+ coords['offx']) * size))// size)
			y = int((y + ((coords['yStart']+ coords['offy']) * size))// size)
			
			world.world[y][x] = self.spriteToPlace

	def DrawWorld(self):
		super().DrawWorld()

		widthBy2 = self.param['width']/2
		heightBy2 = self.param['height']/2

		coords = self.ScreenToWorldCoords

		for y_index,y in enumerate(self.world.world[coords['yStart']:coords['yEnd']]):
			for x_index,x in enumerate(y[coords['xStart']:coords['xEnd']]):
				coord = ((x_index*self.newPixelScale)-(coords['offx']*self.newPixelScale) , (y_index*self.newPixelScale)-(coords['offy']*self.newPixelScale))
				
				sprite = self.world.sprites[x]

				wall = self.world.walls[coords['yStart']+y_index][coords['xStart']+x_index]
				if wall == " ":
					self.window.blit(sprite, coord)

				else:
					self.window.blits(((sprite, coord),(self.world.sprites[wall], coord)))
		
if __name__ == "__main__":
	engineParameters = {
		"height" : 800,
		"width" : 1200,
		"saves": "saves/saves",
		"pixelSize": 16,
		"scaleMultiplier": 4,
		"HudScale": 2,
		"debug": False
	}

	engine = Engine(engineParameters)
	engine.engineLoop()