import pygame 
from pygame.locals import *

import pickle

import gregngine.functions as gFunction
import gregngine.engine as gregngine

from statics import *

class HUDMenuManager(gregngine.HUDMenuManager):
	def __init__(self,engine,hudScale):
		super().__init__(engine,hudScale)

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
			"startMenu": {
				'fonction': self.startMenu,
				'buttons': [
					{
						'text': 'Jouer',
						'fonction': self.btnPlay
					},
					{
						'text': 'Options',
						'fonction': self.btnOptions
					},
					{
						'text': 'Quitter',
						'fonction': self.btnQuit
					}
				]
			},
			"pauseMenu": {
				'fonction': self.pauseMenu,
				'isOpen': False,
				'optionOpen': False,
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
				],
				"optionMenu": {
					'buttons': [
						{
							'text': 'Haut',
							'fonction': self.assigneValue,
							'action': 'up'
						},
						{
							'text': 'Bas',
							'fonction': self.assigneValue,
							'action': 'down'
						},
						{
							'text': 'Gauche',
							'fonction': self.assigneValue,
							'action': 'left'
						},
						{
							'text': 'Droite',
							'fonction': self.assigneValue,
							'action': 'right'
						},
						{
							'text': 'Courir',
							'fonction': self.assigneValue,
							'action': 'sprint'
						},
						{
							'text': 'Attaque',
							'fonction': self.assigneValue,
							'action': 'attack'
						},
						{
							'text': 'Inventaire',
							'fonction': self.assigneValue,
							'action': 'inventory'
						},
						{
							'text': 'Comp??tences',
							'fonction': self.assigneValue,
							'action': 'skillTree'
						},
						{
							'text': 'Pause',
							'fonction': self.assigneValue,
							'action': 'pause'
						},
						{
							'text': 'Retour',
							'fonction': self.btnResume
						}
					]
				}
			},
			
		}
	
	def startMenu(self, passThrough):
		screenWidth, screenHeight = self.engine.window.get_size()
		background = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
		background.fill((255,255,255))
		passThrough['window'].blit(background, (0,0))

		scale = self.hudScale
		
		imgWidth, imgHeight = self.font.size('h')
		imgHeight += self.param['padding']['height']*2*scale
		topHeight = len(self.huds["pauseMenu"]['buttons'])*(imgHeight+self.param['margin']*scale)
		top = int(screenHeight - topHeight)

		self.mousePos = pygame.mouse.get_pos()

		btns = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)

		for button in self.huds["startMenu"]['buttons']:
			height = self.drawButton(button,'centered',top,passThrough,btns)
			top += height*scale

		title = self.font.render('The Legend of Pylda', False, (255, 158, 54))
		imgLeft = int(passThrough['window'].get_width()/2 - title.get_width()/2) + scale
		imgTop = 20*screenHeight/100
		passThrough['window'].blit(title, (imgLeft,imgTop))

		passThrough['window'].blit(btns, (0,0))
	
	def pauseMenu(self, passThrough):
		self.mousePos = pygame.mouse.get_pos()

		if self.huds['pauseMenu']['optionOpen']:
			self.optionMenu(passThrough)
		else:
			screenWidth, screenHeight = self.engine.window.get_size()

			background = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
			background.fill((0,0,0,75))
			passThrough['window'].blit(background, (0,0))

			scale = self.hudScale
			
			imgWidth, imgHeight = self.font.size('h')
			imgHeight += self.param['padding']['height']*2*scale
			topHeight = len(self.huds["pauseMenu"]['buttons'])*(imgHeight+self.param['margin']*scale)
			top = int(screenHeight/2 - topHeight/2)

			btns = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)

			for button in self.huds["pauseMenu"]['buttons']:
				height = self.drawButton(button,'centered',top,passThrough,btns)
				top += height*scale

			passThrough['window'].blit(btns, (0,0))

	def optionMenu(self, passThrough):
		screenWidth, screenHeight = self.engine.window.get_size()
		background = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
		background.fill((0,0,0,75))
		self.engine.window.blit(background, (0,0))

		scale = self.hudScale

		middle = screenWidth/2
		margin = 5*scale

		imgWidth, imgHeight = self.font.size('h')
		imgHeight += self.param['padding']['height']*2*scale
		topHeight = len(self.huds["pauseMenu"]["optionMenu"]['buttons'])*(imgHeight+self.param['margin']*scale)
		top = int(screenHeight/2 - topHeight/2)

		btns = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)

		for button in self.huds["pauseMenu"]["optionMenu"]['buttons']:
			if 'action' in button :
				img = self.font.render(button['text'], False, self.param['color'])
				btns.blit(img,(middle-margin-img.get_width(), top+self.param['padding']['height']*scale))
				height = self.drawInputButton(button,middle+margin, top, passThrough, btns)
			else:
				height = self.drawButton(button,'centered',top,passThrough,btns)
			top += height*scale

		self.engine.window.blit(btns, (0,0))

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
	
	def drawInputButton(self,button,rectLeft,rectTop,passThrough,btns):
		scale = self.hudScale

		color = button['color'] if 'color' in button else self.param['color']
		img = self.font.render(pygame.key.name(actions[button['action']]), False, color)

		rectHeight = img.get_height() + self.param['padding']['height']*2*scale
		rectWidth = img.get_width() + self.param['padding']['width']*2*scale

		imgLeft = rectLeft + self.param['padding']['width']*scale
		imgTop = int(rectTop + rectHeight/2  - img.get_height()/2) - scale 

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
		self.huds['pauseMenu']['optionOpen'] = False
		self.engine.currentHUD = 'main'

	def btnSave(self):
		self.engine.saveGame()

	def btnOptions(self):
		self.huds['pauseMenu']['optionOpen'] = True

	def btnQuit(self):
		pygame.quit()
		quit()

	def btnPlay(self):
		self.engine.currentHUD = 'main'
		self.engine.loadGame()

	def assigneValue(self, action):
		pass