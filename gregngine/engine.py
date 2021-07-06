# Gregoire Layet
# 23-03-2021
# Grafical and physical 2d engine with pygame

import pygame 
from pygame.locals import *

import gregngine.functions as gFunction

import shelve
import json

import math
import time

class Camera(object):
	def __init__(self, xInit=0, yInit=0, xOffsetInit=0, yOffsetInit=0):
		self.x = xInit
		self.y = yInit
		self.xOffset = xOffsetInit
		self.yOffset = yOffsetInit
		self.attachedTo = None

	def getPos(self):
		"""
		return (x,y)
		"""
		return (self.x + self.xOffset, self.y + self.yOffset)
	
	def move(self,x,y):
		"""
		move by x and y
		"""
		self.x += x
		self.y += y
	
	def setPos(self, x, y):
		"""
		setpos by x and y
		"""
		self.x = x
		self.y = y

class Animator(object):
	def __init__(self,data,param):
		self.tilemap = pygame.image.load('assets/sprites/' + data["tilemap"]["src"])
		size = self.tilemap.get_size()
		tilemap = data["tilemap"]
		self.tilemapSettings = {
			'start': ((size[0]/tilemap["totalColumns"])*tilemap["colStart"],(size[1]/tilemap["totalRow"])*tilemap["rowStart"]),
			'size': (size[0]/tilemap["totalColumns"],size[1]/tilemap["totalRow"]),
			'rows': tilemap["rows"],
			'columns': tilemap["columns"],
			'animation order': tilemap["animation order"]
			}
		self.animationSettings = data["animation"]

		self.pixelSize = param['pixelSize']

		self.lastFrame = time.time()

		self.animation = 'BOTTOM WALK'
		self.lastAnimation = 'BOTTOM WALK'
		self.state = 1
		self.reversed = False
		self.animations = {
			'TOP WALK': [],
			'BOTTOM WALK': [],
			'RIGHT WALK': [],
			'LEFT WALK': [],
		}

		self.getFrames()

	def getFrames(self):
		for j in range(self.tilemapSettings['rows']):
			for i in range(self.tilemapSettings['columns']):
				location = (self.tilemapSettings['start'][0]+self.tilemapSettings['size'][0]*i, self.tilemapSettings['start'][1]+self.tilemapSettings['size'][1]*j)
				anim = self.tilemapSettings['animation order'].get(str(j))
				self.animations[anim].append(self.tilemap.subsurface(pygame.Rect(location, self.tilemapSettings['size'])))
		
		self.sprite = self.animations[self.lastAnimation][self.animationSettings['default state']]
	
	def setFrame(self):
		currentTime = time.time()   
		temps = currentTime-self.lastFrame
		if temps >= self.animationSettings['time']:
			self.lastFrame = currentTime

			if not self.reversed:
				self.state +=1
			else:
				self.state -=1

			if self.state >= self.tilemapSettings['columns']-1:
				self.reversed = True
			elif self.state == 0:
				self.reversed = False

			if self.animation == 'IDLE':
				sprite = self.animations[self.lastAnimation][self.animationSettings['default state']]
			else:
				sprite = self.animations[self.animation][self.state]

			self.sprite = pygame.transform.scale(sprite.convert_alpha(),(self.pixelSize,self.pixelSize))

	def setAnimation(self, animation):
		if self.animation != animation:
			self.lastAnimation = self.animation
			self.animation = animation
			self.state = self.animationSettings['default state']
			self.lastFrame = 0

