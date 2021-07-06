import pygame 
from pygame.locals import *

import time

import gregngine.functions as gFunction
import gregngine.engine as gregngine

class Inventory():
	def __init__(self,player):
		self.slots  = [[None,None,None,None],[None,None,None,None]]
		self.stacks = [[   0,   0,   0,   0],[   0,   0,   0,   0]]
		self.hands = None
		self.handsStack = 0
		self.isOpen = False
		self.player = player
		self.engine = self.player.engine

		self.font = pygame.font.Font('./assets/fonts/Pixel Digivolve.otf', 10*self.player.engine.param['HudScale'])
	
	def drawHud(self,passThrough):
		scale = passThrough['HudScale']
		width, height = self.engine.HUDSurface.get_size()
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
			
			self.engine.HUDSurface.blit(case, (coords['left'], coords['top']))

			if self.hands is not None:
				self.hands.drawSprite(scale,coords, passThrough)
				#passThrough['window'].blit(sprite, (width - coords['width']*scale - coords['right']*scale -8, -26+coords['top']*scale))
			
			if self.handsStack > 1:
				img = self.font.render(str(self.handsStack), False, (255, 255, 255))
				imgLeft, imgTop = coords['left'] + case.get_width() - img.get_width() - img.get_width()/2, coords['top'] + case.get_height() - img.get_height() - img.get_height()/4
				self.engine.HUDSurface.blit(img,(imgLeft, imgTop))

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
				self.engine.HUDSurface.blit(case,caseInfo['place'])
				
				if caseInfo['x_value'] is not None:
					coords['left'],coords['top'] = caseInfo['place']
					caseInfo['x_value'].drawSprite(scale,coords,passThrough)
					img = self.font.render(caseInfo['x_value'].data['displayedName'], False, (255, 255, 255))
					imgLeft, imgTop = coords['left'] + (case.get_width() - img.get_width())/2, coords['top'] + case.get_height() - scale
					self.engine.HUDSurface.blit(img,(imgLeft, imgTop))

					if 'y' in caseInfo:
						if self.stacks[caseInfo['y']][caseInfo['x']] > 1:
							img = self.font.render(str(self.stacks[caseInfo['y']][caseInfo['x']]), False, (255, 255, 255))
							imgLeft, imgTop = coords['left'] + case.get_width() - img.get_width() - img.get_width()/2, coords['top'] + case.get_height() - img.get_height() - img.get_height()/4
							self.engine.HUDSurface.blit(img,(imgLeft, imgTop))
					elif caseInfo['x_value'] == self.hands:
						if self.handsStack > 1:
							img = self.font.render(str(self.handsStack), False, (255, 255, 255))
							imgLeft, imgTop = coords['left'] + case.get_width() - img.get_width() - img.get_width()/2, coords['top'] + case.get_height() - img.get_height() - img.get_height()/4
							self.engine.HUDSurface.blit(img,(imgLeft, imgTop))

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
