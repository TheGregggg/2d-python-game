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

weaponTypeAPSMultiplier = {
	'sword': 1,
	'mace': 2
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
			"startMenu": self.startMenu,
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
	
	def startMenu(self, passThrough):
		pass
	
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
		with open(self.engine.savePath + '/data.save', 'wb') as f:
			data = {}
			
			data['playerPos'] = (self.engine.player.x,self.engine.player.y)
			data['playerOrientation'] = self.engine.player.animator.lastAnimation

			data['playerInv'] = {}
			data['playerInv']['hands'] = None if self.engine.player.inventory.hands is None else self.engine.player.inventory.hands.data['name']
			data['playerInv']['handsStack'] = self.engine.player.inventory.handsStack
			data['playerInv']['slots'] = []
			for row in self.engine.player.inventory.slots:
				r = []
				for col in row:
					if col is not None:
						r.append(col.data['name'])
					else:
						r.append(None)
				data['playerInv']['slots'].append(r)

			data['playerInv']['stacks'] = self.engine.player.inventory.stacks
			data['playerData'] = self.engine.player.data
			data['playerData']['skillTree']['skills'] = self.engine.player.skillTree.skills

			data['entities'] = []
			for entitie in self.engine.entitiesManager.entities:
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

	def btnOptions(self):
		print('Options')

	def btnQuit(self):
		pygame.quit()
		quit()

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

class Inventory():
	def __init__(self,player):
		self.slots  = [[None,None,None,None],[None,None,None,None]]
		self.stacks = [[   0,   0,   0,   0],[   0,   0,   0,   0]]
		self.hands = None
		self.handsStack = 0
		self.isOpen = False
		self.player = player

		self.font = pygame.font.Font('./assets/fonts/Pixel Digivolve.otf', 10*self.player.engine.param['HudScale'])
	
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
			
			if self.handsStack > 1:
				img = self.font.render(str(self.handsStack), False, (255, 255, 255))
				imgLeft, imgTop = coords['left'] + case.get_width() - img.get_width() - img.get_width()/2, coords['top'] + case.get_height() - img.get_height() - img.get_height()/4
				passThrough['window'].blit(img,(imgLeft, imgTop))

			if passThrough['mousePosClick'] is not None and Rect((coords['left'], coords['top']),(int(coords['width']*scale),int(coords['height']*scale))).collidepoint(passThrough['mousePosClick']):
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
					img = self.font.render(caseInfo['x_value'].data['displayedName'], False, (255, 255, 255))
					imgLeft, imgTop = coords['left'] + (case.get_width() - img.get_width())/2, coords['top'] + case.get_height() - scale
					passThrough['window'].blit(img,(imgLeft, imgTop))

					if 'y' in caseInfo:
						if self.stacks[caseInfo['y']][caseInfo['x']] > 1:
							img = self.font.render(str(self.stacks[caseInfo['y']][caseInfo['x']]), False, (255, 255, 255))
							imgLeft, imgTop = coords['left'] + case.get_width() - img.get_width() - img.get_width()/2, coords['top'] + case.get_height() - img.get_height() - img.get_height()/4
							passThrough['window'].blit(img,(imgLeft, imgTop))
					elif caseInfo['x_value'] == self.hands:
						if self.handsStack > 1:
							img = self.font.render(str(self.handsStack), False, (255, 255, 255))
							imgLeft, imgTop = coords['left'] + case.get_width() - img.get_width() - img.get_width()/2, coords['top'] + case.get_height() - img.get_height() - img.get_height()/4
							passThrough['window'].blit(img,(imgLeft, imgTop))

				if passThrough['mousePosClick'] is not None:
					if Rect(caseInfo['place'],(int(coords['width']*scale),int(coords['height']*scale))).collidepoint(passThrough['mousePosClick']):
						if 'y' in caseInfo:
							temp = self.hands
							stackTemp = self.handsStack

							self.hands = self.slots[caseInfo['y']][caseInfo['x']]
							self.slots[caseInfo['y']][caseInfo['x']] = temp

							self.handsStack = self.stacks[caseInfo['y']][caseInfo['x']]
							self.stacks[caseInfo['y']][caseInfo['x']] = stackTemp

						elif caseInfo['ground']:
							freeCases = []
							sameCases = []
							if self.hands is None:
								freeCases.append('hands')
							elif self.hands.data['name'] == caseInfo['x_value'].data['name'] and self.hands.data['stats']['stackable'] and self.stacks[y][x] < 100:
								sameCases.append('hands')
							for y,y_value in enumerate(self.slots):
								for x,x_value in enumerate(y_value):
									if x_value is not None and x_value.data['name'] == caseInfo['x_value'].data['name'] and x_value.data['stats']['stackable'] and self.stacks[y][x] < 100:
										sameCases.append((y,x))
									if x_value is None:
										freeCases.append((y,x))
							
							if len(sameCases) > 0:
								if sameCases[0] == 'hands':
									self.handsStack += 1
								else:
									y,x = sameCases[0]
									if self.slots[y][x] is not None:
										self.stacks[y][x] += 1
								self.player.engine.entitiesManager.killEntity(caseInfo['x_value'])

							elif len(freeCases) > 0:
								if freeCases[0] == 'hands':
									self.hands = caseInfo['x_value']
									self.handsStack = 1
								else:
									y,x = freeCases[0]
									self.slots[y][x] = caseInfo['x_value']
									self.stacks[y][x] = 1
								self.player.engine.entitiesManager.killEntity(caseInfo['x_value'])
	
						else:
							self.isOpen = False

class SkillTree():
	def __init__(self,player):
		self.player = player
		self.skills = self.player.data['skillTree']['skills']
		self.isOpen = False
		self.font = pygame.font.Font('./assets/fonts/Pixel Digivolve.otf', 20*self.player.engine.param['HudScale'])
	
	def drawHud(self,passThrough):
		if passThrough['currentHUD'] not in ['skillTree']:
			return

		if passThrough['currentHUD'] == 'skillTree':
			self.skillTree(passThrough)
			
	def skillTree(self,passThrough):
		scale = passThrough['HudScale']
		width, height = passThrough['window'].get_size()

		percentageHeight = 1.2
		percentageWidth = 1.2

		coords = {
			'left': (width - width/percentageWidth)/2,
			'top': (height - height/percentageHeight)/2,
			'height': height/percentageHeight,
			'width': width/percentageWidth
		}

		transparency = 150
		radius = 10
		radius *= scale

		rects, circles = gFunction.createRectWithRoundCorner(0,0,coords['width'],coords['height'],radius)
		popup = pygame.Surface((coords['width'],coords['height']), pygame.SRCALPHA)
		for rect in rects:
			pygame.draw.rect(popup,(0,0,0,transparency),Rect(rect))
		for circle in circles:
			pygame.draw.circle(popup,(0,0,0,transparency),circle,radius)

		passThrough['window'].blit(popup, (coords['left'], coords['top']))
		
		# logic for first part -> skills and skills bar
		#### logic for left part -> skills name

		heightOfEachPart = (coords['height']/2) / (len(self.skills) + 1)
		imgWidth, imgHeight = self.font.size('h')
		marginTop = heightOfEachPart - imgHeight

		img = self.font.render("Skill tree", False, (255, 242, 0))
		imgShadow = self.font.render("Skill tree", False, (255,200,0))
		imgLeft, imgTop = coords['left'] + marginTop, coords['top']  + marginTop/1.5
		passThrough['window'].blit(imgShadow,(imgLeft+scale, imgTop+scale))
		passThrough['window'].blit(img,(imgLeft, imgTop))

		if self.player.stats['points'] > 0:
			img = self.font.render(f"{self.player.stats['points']} points", False, (255, 242, 0))
			imgShadow = self.font.render(f"{self.player.stats['points']} points", False, (255,200,0))
			imgLeft, imgTop = coords['left'] + coords['width'] - img.get_width() - marginTop, coords['top']  + marginTop/1.5
			passThrough['window'].blit(imgShadow,(imgLeft+scale, imgTop+scale))
			passThrough['window'].blit(img,(imgLeft, imgTop))

		longerSkillName = 0
		for i in range(len(self.skills)):
			img = self.font.render(self.skills[i]['displayName'], False, (255, 242, 0))
			if img.get_width() > longerSkillName:
				longerSkillName = img.get_width()
			imgShadow = self.font.render(self.skills[i]['displayName'], False, (255,200,0))
			imgLeft = coords['left'] + marginTop
			imgTop = coords['top'] + (i+1)*heightOfEachPart + marginTop/1.5
			passThrough['window'].blit(imgShadow,(imgLeft+scale, imgTop+scale))
			passThrough['window'].blit(img,(imgLeft, imgTop))
			
		#### logic for right part -> skills bars

		barCoord = {}
		barCoord['btnWidth'] = img.get_height()
		barCoord['left'] = imgLeft + longerSkillName + marginTop + barCoord['btnWidth'] + marginTop/1.5
		barCoord['width'] = coords['width'] - barCoord['left'] + coords['left'] - marginTop 
		barRadius = 5*scale

		for i in range(len(self.skills)):
			top = (i+1)*heightOfEachPart + coords['top'] + marginTop/1.5

			collisionRect = Rect((barCoord['left'] - barCoord['btnWidth'] - marginTop/1.5 ,top),(int(barCoord['btnWidth']),int(barCoord['btnWidth'])))
			isHover = collisionRect.collidepoint(pygame.mouse.get_pos())
			btnColor = (133, 125, 66) if isHover else (255, 147, 38)
			btnColor = btnColor if self.player.stats['points'] > 0 and self.skills[i]['steps'] < self.skills[i]['maxSteps'] else (133, 125, 66)

			rects, circles = gFunction.createRectWithRoundCorner(barCoord['left'] - barCoord['btnWidth'] - marginTop/1.5 ,top,int(barCoord['btnWidth']),int(barCoord['btnWidth']),barRadius)
			for rect in rects:
				pygame.draw.rect(passThrough['window'],btnColor,Rect(rect))
			for circle in circles:
				pygame.draw.circle(passThrough['window'],btnColor,circle,barRadius)

			img = self.font.render("+", False, (255, 255, 255))
			passThrough['window'].blit(img,(barCoord['left'] - barCoord['btnWidth'] - marginTop/1.5 + img.get_width()/2 + scale/2, top - scale))

			leftOfEachPoly = (barCoord['width'] - barRadius) /self.skills[i]['maxSteps']
			barStepsSteep = leftOfEachPoly - 2*scale if leftOfEachPoly - 2*scale < 10*scale else 10*scale
			for step in range(self.skills[i]['maxSteps']):
				color = (255, 147, 38) if step+1 <= self.skills[i]['steps'] else (133, 125, 66)
				if step == 0:
					pygame.draw.circle(passThrough['window'],color,(barCoord['left'] + barRadius,top + barRadius),barRadius,draw_top_left=True)
					pygame.draw.circle(passThrough['window'],color,(barCoord['left'] + barRadius,top + img.get_height() - barRadius),barRadius,draw_bottom_left=True)
					pygame.draw.rect(passThrough['window'],color,Rect(barCoord['left'] + step*leftOfEachPoly, top + barRadius, barRadius, img.get_height() - 2*barRadius))

					points = [
						(barCoord['left'] + step*leftOfEachPoly + barRadius, top),
						(barCoord['left'] + step*leftOfEachPoly + barStepsSteep + leftOfEachPoly - 2*scale, top),
						(barCoord['left'] + step*leftOfEachPoly + leftOfEachPoly - 2*scale, top+img.get_height()),
						(barCoord['left'] + step*leftOfEachPoly + barRadius, top+img.get_height())
					]
					#Rect(barCoord['left'] + step*leftOfEachPoly, top, leftOfEachPoly-scale, img.get_height())
					pygame.draw.polygon(passThrough['window'], color, points)		
				elif step == self.skills[i]['maxSteps']-1:
					pygame.draw.circle(passThrough['window'],color,(barCoord['left'] + step*leftOfEachPoly + leftOfEachPoly - 2*scale,top + barRadius),barRadius,draw_top_right=True)
					pygame.draw.circle(passThrough['window'],color,(barCoord['left'] + step*leftOfEachPoly + leftOfEachPoly - 2*scale,top + img.get_height() - barRadius),barRadius,draw_bottom_right=True)
					pygame.draw.rect(passThrough['window'],color,Rect(barCoord['left'] + step*leftOfEachPoly + leftOfEachPoly - 2*scale, top + barRadius, barRadius, img.get_height() - 2*barRadius))

					points = [
						(barCoord['left'] + step*leftOfEachPoly + barStepsSteep, top),
						(barCoord['left'] + step*leftOfEachPoly + leftOfEachPoly - 2*scale, top),
						(barCoord['left'] + step*leftOfEachPoly + leftOfEachPoly - 2*scale, top+img.get_height()),
						(barCoord['left'] + step*leftOfEachPoly, top+img.get_height())
					]
					#Rect(barCoord['left'] + step*leftOfEachPoly, top, leftOfEachPoly-scale, img.get_height())
					pygame.draw.polygon(passThrough['window'], color, points)
				else:
					points = [
						(barCoord['left'] + step*leftOfEachPoly + barStepsSteep, top),
						(barCoord['left'] + step*leftOfEachPoly + barStepsSteep + leftOfEachPoly - 2*scale, top),
						(barCoord['left'] + step*leftOfEachPoly + leftOfEachPoly - 2*scale, top+img.get_height()),
						(barCoord['left'] + step*leftOfEachPoly, top+img.get_height())
					]
					#Rect(barCoord['left'] + step*leftOfEachPoly, top, leftOfEachPoly-scale, img.get_height())
					pygame.draw.polygon(passThrough['window'], color, points)

			# handle clicks requests
			if passThrough['mousePosClick'] is not None:
				if collisionRect.collidepoint(passThrough['mousePosClick']):
					skill = self.skills[i]
					if self.player.stats['points'] > 0 and skill['steps'] < skill['maxSteps']:
						skill['steps'] += 1
						self.player.stats['points'] -= 1
						self.player.applyNewStats()

		# logic for second part -> global player stats

class Entity(gregngine.Entity):
	def __init__(self, param):
		super().__init__(param)
	
	def death(self):
		print('im dead')
		if self.data['type'] == 'monster':
			for drop in self.stats['drops']:
				rng = random.randint(0,100)
				print(f"{rng} of {drop['rate']} to spawn {drop['loot']}")
				if drop['rate'] >= rng:
					item = Item({'itemRepr': drop['loot'], "engine": self.engine,'x': int(self.x),'y': int(self.y),'isGrounded':True})
					self.engine.entitiesManager.addEntity(item)
			
			self.engine.player.addExp(self.stats['exp'])

class Player(gregngine.Entity):
	def __init__(self, param):
		super().__init__(param)

		self.speed = self.stats["normalSpeed"]
		self.running = False

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

		camSmoothOffset = self.data['camera']['smoothOffset']

		if self.x - self.camera.x > self.param['x']+camSmoothOffset or self.x - self.camera.x < self.param['x']-camSmoothOffset:
			self.camera.move(x,0)
		if self.y - self.camera.y > self.param['y']+camSmoothOffset or self.y - self.camera.y < self.param['y']-camSmoothOffset:
			self.camera.move(0,y)

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
		super().draw(xStart, yStart, passThrough)

class Engine(gregngine.Engine):
	def __init__(self, param):
		super().__init__(param)

		self.world = world
		self.world.loadSprites('overworld',self.param['pixelSize'])
		self.newPixelScale = self.param['newPixelScale']
		
		self.HUDMenuManager = HUDMenuManager(self,self.param['HudScale'])
		self.states['play'] = ['main','inventory','skillTree']
		self.states['pause'] = ['pauseMenu']

		self.collisionsDistance = 1.5
		self.collisionsDistance *= self.newPixelScale
		self.collisions = {}

		self.damagesInfos = []

		self.rezizeSprites()

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

		# inventory code
		if inventoryPressed and not self.player.skillTree.isOpen:
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
		
		# skillTree code
		if skillTreePressed and not self.player.inventory.isOpen:
			if not self.player.skillTree.isOpen:
				self.player.skillTree.isOpen = True
				self.currentHUD = 'skillTree'
			else:
				self.player.skillTree.isOpen = False
				self.currentHUD = 'main'

		if self.player.skillTree.isOpen and self.currentHUD != 'skillTree':
			self.currentHUD = 'skillTree'
		if not self.player.skillTree.isOpen and self.currentHUD == 'skillTree':
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

	def applyDamages(self):
		for entity in self.entitiesManager.visibleEntities:
			for damagedInfo in self.damagesInfos:
				if entity.data['type'] in ['monster','player'] and entity != damagedInfo['entity'] and damagedInfo['attackRect'].colliderect(entity.rect):
					print("Hit " + entity.name, entity.stats['health'])
					entity.stats['health'] -= damagedInfo['damage']
		
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