class Entity(object):
	def __init__(self,param):
		"""
		Entity object 

		param = {
			"name" : x,
			"entityRepr" : y,
			"engine" : engine obj
			"x": 0,
			"y": 0
		}
		"""
		self.param = param
		self.name = param['name']

		self.engine = param['engine']
		self.param["pixelSize"] = self.engine.param["pixelSize"]

		self.x = param['x']
		self.y = param['y']
		self.velocity = {"x": 0, "y": 0}

		self.walls = []
		self.collisions = {}

		self.rect = Rect(0,0,0,0)

		with open("entities/" + param['entityRepr'] + ".json","r") as file:
			self.data = json.load(file)

		self.col = self.data['collider']
		self.colAngleSize = self.col['angleSize']*self.param['pixelSize']

		self.stats = self.data["stats"]
		self.stats["health"] = self.stats["maxHealth"]

		self.lastAttackTime = time.time()
		self.isAttacking = False
		self.atkAnim = {'lastStep':-1,'lastTime':0}

		self.animator = Animator(self.data,param)

	def move(self, dTime):
		x,y = self.velocity['x'],self.velocity['y']
		x,y = x*self.stats["speed"],y*self.stats["speed"]
		x,y = x * dTime * 0.001,y * dTime * 0.001

		self.x += x
		self.y += y

		self.setVelocity(0,0)

	def setVelocity(self,x,y):
		self.velocity = {"x": x, "y": y}

	def setOrientation(self,x,y):
		if abs(x)+0.1 < abs(y) and y < 0:
			self.animator.setAnimation('TOP WALK')
		elif abs(x)+0.1 < abs(y) and y > 0:
			self.animator.setAnimation('BOTTOM WALK')
		elif x < 0 and abs(x)+0.1 > abs(y):
			self.animator.setAnimation('LEFT WALK')
		elif x > 0 and abs(x)+0.1 > abs(y):
			self.animator.setAnimation('RIGHT WALK')
		else:
			self.animator.setAnimation('IDLE')

	def attack(self):
		atkPerSec = self.stats['atkPerSec']
		damage = self.stats['atkDamage']

		currentTime = time.time()   
		if currentTime-self.lastAttackTime >= atkPerSec and not self.isAttacking:
			self.lastAttackTime = currentTime 

			dico = {
				'TOP WALK': 'top',
				'BOTTOM WALK': 'bottom',
				'RIGHT WALK': 'right',
				'LEFT WALK': 'left',
			}

			anim = self.animator.animation if self.animator.animation != 'IDLE' else self.animator.lastAnimation
			lookingTo = dico.get(anim)
			self.atkLookingTo = lookingTo

			attackRect = self.rect

			if lookingTo == 'left':
				attackRect.left -= self.param['pixelSize']
			elif lookingTo == 'right':
				attackRect.left += self.param['pixelSize']
			elif lookingTo == 'top':
				attackRect.top -= self.param['pixelSize']
			elif lookingTo == 'bottom':
				attackRect.top += self.param['pixelSize']

			self.isAttacking = True

			return {'entity':self,'attackRect':attackRect,'damage':damage}

		else:
			return None

	def attackAnimation(self):
		if self.isAttacking:
			t = self.atkAnim['lastTime'] + self.data['animation']['attack']['stepTime']
			if t < time.time():
				self.atkAnim['lastTime'] = time.time()
				self.atkAnim['lastStep'] += 1

			if self.atkAnim['lastStep'] == len(self.data['animation']['attack']['steps']):
				self.isAttacking = False
				self.atkAnim['lastStep'] = -1
				self.atkAnim['lastTime'] = 0

			currentStep = self.data['animation']['attack']['steps'][self.atkAnim['lastStep']]
			animationSurface = pygame.Surface((int(3*self.param['pixelSize']),int(3*self.param['pixelSize'])), pygame.SRCALPHA)

			sprite = self.animator.sprite

			sprite = pygame.transform.rotate(sprite,currentStep['rotation'])

			y = currentStep['y']*self.param['pixelSize']/100
			x = currentStep['x']*self.param['pixelSize']/100

			if self.atkLookingTo == 'top':
				x,y = -y,-x
			elif self.atkLookingTo == 'bottom':
				x,y = y,x
			elif self.atkLookingTo == 'left':
				x = -x
			
			animationSurface.blit(sprite,(self.param['pixelSize']+x,self.param['pixelSize']+y))

			return animationSurface

		return None

	def draw(self, xStart, yStart, passThrough):
		xToDraw = self.x - xStart 
		yToDraw = self.y - yStart

		if not passThrough['isPaused']:
			self.animator.setFrame()

		self.rect = Rect((xToDraw+self.col['offSets']['left'])*self.param['pixelSize'], (yToDraw+self.col['offSets']['top'])*self.param['pixelSize'], self.col['size']['width']*self.param['pixelSize'], self.col['size']['height']*self.param['pixelSize'])
		if passThrough['debug'] == True:
			pygame.draw.rect(self.engine.renderedSurface,(255,0,0),self.rect)

		if not passThrough['isPaused']:
			self.animationSurface = self.attackAnimation()

		if self.data['type'] == 'player':
			self.engine.renderedSurface.blit(self.animator.sprite , (xToDraw*self.param['pixelSize'], yToDraw*self.param['pixelSize']))
		elif self.animationSurface is None:
			self.engine.renderedSurface.blit(self.animator.sprite , (xToDraw*self.param['pixelSize'], yToDraw*self.param['pixelSize']))

		if self.animationSurface is not None:
			self.engine.renderedSurface.blit(self.animationSurface,((xToDraw-1)*self.param['pixelSize'], (yToDraw-1)*self.param['pixelSize']))

	def drawHud(self, xPos, yPos, passThrough):
		if passThrough['currentHUD'] == 'main':
			scale = passThrough['HudScale']

			xToDraw = (self.x - xPos)*self.param['pixelSize'] * self.engine.renderedWidthAndHeightRatios[0]
			yToDraw = (self.y - yPos)*self.param['pixelSize'] * self.engine.renderedWidthAndHeightRatios[1]

			value = ((self.stats["health"] * 100) / self.stats["maxHealth"]) / 100 if self.stats["health"] > 0 else 0

			if self.stats["health"] < self.stats["maxHealth"]:
				rect = gFunction.createRectOutlined(value,xToDraw,yToDraw,100,20,6)
				pygame.draw.rect(self.engine.HUDSurface,(0,0,0),rect[0])
				pygame.draw.rect(self.engine.HUDSurface,(255,0,0),rect[1])

	def death(self):
		pass

