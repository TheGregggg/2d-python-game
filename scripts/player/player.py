import pygame 
from pygame.locals import *

import time
import math

import gregngine.functions as gFunction
import gregngine.engine as gregngine

from statics import *

from game import Inventory
from game import SkillTree 

from scripts.ParticleSystem import *

class Player(gregngine.Entity):
	def __init__(self, param):
		super().__init__(param)

		self.speed = self.stats["normalSpeed"]
		self.running = False
		self.isMoving = False

		self.camera = None
		self.inventory = Inventory(self)
		self.skillTree = SkillTree(self)
		self.applyNewStats()

		self.stats["energy"] = self.stats["maxEnergy"]
		self.stats["level"] = 1
		self.applyExpFromLevel()

		self.moneyLimit = 9999999
		self.stats["money"] = 0

		self.lastAttackTime = time.time()
		self.isAttacking = False
		self.atkAnim = {'lastStep':-1,'lastTime':0}

		self.animator.setFrame()

		self.particles = ParticleSystem(self.engine, color=(255,255,255),
		duration=10, power=3, startSize=1.5, sizeReduction=0.015,
		emitingRate=0.15, emitingRadius=90, gravity=0.005, speed=0.6, 
		outline=2, outlineColor=(50,50,50), shape='square')
		self.particles.coordReference = 'global'

		self.weaponParticles = ParticleSystem(self.engine, color=(255,255,255),
		duration=10, power=1, startSize=1.5, sizeReduction=0.09,
		emitingRate=0.0001, emitingRadius=360, gravity=0, speed=0, 
		outline=0, outlineColor=(0,0,0), shape='circle')
		self.weaponParticles.coordReference = 'global'

		self.weaponEffectsParticles = ParticleSystem(self.engine, color=(3, 173, 252),
		duration=10, power=1, startSize=4, sizeReduction=0.03,
		emitingRate=0.008, emitingRadius=360, speed=0, shape='circle')
		self.weaponEffectsParticles.coordReference = 'global'

		self.angleToMouse = 0
		self.lastAngleToMouse = 0

		self.specialsDamage = 1

	def applyExpFromLevel(self):
		expTable = self.data['experienceTable']
		self.stats["experience"] = 0
		self.stats["nextLevelExp"] = expTable[str(self.stats["level"])]['nextLevelExp']

	def initPostParent(self):
		self.bigFont = pygame.font.Font('./assets/fonts/Pixel Digivolve.otf', 30*self.engine.param['HudScale'])
		self.smallFont = pygame.font.Font('./assets/fonts/Pixel Digivolve.otf', 14*self.engine.param['HudScale'])

	def applyNewStats(self):
		for skill in self.data['skillTree']['skills']:
			if skill['statPerStep']['mode'] == 'add':
				self.stats[skill['statToModify']] = self.data['baseStats'][skill['statToModify']] + skill['steps']*skill['statPerStep']['value']
			elif skill['statPerStep']['mode'] == 'sub':
				self.stats[skill['statToModify']] = self.data['baseStats'][skill['statToModify']] - skill['steps']*skill['statPerStep']['value']

		self.data['animation']['attack']['stepTime'] = self.stats['atkPerSec']/len(self.data['animation']['attack']['steps'])

	def addMoney(self,money):
		addition = self.stats["money"] + money
		if addition > self.moneyLimit:
			self.stats["money"] = self.moneyLimit
		else:
			self.stats["money"] = addition
	
	def addExp(self,exp):
		if self.stats["level"] < 100:
			addition = self.stats["experience"] + exp
			if addition > self.stats["nextLevelExp"]:
				self.stats["level"] += 1
				self.stats["points"] += 1
				rest = addition - self.stats["nextLevelExp"]
				self.applyExpFromLevel()
				self.addExp(rest)
			else:
				self.stats["experience"] = addition

	def healOf(self,ammount):
		self.stats['health'] += ammount
		if self.stats['health'] > self.stats['maxHealth']:
			self.stats['health'] = self.stats['maxHealth']

	def takeDamageOf(self, damage):
		self.stats['health'] -= damage

	def drawHud(self, xPos, yPos, passThrough):
		self.inventory.drawHud(passThrough)
		self.skillTree.drawHud(passThrough)

		if passThrough['currentHUD'] == 'main':
			scale = passThrough['HudScale']

			top = 8
			left = 8

			expValue = 143*(self.stats['experience']/self.stats['nextLevelExp']) 
			expValue = expValue if expValue > 7 else 7

			healValue = 94*(self.stats['health']/self.stats['maxHealth']) 
			healValue = healValue if healValue > 7 else 7

			energyValue = 94*(self.stats['energy']/self.stats['maxEnergy']) 
			energyValue = energyValue if energyValue > 7 else 7

			rectCoords = [
				{ # first rect
					'top': 0,
					'left': 0,
					'width': 50,
					'height': 50
				},{ # ---- exp bar ------
					# second bottom rect 
					'top': 39,
					'left': 0,
					'width': 150,
					'height': 11
				},{ # exp bar behind rect
					'top': 43,
					'left': 2,
					'width': 143,
					'height': 3,
					'color': (85,85,85,255)
				},{ # exp bar front rect
					'top': 41,
					'left': 2,
					'width': expValue,
					'height': 7,
					'color': (0, 135, 255,255)
				},{ # ---- heal bar ----
					# heal bar outline bottom rect
					'top': 2,
					'left': 52,
					'width': 98,
					'height': 11
				},{ # heal bar behind rect
					'top': 6,
					'left': 55,
					'width': 91,
					'height': 3,
					'color': (85,85,85,255)
				},{ # heal bar front rect
					'top': 4,
					'left': 54,
					'width': healValue,
					'height': 7,
					'color': (255,80,0,255)
				},{ # ---- energy bar ----
					# energy bar outline bottom rect
					'top': 15,
					'left': 52,
					'width': 98,
					'height': 11
				},{ # energy bar behind rect
					'top': 19,
					'left': 55,
					'width': 91,
					'height': 3,
					'color': (85,85,85,255)
				},{ # energy bar front rect
					'top': 17,
					'left': 54,
					'width': energyValue,
					'height': 7,
					'color': (0,80,255,255)
				}
			]
			transparency = 225
			Radius = 10

			case = pygame.Surface((150*scale,50*scale), pygame.SRCALPHA)
			for coords in rectCoords:
				radius = Radius*scale if Radius*scale <= coords['height']*scale/2 else coords['height']*scale/2
				color = coords['color'] if 'color' in coords else (0,0,0,transparency)
				rects, circles = gFunction.createRectWithRoundCorner(coords['left']*scale,coords['top']*scale,coords['width']*scale,coords['height']*scale,radius)
				for rect in rects:
					pygame.draw.rect(case,color,Rect(rect))
				for circle in circles:
					pygame.draw.circle(case,color,circle,radius)
				
				if coords == rectCoords[0]:
					pygame.draw.rect(case,(0,0,0,transparency),
						Rect(rectCoords[0]['width']*scale,(rectCoords[1]['top']-Radius)*scale,Radius*scale,Radius*scale)) #little concave circle
					pygame.draw.circle(case,(0,0,0,0),((rectCoords[0]['width']+Radius)*scale,(rectCoords[1]['top']-Radius)*scale),Radius*scale,draw_bottom_left=True) #little concave circle mask
			
			passThrough['window'].blit(case, (left*scale, top*scale))

			# render level text
			img = self.bigFont.render(str(self.stats['level']), False, (255, 242, 0))
			imgLeft = int(left*scale + rectCoords[0]['width']*scale/2 - img.get_width()/2) + scale
			imgTop = int(top*scale + rectCoords[1]['top']*scale/2 - img.get_height()/2) + scale
			passThrough['window'].blit(img,(imgLeft, imgTop))

			# render money text
			img = self.smallFont.render(str(self.stats['money']) + ' $', False, (255, 242, 0))
			imgShadow = self.smallFont.render(str(self.stats['money']) + ' $', False, (0, 0, 0, 0.5))
			imgLeft = int(left*scale + rectCoords[1]['width']*scale - img.get_width()) + scale
			imgTop = int(top*scale + rectCoords[7]['top']*scale + img.get_height()/2 )
			passThrough['window'].blit(imgShadow,(imgLeft+scale, imgTop+scale))
			passThrough['window'].blit(img,(imgLeft, imgTop))

	def drawHudBar(self,value,max,color,passThrough,coords):
		"""
		coords = {
			'top',
			'left',
			'width',
			'height',
			'outline'
		}
		"""
		scale = passThrough['HudScale']
		x = ((value * 100) / max) /100 if value > 0 else 0

		rect = gFunction.createRectOutlined(x, coords['left']*scale, coords['top']*scale, coords['width']*scale, coords['height']*scale, coords['outline']*scale)
		pygame.draw.rect(passThrough['window'],(0,0,0),rect[0])

		if x > 0:
			pygame.draw.rect(passThrough['window'],color,rect[1])

	def move(self,dTime):
		x,y = self.velocity['x'],self.velocity['y']

		if self.velocity['x'] != 0 or self.velocity['y'] != 0:
			self.isMoving = True
		else:
			self.isMoving = False

		if self.running and self.stats['energy']  > 0 and (x != 0 or y !=0):
			x,y = x*self.stats["maxSpeed"],y*self.stats["maxSpeed"]
			if self.stats['energy']  < 1:
				self.stats['energy'] -= 10
			else:
				self.stats['energy'] -= 30*dTime*0.001
		else:
			x,y = x*self.stats["normalSpeed"],y*self.stats["normalSpeed"]

		x,y = gFunction.normalize(x * dTime * 0.001,y * dTime * 0.001)

		self.x += x
		self.y += y

		camSmoothPercentage = self.data['camera']['smoothPercentage']

		camCenterX = self.camera.x + self.param['x']
		camCenterY = self.camera.y + self.param['y']

		camMouvX = (self.x - camCenterX) / camSmoothPercentage
		camMouvY = (self.y - camCenterY) / camSmoothPercentage

		self.camera.move(camMouvX, camMouvY)

		self.setVelocity(0,0)

	def increaseEnergy(self,dtime):
		if self.stats['energy'] < self.stats['maxEnergy']:
			self.stats['energy'] += 10*dtime*0.001
			if self.stats['maxEnergy'] < self.stats['energy']:
				self.stats['energy'] = self.stats['maxEnergy']

	def setCameraOffset(self,x,y):
		self.camera.xOffset = -(x/2) + self.param['x']
		self.camera.yOffset = -(y/2) + self.param['y']

	def attack(self):
		if self.inventory.hands is None:
			atkPerSec = self.stats['atkPerSec']
			damage = self.stats['atkBaseDamage']
		elif self.inventory.hands.data['itemType'] == 'consumable':
			atkPerSec = self.stats['atkPerSec']
		else:
			atkPerSec = self.stats['atkPerSec']*weaponTypeAPSMultiplier.get(self.inventory.hands.data['weaponType'])
			damage = self.stats['atkBaseDamage'] + self.inventory.hands.data['stats']['damage']

		currentTime = time.time()   
		if currentTime-self.lastAttackTime >= atkPerSec and not self.isAttacking:
			self.lastAttackTime = currentTime 

			if self.inventory.hands is not None and self.inventory.hands.data['itemType'] == 'consumable':
				self.consumeItemInHand()
				return None

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

	def drawWeapon(self,playerCenter):
		sprite = self.inventory.hands.sprite
		tilemap = self.inventory.hands.data['tilemap']
		itemScale = (int(self.param['newPixelScale']*tilemap['scaling']/tilemap['ratio']),int(self.param['newPixelScale']*tilemap['scaling']))
		sprite = pygame.transform.scale(sprite.convert_alpha(),itemScale)
		weaponSurface = pygame.Surface((sprite.get_width(),sprite.get_height()*2), pygame.SRCALPHA)
		weaponSurface.blit(sprite,(0,0))
		weaponSurface = pygame.transform.rotate(weaponSurface, -self.angleToMouse)
		self.engine.window.blit(weaponSurface, (playerCenter[0] - weaponSurface.get_width()/2,playerCenter[1] - weaponSurface.get_height()/2))

	def consumeItemInHand(self):
		if self.inventory.hands.data["itemType"] == 'consumable':
			if 'heal' in self.inventory.hands.data['stats']:
				self.healOf(self.inventory.hands.data['stats']['heal'])

			if self.inventory.handsStack > 1:
				self.inventory.handsStack -= 1
			else:
				self.inventory.hands = None
				self.inventory.handsStack = 0
			
	def draw(self, xStart, yStart, passThrough):
		xToDraw = self.x - xStart 
		yToDraw = self.y - yStart

		willDrawWeapon = False
		weaponParticlesCoords = (0,0)

		# angle compare to mouse and player pos weapon
		playerCenter = (int((xToDraw+0.5)*self.param['newPixelScale']), int((yToDraw+0.5)*self.param['newPixelScale']))
		playerCenter = (int((xToDraw+0.5)*self.param['newPixelScale']), int((yToDraw+0.5)*self.param['newPixelScale']))
		if self.engine.currentHUD in self.engine.states['play']:
			mouse = pygame.mouse.get_pos()
			adj, opo = mouse[0] - playerCenter[0], mouse[1] - playerCenter[1]
			hypo = math.sqrt(adj**2 + opo**2)
			cos, sin = adj/hypo, opo/hypo
			angle = ((math.asin(sin))*180)/math.pi
			angle +=90
			if cos < 0:
				angle = 180 + 180-angle
			self.lastAngleToMouse = self.angleToMouse
			self.angleToMouse = angle

			angleMouse = self.angleToMouse
			if self.lastAngleToMouse > 315 and self.angleToMouse < 45:
				angleMouse += 360
			mouseAngleDif = max(angleMouse,self.lastAngleToMouse) - min(angleMouse,self.lastAngleToMouse)

			weaponParticlesVelocity = None
			if self.isAttacking and mouseAngleDif > 2 and self.stats['energy'] > 0:
				self.weaponEffectsParticles.power = 1
				weaponParticlesVelocity = [cos*2,sin*2]
				self.stats['energy'] -= 100*self.engine.clock.get_time()*0.001
			else:
				self.weaponEffectsParticles.power = 0

			#weapon normal parcticles calculations
			if self.inventory.hands is not None and self.inventory.hands.data["itemType"] == 'weapon':
				self.specialsDamage = self.inventory.hands.data['stats']['specials damage']
				circleRadius = self.inventory.hands.data['particles']['circle']*self.param['newPixelScale']
				weaponParticlesCoords = (playerCenter[0] + cos*circleRadius, playerCenter[1] + sin*circleRadius)

			#weapon particles
		self.weaponParticles.draw(weaponParticlesCoords)
		self.weaponEffectsParticles.draw(weaponParticlesCoords,vel=weaponParticlesVelocity)
		for particle in self.weaponEffectsParticles.particles:
			attackRect = pygame.Rect(particle['pos'][0] + particle['size']*0.25,particle['pos'][1]+ particle['size']*0.25, particle['size']*0.75, particle['size']*0.75)
			damage = (particle['size']/self.weaponEffectsParticles.startSize)*self.specialsDamage
			self.engine.damagesInfos.append({'entity':self, 'particle': particle,'attackRect':attackRect,'damage': damage})

		#draw weapon before player if top direction
		if self.inventory.hands is not None and self.inventory.hands.data["itemType"] == 'weapon':
			self.weaponParticles.power = 1
			if not 90 < self.angleToMouse < 270:
				self.drawWeapon(playerCenter)
			else:
				willDrawWeapon = True
		else:
			self.weaponParticles.power = 0

		# particles when moving
		coords = (int((xToDraw+0.5)*self.param['newPixelScale']), int((yToDraw+1.05)*self.param['newPixelScale']))
		if self.isMoving:
			self.particles.color = self.engine.window.get_at(coords)
			self.particles.power = 2
		else:
			self.particles.power = 0
		
		self.particles.draw(coords)

		#draw player
		self.rect = Rect((xToDraw+self.col['offSets']['left'])*self.param['newPixelScale'], (yToDraw+self.col['offSets']['top'])*self.param['newPixelScale'], self.col['size']['width']*self.param['newPixelScale'], self.col['size']['height']*self.param['newPixelScale'])
		if passThrough['debug'] == True:
			pygame.draw.rect(passThrough['window'],(255,0,0),self.rect)
		if not passThrough['isPaused']:
			self.animator.setFrame()
		passThrough['window'].blit(self.animator.sprite , (xToDraw*self.param['newPixelScale'], yToDraw*self.param['newPixelScale']))

		#draw weapon after player if bottom direction
		if willDrawWeapon:
			self.drawWeapon(playerCenter)
