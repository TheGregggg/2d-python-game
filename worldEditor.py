import gregngine.engine as gregngine
import gregngine.functions as gFunction

import world

import math
import time

import shelve
import json
import copy

import pygame 
from pygame.locals import *

actions = {
	"up":     pygame.K_z,
	"down":   pygame.K_s,
	"right":  pygame.K_d,
	"left":   pygame.K_q,
	"sprint": pygame.K_LSHIFT,
	"switchLayer": pygame.K_SPACE,
	"menu": pygame.K_e,
	"pause": pygame.K_ESCAPE,
	"rewind": pygame.K_a,
}

class HUDMenuManager(gregngine.HUDMenuManager):
	def __init__(self,engine,hudScale):
		super().__init__(engine,hudScale)

		self.pauseMenuIsOpen = False

		self.param = {
			'margin': 0,
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
				'isOpen': False,
				'rightClick': {
					"start":{
						"x": None,
						"y": None,
					},
					"end":{
						"x": None,
						"y": None,
					}
				}
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
					#{
					#	'text': 'options',
					#	'fonction': self.btnOptions
					#},
					{
						'text': 'quitter',
						'fonction': self.btnQuit
					}
				]
			}
		}
	
	def menu(self, passThrough):
		screenWidth, screenHeight = passThrough['window'].get_size()

		size = self.engine.world.tilemaps['overworld'].get_size()
		size = size[0]*self.hudScale, size[1]*self.hudScale
		tilemap = pygame.transform.scale(self.engine.world.tilemaps['overworld'],size)

		background = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
		background.fill((0,0,0,200))
		passThrough['window'].blit(background, (0,0))


		place = screenWidth/2 - size[0]/2, screenHeight/2 - size[1]/2
		passThrough['window'].blit(tilemap,place)

		if passThrough['mousePosClick'] is not None:
			if place[0] < passThrough['mousePosClick'][0] < place[0]+size[0] and place[1] < passThrough['mousePosClick'][1] < place[1]+size[1]:
				if passThrough['mouseButtonClick'][0]:
					x = passThrough['mousePosClick'][0] - place[0] 
					x = x//(self.engine.world.tilemaps['overworld'].get_width()/self.engine.param['pixelSize']*self.hudScale)

					y = passThrough['mousePosClick'][1] - place[1] 
					y = y//(self.engine.world.tilemaps['overworld'].get_height()/self.engine.param['pixelSize']*self.hudScale)
					
					#print(x,y,(y*self.engine.world.tilemaps['overworld'].get_height()/self.engine.param['pixelSize'])+x)
					sprite = int((y*self.engine.world.tilemaps['overworld'].get_height()/self.engine.param['pixelSize'])+x)
					size = {'y':len(self.engine.spriteToPlace),'x':len(self.engine.spriteToPlace[0])}

					self.engine.setSprite(sprite,size)
					self.closeMenu()

				elif passThrough['mouseButtonClick'][2]:
					x = passThrough['mousePosClick'][0] - place[0] 
					x = int(x//(self.engine.world.tilemaps['overworld'].get_width()/self.engine.param['pixelSize']*self.hudScale))
					y = passThrough['mousePosClick'][1] - place[1] 
					y = int(y//(self.engine.world.tilemaps['overworld'].get_height()/self.engine.param['pixelSize']*self.hudScale))

					rightClick = self.huds['menu']['rightClick']

					if rightClick["start"]["x"] is None: 		# if it's first right click
						rightClick["start"] = {'x':x,'y':y}
					else:
						rightClick["end"] = {'x':x,'y':y}
					
					
					if rightClick["end"]["x"] is not None:  # if both click as been register
						sprites = []
						for i in range(rightClick["start"]["y"],rightClick["end"]["y"]+1):
							a = []
							for j in range(rightClick["start"]["x"],rightClick["end"]["x"]+1):
								a.append(int((i*self.engine.world.tilemaps['overworld'].get_height()/self.engine.param['pixelSize'])+j))

							sprites.append(a)

						self.engine.setSprite(sprites,{'x':len(sprites[0]),'y':len(sprites)})
						self.closeMenu()
				
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
	
	def closeMenu(self):
		self.huds['menu']['isOpen'] = False
		self.huds['menu']['rightClick'] = {"start":{"x": None,"y": None,},"end":{"x": None,"y": None,}}
		self.engine.currentHUD = 'main'

	def btnResume(self):
		self.huds['pauseMenu']['isOpen'] = False
		self.engine.currentHUD = 'main'

	def btnSave(self):
		self.engine.world.savesWorld(self.engine.world.world,self.engine.world.walls)
		print('Save')

	def btnOptions(self):
		print('Options')

	def btnQuit(self):
		pygame.quit()
		quit()

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

		self.lastState = {
			'world': copy.deepcopy(self.world.world),
			'walls': copy.deepcopy(self.world.walls)}

		self.spriteToPlace = [[0]]
		self.layer = 'ground'

		self.newPixelScale = self.param['newPixelScale']
		
		self.HUDMenuManager = HUDMenuManager(self,self.param['HudScale'])
		self.states['play'] = ['main','inventory']
		self.states['pause'] = ['pauseMenu']

		self.rezizeSprites()

		#pygame.key.set_repeat(1,20)

		playerParam = {
			"name" : 'player',
			"entityRepr" : 'player',
			"engine": self,
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
			if inputPressed[actions["rewind"]]:
				self.world.world = copy.deepcopy(self.lastState['world'])
				self.world.walls = copy.deepcopy(self.lastState['walls'])

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
				if event.key==actions["switchLayer"]:
					if self.layer == 'ground':
						self.layer = 'walls'
					else:
						self.layer = 'ground'
			if event.type == MOUSEWHEEL:
				size = len(self.spriteToPlace)
				if size%2 == 0:
					size -=1
				if event.y < 0:
					if size >= 3:
						size -= 2
				else:
					size += 2
				self.setSprite(self.spriteToPlace[0][0],{'x':size,'y':size})

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

	def setSprite(self,tile,size):
		if type(tile) is int:
			self.spriteToPlace = []
			for i in range(size['y']):
				a = []
				for j in range(size['x']):
					a.append(tile)
				self.spriteToPlace.append(a)
		elif type(tile) is list:
			self.spriteToPlace = tile

	def placeSprite(self):
		if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
			self.lastState['world'] = copy.deepcopy(self.world.world)
			self.lastState['walls'] = copy.deepcopy(self.world.walls)
			self.getTilesOnScreen()
			coords = self.ScreenToWorldCoords
			size = self.newPixelScale
			x, y = pygame.mouse.get_pos()
			x = int((x + ((coords['xStart']+ coords['offx']) * size))// size)
			y = int((y + ((coords['yStart']+ coords['offy']) * size))// size)

			x_start = x - math.floor(len(self.spriteToPlace)/2)
			x_end = x + math.floor(len(self.spriteToPlace)/2)
			if len(self.spriteToPlace) % 2 != 0:
				x_end += 1
			
			y_start = y - math.floor(len(self.spriteToPlace[0])/2)
			y_end = y + math.floor(len(self.spriteToPlace[0])/2)
			if len(self.spriteToPlace[0]) % 2 != 0:
				y_end += 1

			world = self.world.walls
			if self.layer == 'ground':
				world = self.world.world

			for i_index,i in enumerate(range(y_start,y_end)):  # y
				for j_index,j in enumerate(range(x_start,x_end)): # x
					try:
						if pygame.mouse.get_pressed()[0]:
							world[i][j] = self.spriteToPlace[i_index][j_index]
						elif pygame.mouse.get_pressed()[2] and self.layer != 'ground':
							world[i][j] = ' '
					except Exception as e:
						print(e)

	def drawCurrentSprite(self):
		self.getTilesOnScreen()
		coords = self.ScreenToWorldCoords
		size = self.newPixelScale
		x, y = pygame.mouse.get_pos()

		x = math.floor((x // size)* size)
		y = math.floor((y // size)* size) 

		x -= coords['widthOffset']* size
		y -= coords['heightOffset']* size
		
		return (x,y)

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
		
		currentSpriteToDrawCoord = self.drawCurrentSprite()
		self.window.blit(self.world.sprites[self.spriteToPlace[0][0]],currentSpriteToDrawCoord)
		
		
		if self.layer == 'ground':
			color = (0,80,255)
		else:
			color = (255,80,0)
		size = len(self.spriteToPlace)
		pygame.draw.rect(self.window,color,Rect(10*self.param['HudScale'],10*self.param['HudScale'],size*5*self.param['HudScale'],size*5*self.param['HudScale']))

if __name__ == "__main__":
	engineParameters = {
		"height" : 800,
		"width" : 1200,
		"saves": "saves/saves",
		"pixelSize": 16,
		"scaleMultiplier": 4,
		"HudScale": 3,
		"debug": False
	}

	engine = Engine(engineParameters)
	engine.engineLoop()