class EntitiesManager(object):
	def __init__(self):
		self.entities = []
		self.visibleEntities = []

	def addEntity(self,entity):
		self.entities.append(entity)

	def getVisibleEntities(self,coords):
		self.visibleEntities = []
		for entity in self.entities:
			if entity.x >= coords['xStart']-1 and entity.x <= coords['xEnd'] and entity.y >= coords['yStart']-1 and entity.y <= coords['yEnd']:
				self.visibleEntities.append(entity)

	def killEntity(self,ent):
		for entity in self.entities:
			if entity == ent:
				entity.death()
				self.entities.remove(entity)

class HUDMenuManager(object):
	def __init__(self,engine,hudScale):
		self.engine = engine
		self.hudScale = hudScale

		self.huds = {}

	def drawHud(self,passThrough):
		f = self.huds.get(passThrough['currentHUD'])
		if f is not None:
			f['fonction'](passThrough)
	
class Engine(object):
	def __init__(self,param):
		"""
		Principal engine class

		engine do each frame this loop:
			- transmit input
			- apply physical changes
			- call drawWorld function
			- Draw all visible entities
			- Draw all HUD

		param = {
				"width" : 1200,
				"height" : 800,
				"saves": "saves",
				"pixelSize": 16,
				"scaleMultiplier": 6,
				"aspectRatio": [16,9],
				"HudScale": 2,
				"debug": false
			}
		"""
		pygame.init()

		self.param = param
		self.debugMode = param["debug"]

		self.states = {								# states for the engine, in relation with the currentHUD, match hud page with the game state
			'play': [],								# pause -> the game will not call the entities .draw() methods 
			'pause': []
		}

		self.window = pygame.display.set_mode((param["width"], param["height"]),RESIZABLE)

		self.renderedSurface = pygame.Surface((param['aspectRatio'][0]*param["pixelSize"],param['aspectRatio'][1]*param["pixelSize"]))
		self.getRenderedWidthAndHeight()

		self.HUDSurface = pygame.Surface(self.renderedWidthAndHeight, pygame.SRCALPHA)

		self.mainCamera = Camera()

		self.savePath = param["saves"]

		self.entitiesManager = EntitiesManager()

		self.currentHUD = 'main'
		self.HUDMenuManager = HUDMenuManager(self,param['HudScale'])

		#self.loadSaves() load save done in game.py to ensure there is a save file
		self.clock = pygame.time.Clock()
		self.clockTick = 120
		self.font = pygame.font.SysFont("Arial", 18)
	
	def getRenderedWidthAndHeight(self):
		width, height = self.param["width"], self.param["height"]
		xOffsets, yOffsets = 0, 0

		if self.param["width"]/self.param['aspectRatio'][0]  >  self.param["height"]/self.param['aspectRatio'][1]:
			width = int( (self.param["height"] / self.param['aspectRatio'][1]) * self.param['aspectRatio'][0])
			xOffsets = (self.param["width"] - width)/2
		else:
			height = int( (self.param["width"] / self.param['aspectRatio'][0]) * self.param['aspectRatio'][1])
			yOffsets = (self.param["height"] - height)/2
		
		self.renderedWidthAndHeight = (width, height)
		self.renderedWidthAndHeightRatios = (width/(self.param['aspectRatio'][0]*self.param["pixelSize"]) ,height/(self.param['aspectRatio'][1]*self.param["pixelSize"]))
		self.renderedDisplayOffsets = (xOffsets, yOffsets)

	def loadSaves(self):
		with shelve.open(self.savePath + "/saves") as data:
			if 'miscs' in data:
				if 'windowsHeight' in data['miscs'] and 'windowsWidth' in data['miscs']:
					self.rezizeWindow(data['miscs']['windowsHeight'],data['miscs']['windowsWidth'],False)
			else:
				data['miscs'] = {}

	def rezizeWindow(self,h,w,saveData=True):
		self.window = pygame.display.set_mode((w, h),RESIZABLE)
		self.param['height'] = h
		self.param['width'] = w
		self.getRenderedWidthAndHeight()
		self.HUDSurface = pygame.Surface(self.renderedWidthAndHeight, pygame.SRCALPHA)

		if saveData:
			with shelve.open(self.savePath + "/saves") as data:
				dictio = data['miscs']
				dictio['windowsHeight'] = h
				dictio['windowsWidth'] = w
				data['miscs'] = dictio

	def getTilesOnScreen(self):
		CameraPosX, CameraPosY = self.mainCamera.getPos()
		
		xStart = math.floor(CameraPosX) - int((self.param['aspectRatio'][0]+1)/2 - 0.5)
		yStart = math.floor(CameraPosY) - int((self.param['aspectRatio'][1]+1)/2 - 0.5)

		xEnd = xStart + self.param['aspectRatio'][0] + 2
		yEnd = yStart + self.param['aspectRatio'][1] + 2

		widthOffset = round(self.param['aspectRatio'][0]*self.param['pixelSize'] - self.renderedSurface.get_width(),2)/self.param['pixelSize']/2
		heightOffset = round(self.param['aspectRatio'][1]*self.param['pixelSize'] - self.renderedSurface.get_height(),2)/self.param['pixelSize']/2

		offx = round(CameraPosX - math.floor(CameraPosX),3) + 0.25 #+ widthOffset
		offy = round(CameraPosY - math.floor(CameraPosY),3) #+ heightOffset

		dic = {
			"yStart":yStart,
			"yEnd":yEnd,
			"xStart":xStart,
			"xEnd":xEnd,
			"offx": offx,
			"offy": offy,
			"widthOffset": widthOffset,
			"heightOffset": heightOffset
		}

		self.ScreenToWorldCoords = dic

	def engineLoop(self):
		active = True
		while active:

			self.mousePosClick = None
			self.mouseButtonClick = None

			inputEvent = pygame.event.get()
			for event in inputEvent:
				if event.type == QUIT:
					pygame.quit()
					quit()
				if event.type == VIDEORESIZE:
					self.rezizeWindow(event.h,event.w)
				if event.type == pygame.MOUSEBUTTONDOWN:
					mousePosTuple = pygame.mouse.get_pos()
					self.mousePosClick = [0,0]
					self.mousePosClick[0] = mousePosTuple[0] - self.renderedDisplayOffsets[0]
					self.mousePosClick[1] = mousePosTuple[1] - self.renderedDisplayOffsets[1]
					self.mouseButtonClick = pygame.mouse.get_pressed()
			
			self.main(inputEvent, pygame.key.get_pressed())

			self.applyPhysicalChanges(self.clock.get_time())

			self.Draws()

			self.DrawHUDs()

			pygame.display.update()
			self.clock.tick()
			#self.clock.tick(self.clockTick)

	def main(self,inputEvent,inputPressed):
		pass

	def applyPhysicalChanges(self,deltaTime):
		for entitie in self.entitiesManager.entities:
			if entitie.data['type'] == 'monster':
				if entitie.stats['health'] <= 0:
					self.entitiesManager.killEntity(entitie)
			entitie.move(self.clock.get_time())

	def Draws(self):
		self.getTilesOnScreen()
		self.DrawWorld()

		coords = self.ScreenToWorldCoords

		entities = self.entitiesManager.visibleEntities
		entities = sorted(entities, key=lambda ent: ent.y-1 if ent.data['type'] == 'item' else ent.y )

		isPaused = self.currentHUD in self.states['pause']

		for entitie in entities:
			entitie.draw(coords['xStart']+coords['offx'],coords['yStart']+coords['offy'],{'debug':self.debugMode,'window':self.window,'isPaused':isPaused})

		scaledRenderedSurface = pygame.transform.scale(self.renderedSurface, self.renderedWidthAndHeight)
		self.window.blit(scaledRenderedSurface, self.renderedDisplayOffsets)
		fps = str(int(self.clock.get_fps()))
		fps_text = self.font.render(fps, 1, (255,255,255))
		self.window.blit(fps_text, (0, 0))
	
	def DrawWorld(self):
		self.renderedSurface.fill((0,0,0))
		self.window.fill((0,0,0)) 
		self.entitiesManager.getVisibleEntities(self.ScreenToWorldCoords)

	def DrawHUDs(self):
		self.HUDSurface.fill((0,0,0,0))

		coords = self.ScreenToWorldCoords
		visibleEnt = self.entitiesManager.visibleEntities
		mousePosTuple = pygame.mouse.get_pos()
		mousePos = [0,0]
		mousePos[0] = mousePosTuple[0] - self.renderedDisplayOffsets[0]
		mousePos[1] = mousePosTuple[1] - self.renderedDisplayOffsets[1]

		passThrough = {
			"window": self.window,
			"HudScale": self.param['HudScale'],
			"currentHUD": self.currentHUD,
			"mousePos": mousePos,
			"mousePosClick": self.mousePosClick,
			"mouseButtonClick": self.mouseButtonClick,
			"visibleEntities": visibleEnt
		}

		self.HUDMenuManager.drawHud(passThrough)

		for entitie in visibleEnt:
			entitie.drawHud((coords['xStart']+coords['offx']),(coords['yStart']+coords['offy']),passThrough)

		self.window.blit(self.HUDSurface,  self.renderedDisplayOffsets)
