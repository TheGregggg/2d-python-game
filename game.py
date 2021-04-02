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
	"attack": pygame.K_SPACE,
	"inventory": pygame.K_i
}

weaponTypeAPSMultiplier = {
	'sword': 1,
	'mace': 2
}

class Item():
	def __init__(self,param):
		"""
		param = {
			itemRepr
			"pixelSize": 16,
			"scaleMultiplier": 6,
		}
		"""
	
		self.param = param
		self.param['newPixelScale'] = self.param["pixelSize"]*self.param["scaleMultiplier"]

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
		self.tilemap = pygame.image.load(self.data["tilemap"]["src"])
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

class Inventory():
	def __init__(self):
		self.slots = [[None,None,None,None],[None,None,None,None]]
		self.hands = None
		self.isOpen = False
		self.player = None
	
	def drawHud(self,passThrough):
		scale = passThrough['HudScale']
		width, height = passThrough['window'].get_size()
		coords = {
			'right': 8,
			'top': 8,
			'height': 50,
			'width': 50,
			'inventory-margin': 5
		}
		coords['left'] = width - coords['width']*scale - coords['right']*scale
		coords['top'] *= scale
		transparency = 150
		radius = 10
		radius *= scale

		rects, circles = gFunction.createRectWithRoundCorner(0,0,coords['width']*scale,coords['height']*scale,radius)
		case = pygame.Surface((coords['width']*scale,coords['height']*scale), pygame.SRCALPHA)
		for rect in rects:
			pygame.draw.rect(case,(0,0,0,transparency),Rect(rect))
		for circle in circles:
			pygame.draw.circle(case,(0,0,0,transparency),circle,radius)

		if passThrough['currentHUD'] == 'main':
			passThrough['window'].blit(case, (coords['left'], coords['top']))

			if self.hands is not None:
				self.hands.drawSprite(scale,coords, passThrough)
				#passThrough['window'].blit(sprite, (width - coords['width']*scale - coords['right']*scale -8, -26+coords['top']*scale))
			if passThrough['mousePos'] is not None and Rect( (coords['left'], coords['top']),(int(coords['width']*scale),int(coords['height']*scale))).collidepoint(passThrough['mousePos']):
					self.isOpen = True
		
		if passThrough['currentHUD'] == 'inventory':
			stepHeight = coords['height'] + coords['inventory-margin']*2
			stepWidth  = coords['width']  + coords['inventory-margin']*2

			invWidth  = len(self.slots[0]) * stepWidth *scale
			invHeight = len(self.slots)    * stepHeight *scale
			startLeft = width/2  - invWidth/2  
			startTop  = height/2 - invHeight/2 

			cases = []

			for y,y_value in enumerate(self.slots):
				for x,x_value in enumerate(y_value):
					placeLeft = startLeft + x*(stepWidth  + coords['inventory-margin']/2)*scale + coords['inventory-margin']*scale
					placeTop  = startTop  + y*(stepHeight + coords['inventory-margin']/2)*scale + coords['inventory-margin']*scale
					cases.append({'place':(int(placeLeft),int(placeTop)),'x_value':x_value,'x':x,'y':y,'ground':False})

			cases.append({
				'place':(int(width/2  - stepWidth*scale/2 + coords['inventory-margin']*1.68*scale),int(height/2  - stepHeight*scale*2 + coords['inventory-margin']*scale)),
				'x_value':self.hands,
				'ground':False})
			
			ents = [ent for ent in passThrough['visibleEntities'] if ent.data['type'] == 'item' and ent.x == round(self.player.x) and ent.y == round(self.player.y)]

			if len(ents) > 0:
				groundItemWidth  = len(ents) * stepWidth * scale
				startLeft = width/2  - groundItemWidth/2
				startTop  = height/2 + invHeight/2 

				isSolo = 1 if len(ents) == 1 else 0

				for x,entity in enumerate(ents):
					placeLeft = startLeft + x*(stepWidth  + coords['inventory-margin']/2)*scale + coords['inventory-margin']*1.5*scale + coords['inventory-margin']/2*scale*isSolo
					placeTop  = startTop  + coords['inventory-margin']*2*scale 
					cases.append({'place':(int(placeLeft),int(placeTop)),'x_value':entity,'ground':True})

			for caseInfo in cases:
				passThrough['window'].blit(case,caseInfo['place'])
				
				if caseInfo['x_value'] is not None:
					coords['left'],coords['top'] = caseInfo['place']
					caseInfo['x_value'].drawSprite(scale,coords,passThrough)

				if passThrough['mousePos'] is not None:
					if Rect(caseInfo['place'],(int(coords['width']*scale),int(coords['height']*scale))).collidepoint(passThrough['mousePos']):
						if 'y' in caseInfo:
							temp = self.hands
							self.hands = self.slots[caseInfo['y']][caseInfo['x']]
							self.slots[caseInfo['y']][caseInfo['x']] = temp
						elif caseInfo['ground']:
							freeCases = []
							if self.hands is None:
								freeCases.append('hands')
							for y,y_value in enumerate(self.slots):
								for x,x_value in enumerate(y_value):
									if x_value is None:
										freeCases.append((y,x))
							
							if len(freeCases) > 0:
								if freeCases[0] == 'hands':
									self.hands = caseInfo['x_value']
								else:
									y,x = freeCases[0]
									self.slots[y][x] = caseInfo['x_value']
								self.player.parent.entitiesManager.killEntity(caseInfo['x_value'])
	
						else:
							self.isOpen = False

