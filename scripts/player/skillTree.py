import pygame 
from pygame.locals import *

import time

import gregngine.functions as gFunction
import gregngine.engine as gregngine

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