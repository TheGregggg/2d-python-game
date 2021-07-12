import gregngine.engine as gregngine
import gregngine.functions as gFunction

import world

import math
import random
import time
import os

import shelve
import json
import pickle5.pickle as pickle

import pygame 
from pygame.locals import *

from statics import *

#player scirpts import
from scripts.player.Player import *
from scripts.player.Inventory import *
from scripts.player.SkillTree import *

# other scripts import
from scripts.HUDMenuManager import *
from scripts.Item import *
from scripts.Entity import *

from scripts.ParticleSystem import *

class Engine(gregngine.Engine):
	def __init__(self, param):
		super().__init__(param)

		pygame.mouse.set_visible(False)

		self.world = world
		self.world.loadSprites('overworld',self.param['pixelSize'])
		self.newPixelScale = self.param['newPixelScale']
		
		self.HUDMenuManager = HUDMenuManager(self,self.param['HudScale'])
		self.states['start'] = ['startMenu']
		self.states['play'] = ['main','inventory','skillTree']
		self.states['pause'] = ['pauseMenu']
		self.currentHUD = 'startMenu'

		self.collisionsDistance = 1.5
		self.collisionsDistance *= self.newPixelScale
		self.collisions = {}

		self.damagesInfos = []

		self.rezizeSprites()

	def rezizeSprites(self):
		for sprite in self.world.sprites:
			self.world.sprites[sprite] = pygame.transform.scale(self.world.sprites[sprite].convert_alpha(),(self.newPixelScale,self.newPixelScale))

	def loadScreenSaves(self):
		super().loadSaves()

	def loadSaves(self):
		if not os.path.exists(self.savePath + "/data.save"):
			return False

		with open(self.savePath + "/data.save", 'rb') as f:
			data = pickle.load(f)

			playerParam = {
				"name" : 'player',
				"entityRepr" : 'player',
				"engine": self}
			playerParam['x'],playerParam['y'] = data['playerPos']
			self.player = Player(playerParam)
			self.player.initPostParent()
			self.player.camera = self.mainCamera
			self.mainCamera.setPos(0,0)

			self.player.data = data['playerData']
			self.player.stats = self.player.data['stats']
			self.player.skillTree.skills = self.player.data['skillTree']['skills']
			self.player.applyNewStats()
			self.player.applyExpFromLevel()

			self.player.inventory.hands = None if data['playerInv']['hands'] is None else Item({'itemRepr': data['playerInv']['hands'], "engine": self})
			self.player.inventory.handsStack = data['playerInv']['handsStack']

			self.player.inventory.slots = []
			for row in data['playerInv']['slots']:
				r = []
				for col in row:
					if col is not None:
						r.append(Item({'itemRepr': col, "engine": self}))
					else:
						r.append(None)
				self.player.inventory.slots.append(r)

			self.player.inventory.stacks = data['playerInv']['stacks']

			self.player.animator.lastAnimation = data['playerOrientation']
			self.player.animator.animation = data['playerOrientation']
			self.entitiesManager.addEntity(self.player)

			namesUsed = []
			for entitie in data['entities']:
				param = {
					"engine": self,
					"x": entitie['x'],
					"y": entitie['y']
				}
				ent = None
				if entitie['type'] == 'entitie':
					name = f"{entitie['repr']}-{gFunction.generateRandomString(10)}"
					while name in namesUsed:
						name = f"{entitie['repr']}-{gFunction.generateRandomString(10)}"
					namesUsed.append(name)

					param["name"] = name
					param["entityRepr"] = entitie['repr']
					ent = Entity(param)
					ent.stats = entitie['stats']

				if entitie['type'] == 'item':
					param["itemRepr"] = entitie['repr']
					param["isGrounded"] = True
					ent = Item(param)
					
				self.entitiesManager.addEntity(ent)

		print('data loaded')
		return True

	def saveGame(self):
		with open(self.savePath + '/data.save', 'wb') as f:
			data = {}
			
			data['playerPos'] = (self.player.x,self.player.y)
			data['playerOrientation'] = self.player.animator.lastAnimation

			data['playerInv'] = {}
			data['playerInv']['hands'] = None if self.player.inventory.hands is None else self.player.inventory.hands.data['name']
			data['playerInv']['handsStack'] = self.player.inventory.handsStack
			data['playerInv']['slots'] = []
			for row in self.player.inventory.slots:
				r = []
				for col in row:
					if col is not None:
						r.append(col.data['name'])
					else:
						r.append(None)
				data['playerInv']['slots'].append(r)

			data['playerInv']['stacks'] = self.player.inventory.stacks
			data['playerData'] = self.player.data
			data['playerData']['skillTree']['skills'] = self.player.skillTree.skills

			data['entities'] = []
			for entitie in self.entitiesManager.entities:
				dico = {}
				if 'entityRepr' in entitie.param and entitie.param['entityRepr'] == 'player':
					continue 

				if 'entityRepr' in entitie.param and entitie.param['entityRepr'] != 'player':
					dico['type'] = 'entitie'
					dico['repr'] = entitie.param['entityRepr']
					dico['stats'] = entitie.stats

				elif 'itemRepr' in entitie.param:
					dico['type'] = 'item'
					dico['repr'] = entitie.param['itemRepr']

				dico['x'], dico['y'] = entitie.x, entitie.y
				data['entities'].append(dico)

			pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

		print('Save')

	def loadGame(self):
		savesLoaded = self.loadSaves()
		#savesLoaded = False
		
		if not savesLoaded:
			print('load init')
			playerParam = {
				"name" : 'player',
				"entityRepr" : 'player',
				"engine": self,
				'x':6,
				'y':6}
			self.player = Player(playerParam)
			self.player.initPostParent()
			self.player.camera = self.mainCamera
			self.mainCamera.setPos(0,0)

			self.entitiesManager.addEntity(self.player)

			sword   = Item({'itemRepr':'normal_sword', "engine": self,'x':10,'y':6,'isGrounded':True})
			mace    = Item({'itemRepr':'normal_mace' , "engine": self,'x':11,'y':6,'isGrounded':True})
			bread   = Item({'itemRepr':'bread' , "engine": self,'x':11,'y':7,'isGrounded':True})
			bread2  = Item({'itemRepr':'bread' , "engine": self,'x':11,'y':7,'isGrounded':True})
			bread3  = Item({'itemRepr':'bread' , "engine": self,'x':11,'y':7,'isGrounded':True})

			self.entitiesManager.addEntity(sword)
			self.entitiesManager.addEntity(bread)
			self.entitiesManager.addEntity(bread2)
			self.entitiesManager.addEntity(bread3)

			self.entitiesManager.addEntity(Entity({"name" : "slim1","entityRepr" : "slim", "engine": self,'x':9,'y':10}))
		
		self.loadScreenSaves()

	def main(self,inputEvent,inputPressed):
		if self.currentHUD in self.states['play']:
			self.checkCollision()
			self.playerInputMouvement(inputEvent,inputPressed)

			for entity in self.entitiesManager.visibleEntities:
				if entity.data['type'] == 'monster':
					walls = entity.walls
					adj = entity.x - self.player.x
					opo = entity.y - self.player.y
					hypo = math.sqrt(adj**2 + opo**2)

					if hypo < 0.7:
						attackinfo = entity.attack()
						if attackinfo is not None:
							self.damagesInfos.append(attackinfo)
					
					if not entity.isAttacking:
						coef = 1/hypo
						x = -adj * coef
						y = -opo * coef

						entity.setOrientation(x,y)
						
						if x > 0 and "Right" in walls:
							x *= 0
						if x < 0 and "Left" in walls:
							x *= 0
						if y > 0 and "Bottom" in walls:
							y *= 0
						if y < 0 and "Top" in walls:
							y *= 0

						entity.setVelocity(x,y)
			
			self.applyDamages()
		
		if self.currentHUD not in self.states['start']:
			self.playerInputMenus(inputEvent,inputPressed)

	def playerInputMouvement(self,inputEvent,inputPressed):
		playerSpeedY,playerSpeedX = 0, 0
		playerMouvY,playerMouvX = 0, 0

		walls = self.player.walls

		if inputPressed[actions["sprint"]]:
			self.player.running = True
			if self.player.stats['energy'] > 0:
				self.player.animator.animationSettings['time'] = self.player.animator.animationSettings['maxSpeed']
			else:
				self.player.animator.animationSettings['time'] = self.player.animator.animationSettings['normalSpeed']
		else:
			self.player.running = False
			self.player.animator.animationSettings['time'] = self.player.animator.animationSettings['normalSpeed']

		self.player.increaseEnergy(self.clock.get_time())

		if inputPressed[actions["up"]]:
			if "Top" not in walls:
				playerSpeedY -= 1
			playerMouvY -= 1

		if inputPressed[actions["down"]]:
			if "Bottom" not in walls:
				playerSpeedY += 1
			playerMouvY += 1

		if inputPressed[actions["left"]]:
			if "Left" not in walls:
				playerSpeedX -= 1
			playerMouvX -= 1

		if inputPressed[actions["right"]]:
			if "Right" not in walls:
				playerSpeedX += 1
			playerMouvX += 1
		
		if playerSpeedX != 0 or playerSpeedY != 0:
			self.player.setVelocity(playerSpeedX, playerSpeedY)
		
		self.player.setOrientation(playerMouvX, playerMouvY)
		
		# attack code
		if inputPressed[actions["attack"]]:
			attackinfo = self.player.attack()

			if attackinfo is not None:
				self.damagesInfos.append(attackinfo)
				"""for entity in self.entitiesManager.visibleEntities:
					if entity.data['type'] == 'monster' and attackinfo['attackRect'].colliderect(entity.rect):
						print("Hit " + entity.name)
						entity.stats['health'] -= attackinfo['damage']"""

	def playerInputMenus(self,inputEvent,inputPressed):
		
		inventoryPressed, skillTreePressed, pausePressed = False, False, False

		for event in inputEvent:
			if event.type == pygame.KEYDOWN:
				if event.key==actions["inventory"]:
					inventoryPressed = True
				if event.key==actions["skillTree"]:
					skillTreePressed = True
				if event.key==actions["pause"]:
					pausePressed = True

		self.currentHUD = 'main'

		# inventory code
		if inventoryPressed and not self.player.skillTree.isOpen:
			if not self.player.inventory.isOpen:
				self.player.inventory.isOpen = True
			else:
				self.player.inventory.isOpen = False
		
		# skillTree code
		if skillTreePressed and not self.player.inventory.isOpen:
			if not self.player.skillTree.isOpen:
				self.player.skillTree.isOpen = True
			else:
				self.player.skillTree.isOpen = False

		if self.player.inventory.isOpen:
			self.currentHUD = 'inventory'

		if self.player.skillTree.isOpen:
			self.currentHUD = 'skillTree'

		if self.HUDMenuManager.huds['pauseMenu']['isOpen']:
			self.currentHUD = 'pauseMenu'

		# pause menu code
		if pausePressed:
			if self.currentHUD in ['inventory','skillTree']:
				self.player.inventory.isOpen = False
				self.player.skillTree.isOpen = False
				
			else:
				if not self.HUDMenuManager.huds['pauseMenu']['isOpen']:
					if self.currentHUD not in ['optionMenu']: #menus in pauseMenu
						self.HUDMenuManager.huds['pauseMenu']['isOpen'] = True
						self.currentHUD = 'pauseMenu'
				else:
					self.HUDMenuManager.huds['pauseMenu']['isOpen'] = False
					self.HUDMenuManager.huds['pauseMenu']['optionOpen'] = False
					self.currentHUD = 'main'

	def applyDamages(self):
		for entity in self.entitiesManager.visibleEntities:
			for damagedInfo in self.damagesInfos:
				if entity.data['type'] in ['monster','player'] and entity != damagedInfo['entity'] and damagedInfo['attackRect'].colliderect(entity.rect):
					print("Hit " + entity.name, entity.stats['health'])
					entity.takeDamageOf(damagedInfo['damage'])
		
		self.damagesInfos = []

	def DrawWorld(self):
		super().DrawWorld()

		widthBy2 = self.param['width']/2
		heightBy2 = self.param['height']/2

		coords = self.ScreenToWorldCoords
		for entity in self.entitiesManager.visibleEntities:
			entity.collisions = {}

		for y_index,y in enumerate(self.world.world[coords['yStart']:coords['yEnd']]):
			for x_index,x in enumerate(y[coords['xStart']:coords['xEnd']]):
				coord = ((x_index*self.newPixelScale)-(coords['offx']*self.newPixelScale) , (y_index*self.newPixelScale)-(coords['offy']*self.newPixelScale))
				
				wall = self.world.walls[coords['yStart']+y_index][coords['xStart']+x_index]
				if wall == " ":
					self.window.blit(self.world.sprites[x], coord)

				else:
					self.window.blits(((self.world.sprites[x], coord),(self.world.sprites[wall], coord)))
					for entity in self.entitiesManager.visibleEntities:
						if entity.data['type'] != 'item':
							x,y = entity.x - (coords['xStart'] + coords['offx']),entity.y - (coords['yStart']+coords['offy'])
							x,y = x*self.param['newPixelScale'], y*self.param['newPixelScale']
							dist = math.hypot(coord[0]-x, coord[1]-y)
							if abs(dist) < self.collisionsDistance:
								if (y_index,x_index) not in self.collisions:
									entity.collisions[(y_index,x_index)] = coord
							
								if self.debugMode == True:
									pygame.draw.rect(self.window,(255,0,0),Rect(coord,(self.newPixelScale,self.newPixelScale)))

		#self.particles.draw((500,500))
		
	def checkCollision(self):
		ents = [ent for ent in self.entitiesManager.visibleEntities if ent.data['type'] != 'item']
		for Entity in ents:
			walls = []

			yEntityMin, yEntityMax = math.floor(Entity.y), math.ceil(Entity.y)
			xEntityMin, xEntityMax = math.floor(Entity.x), math.ceil(Entity.x)

			points = {
				"topleft": {
					"value": 0,
					"pos": Entity.rect.topleft
				},
				"topleftbottom": {
					"value": 0,
					"pos": (Entity.rect.topleft[0],Entity.rect.topleft[1]+Entity.colAngleSize)
				},
				"toplefttop": {
					"value": 0,
					"pos": (Entity.rect.topleft[0]+Entity.colAngleSize,Entity.rect.topleft[1])
				},

				"topright": {
					"value": 0,
					"pos": Entity.rect.topright
				},
				"toprighttop": {
					"value": 0,
					"pos": (Entity.rect.topright[0]-Entity.colAngleSize,Entity.rect.topright[1])
				},
				"toprightbottom": {
					"value": 0,
					"pos": (Entity.rect.topright[0],Entity.rect.topright[1]+Entity.colAngleSize)
				},

				"bottomright": {
					"value": 0,
					"pos": Entity.rect.bottomright
				},
				"bottomrighttop": {
					"value": 0,
					"pos": (Entity.rect.bottomright[0],Entity.rect.bottomright[1]-Entity.colAngleSize)
				},
				"bottomrightbottom": {
					"value": 0,
					"pos": (Entity.rect.bottomright[0]-Entity.colAngleSize,Entity.rect.bottomright[1])
				},

				"bottomleft": {
					"value": 0,
					"pos": Entity.rect.bottomleft
				},
				"bottomlefttop": {
					"value": 0,
					"pos": (Entity.rect.bottomleft[0],Entity.rect.bottomleft[1]-Entity.colAngleSize)
				},
				"bottomleftbottom": {
					"value": 0,
					"pos": (Entity.rect.bottomleft[0]+Entity.colAngleSize,Entity.rect.bottomleft[1])
				}
			}

			for collisions in Entity.collisions.keys():
				rect = Rect(Entity.collisions[collisions],(self.newPixelScale,self.newPixelScale))

				for point in points.keys():
					if points[point]["value"] == 0:
						
						points[point]["value"] = rect.collidepoint(points[point]["pos"])
			
			for entity in self.entitiesManager.visibleEntities:
				if entity != Entity and entity.data['type'] != 'item':
					for point in points.keys():
						if points[point]["value"] == 0:
							points[point]["value"] = entity.rect.collidepoint(points[point]["pos"])
				
			if points["topleft"]["value"] and points["toplefttop"]["value"] or points["topright"]["value"] and points["toprighttop"]["value"]:
				walls.append("Top")
			if points["bottomleft"]["value"] and points["bottomleftbottom"]["value"] or points["bottomright"]["value"] and points["bottomrightbottom"]["value"]:
				walls.append("Bottom")
			if points["topleft"]["value"] and points["topleftbottom"]["value"] or points["bottomleft"]["value"] and points["bottomlefttop"]["value"]:
				walls.append("Left")
			if points["topright"]["value"] and points["toprightbottom"]["value"] or points["bottomright"]["value"] and points["bottomrighttop"]["value"]:
				walls.append("Right")

			Entity.walls = walls

	def DrawHUDs(self):
		super().DrawHUDs()

		xM, yM = pygame.mouse.get_pos()
		color = (255,255,255)
		pygame.draw.rect(self.window, color, (xM-crosshair['gap']-crosshair['length'], yM-crosshair['width']/2, crosshair['length'], crosshair['width']) )
		pygame.draw.rect(self.window, color, (xM+crosshair['gap'], yM-crosshair['width']/2, crosshair['length'], crosshair['width']) )
		pygame.draw.rect(self.window, color, (xM-crosshair['width']/2, yM-crosshair['gap']-crosshair['length'], crosshair['width'] , crosshair['length']) )
		pygame.draw.rect(self.window, color, (xM-crosshair['width']/2, yM+crosshair['gap'], crosshair['width'], crosshair['length']) )

if __name__ == "__main__":
	with open("config.json","r") as file:
		engineParameters = json.load(file)

	engine = Engine(engineParameters)
	engine.engineLoop()