class Player(gregngine.Entity):
	def __init__(self, param):
		super().__init__(param)

		self.parent = None

		self.speed = self.stats["normalSpeed"]
		self.running = False

		self.camera = None
		self.inventory = Inventory()
		self.inventory.player = self

		self.health = self.stats["maxHealth"]
		self.energy = self.stats["maxEnergy"]

		self.lastAttackTime = time.time()
		self.isAttacking = False
		self.atkAnim = {'lastStep':-1,'lastTime':0}

		self.animator.setFrame()

	def drawHud(self, xPos, yPos, passThrough):
		self.inventory.drawHud(passThrough)

		if passThrough['currentHUD'] == 'main':
			scale = passThrough['HudScale']

			x = ((self.energy * 100) / self.stats["maxEnergy"]) /100 if self.energy > 0 else 0

			rect = gFunction.createRectOutlined(x, 8*scale, 8*scale, 100*scale, 20*scale, 4*scale)
			pygame.draw.rect(passThrough['window'],(0,0,0),rect[0])

			if x > 0:
				pygame.draw.rect(passThrough['window'],(0,80,255),rect[1])

	def move(self,dTime):
		x,y = self.velocity['x'],self.velocity['y']

		if self.running and self.energy > 0 and (x != 0 or y !=0):
			x,y = x*self.stats["maxSpeed"],y*self.stats["maxSpeed"]
			if self.energy < 1:
				self.energy -= 10
			else:
				self.energy -= 30*dTime*0.001
		else:
			x,y = x*self.stats["normalSpeed"],y*self.stats["normalSpeed"]

		x,y = gFunction.normalize(x * dTime * 0.001,y * dTime * 0.001)

		self.x += x
		self.y += y

		camSmoothOffset = self.data['camera']['smoothOffset']

		if self.x - self.camera.x > self.param['x']+camSmoothOffset or self.x - self.camera.x < self.param['x']-camSmoothOffset:
			self.camera.move(x,0)
		if self.y - self.camera.y > self.param['y']+camSmoothOffset or self.y - self.camera.y < self.param['y']-camSmoothOffset:
			self.camera.move(0,y)

		self.setVelocity(0,0)

	def increaseEnergy(self,dtime):
	
		if self.energy < self.stats['maxEnergy']:
			self.energy += 10*dtime*0.001
			if self.stats['maxEnergy'] < self.energy:
				self.energy = self.stats['maxEnergy']

	def setCameraOffset(self,x,y):
		self.camera.xOffset = -(x/2) + self.param['x']
		self.camera.yOffset = -(y/2) + self.param['y']

	def attack(self):
		if self.inventory.hands is None:
			atkPerSec = self.stats['atkPerSec']
			damage = self.stats['atkBaseDamage']
		elif self.inventory.hands.data['itemType'] != 'weapon':
			return None
		else:
			atkPerSec = self.stats['atkPerSec']*weaponTypeAPSMultiplier.get(self.inventory.hands.data['weaponType'])
			damage = self.stats['atkBaseDamage'] + self.inventory.hands.data['stats']['damage']

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
				attackRect.left -= self.param['newPixelScale']
			elif lookingTo == 'right':
				attackRect.left += self.param['newPixelScale']
			elif lookingTo == 'top':
				attackRect.top -= self.param['newPixelScale']
			elif lookingTo == 'bottom':
				attackRect.top += self.param['newPixelScale']

			self.isAttacking = True

			return {'attackRect':attackRect,'damage':damage}

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

			elif self.inventory.hands is not None:
				currentStep = self.data['animation']['attack']['steps'][self.atkAnim['lastStep']]
				animationSurface = pygame.Surface((int(3*self.param['newPixelScale']),int(3*self.param['newPixelScale'])), pygame.SRCALPHA)

				sprite = self.inventory.hands.sprite
				tilemap = self.inventory.hands.data['tilemap']

				itemScale = (int(self.param['newPixelScale']*tilemap['scaling']/tilemap['ratio']),int(self.param['newPixelScale']*tilemap['scaling']))
				sprite = pygame.transform.scale(sprite.convert_alpha(),(itemScale))
				sprite = pygame.transform.rotate(sprite,currentStep['rotation'])

				animationSurface.blit(sprite,(currentStep['y'],currentStep['x']))
				if self.atkLookingTo == 'top':
					animationSurface = pygame.transform.rotate(animationSurface,90)
				elif self.atkLookingTo == 'bottom':
					animationSurface = pygame.transform.rotate(animationSurface,-90)
				elif self.atkLookingTo == 'left':
					animationSurface = pygame.transform.flip(animationSurface,True,False)

				return animationSurface

		return None

	def draw(self, xStart, yStart, passThrough):
		super().draw(xStart, yStart, passThrough)

		xToDraw = self.x - xStart -1
		yToDraw = self.y - yStart -1

		animationSurface = self.attackAnimation()
		if animationSurface is not None:
			passThrough['window'].blit(animationSurface,(xToDraw*self.param['newPixelScale'], yToDraw*self.param['newPixelScale']))

class Engine(gregngine.Engine):
	def __init__(self, param):
		super().__init__(param)

		self.world = world
		self.newPixelScale = self.param['newPixelScale']

		self.collisionsDistance = 1.5
		self.collisionsDistance *= self.newPixelScale
		self.collisions = {}

		self.rezizeSprites()

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
		self.loadSaves()

		sword = Item({'itemRepr':'normal_sword',"pixelSize": self.param['pixelSize'],"scaleMultiplier": self.param['scaleMultiplier'],'x':10,'y':6,'isGrounded':True})
		mace  = Item({'itemRepr':'normal_mace' ,"pixelSize": self.param['pixelSize'],"scaleMultiplier": self.param['scaleMultiplier'],'x':11,'y':6,'isGrounded':True})

		self.entitiesManager.addEntity(self.player)
		self.entitiesManager.addEntity(sword)
		self.entitiesManager.addEntity(mace)

		#self.entitiesManager.addEntity(gregngine.Entity({"name" : "slim1","entityRepr" : "slim","pixelSize": self.param['pixelSize'],"scaleMultiplier": self.param['scaleMultiplier'],'x':9,'y':10}))
		#self.entitiesManager.addEntity(gregngine.Entity({"name" : "bat1","entityRepr" : "bat","pixelSize": self.param['pixelSize'],"scaleMultiplier": self.param['scaleMultiplier'],'x':6,'y':15}))
		"""self.entitiesManager.addEntity(gregngine.Entity({"name" : "slim2","entityRepr" : "slim","pixelSize": self.param['pixelSize'],"scaleMultiplier": self.param['scaleMultiplier'],'x':10,'y':10}))
		self.entitiesManager.addEntity(gregngine.Entity({"name" : "slim3","entityRepr" : "slim","pixelSize": self.param['pixelSize'],"scaleMultiplier": self.param['scaleMultiplier'],'x':10,'y':11}))
		self.entitiesManager.addEntity(gregngine.Entity({"name" : "slim4","entityRepr" : "slim","pixelSize": self.param['pixelSize'],"scaleMultiplier": self.param['scaleMultiplier'],'x':10,'y':15}))
		self.entitiesManager.addEntity(gregngine.Entity({"name" : "slim5","entityRepr" : "slim","pixelSize": self.param['pixelSize'],"scaleMultiplier": self.param['scaleMultiplier'],'x':10,'y':16}))
		self.entitiesManager.addEntity(gregngine.Entity({"name" : "bat1","entityRepr" : "bat","pixelSize": self.param['pixelSize'],"scaleMultiplier": self.param['scaleMultiplier'],'x':6,'y':15}))
		self.entitiesManager.addEntity(gregngine.Entity({"name" : "bat2","entityRepr" : "bat","pixelSize": self.param['pixelSize'],"scaleMultiplier": self.param['scaleMultiplier'],'x':7,'y':15}))
		self.entitiesManager.addEntity(gregngine.Entity({"name" : "bat3","entityRepr" : "bat","pixelSize": self.param['pixelSize'],"scaleMultiplier": self.param['scaleMultiplier'],'x':8,'y':15}))"""
		
	def rezizeSprites(self):
		elems = ["g","s","r"]
		for sprite in elems:
			self.world.sprites[sprite] = pygame.transform.scale(self.world.sprites[sprite].convert_alpha(),(self.newPixelScale,self.newPixelScale))

	def main(self,inputEvent,inputPressed):
		self.checkCollision()
		self.playerInput(inputEvent,inputPressed)

		for entity in self.entitiesManager.visibleEntities:
			if entity.data['type'] == 'monster':
				walls = entity.walls
				adj = entity.x - self.player.x
				opo = entity.y - self.player.y
				hypo = math.sqrt(adj**2 + opo**2)

				if hypo < 0.7:
					entity.isAttacking = True
				
				if entity.isAttacking:
					entity.attack()

				else:
					coef = 1/hypo
					x = -adj * coef
					y = -opo * coef

					entity.setOrientation(x,y)
					
					if entity.isAttacking is False:
						if x > 0 and "Right" in walls:
							x *= 0
						if x < 0 and "Left" in walls:
							x *= 0
						if y > 0 and "Bottom" in walls:
							y *= 0
						if y < 0 and "Top" in walls:
							y *= 0

						entity.setVelocity(x,y)
		
	def playerInput(self,inputEvent,inputPressed):
		playerSpeedY,playerSpeedX = 0, 0
		playerMouvY,playerMouvX = 0, 0

		walls = self.player.walls

		if inputPressed[actions["sprint"]]:
			self.player.running = True
			if self.player.energy > 0:
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
				for entity in self.entitiesManager.visibleEntities:
					if entity.data['type'] == 'monster' and attackinfo['attackRect'].colliderect(entity.rect):
						print("Hit " + entity.name)
						entity.stats['health'] -= attackinfo['damage']

		# inventory code
		inventoryPressed = False

		self.mousePos = None
		for event in inputEvent:
			if event.type == pygame.KEYDOWN:
				if event.key==actions["inventory"]:
					inventoryPressed = True
			if event.type == pygame.MOUSEBUTTONDOWN:
				self.mousePos = pygame.mouse.get_pos()
			
		if inventoryPressed:
			#self.player.inventory()
			if not self.player.inventory.isOpen:
				self.player.inventory.isOpen = True
				self.currentHUD = 'inventory'
			else:
				self.player.inventory.isOpen = False
				self.currentHUD = 'main'

		if self.player.inventory.isOpen and self.currentHUD != 'inventory':
			self.currentHUD = 'inventory'
		if not self.player.inventory.isOpen and self.currentHUD == 'inventory':
			self.currentHUD = 'main'

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

if __name__ == "__main__":
	with open("config.json","r") as file:
		engineParameters = json.load(file)

	engine = Engine(engineParameters)
	engine.engineLoop()