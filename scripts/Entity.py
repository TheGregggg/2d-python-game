import gregngine.engine as gregngine

import random

from scripts.Item import *

from scripts.ParticleSystem import *

class Entity(gregngine.Entity):
	def __init__(self, param):
		super().__init__(param)

		self.blood = ParticleSystem(self.engine, color=(255,20,20),
		duration=10, power=1, startSize=0.8, sizeReduction=0.015,
		emitingRate=0.5, emitingRadius=360, gravity=0.01, speed=0.4, 
		outline=1, outlineColor=(0,0,0))
		self.blood.coordReference = 'global'

	def draw(self, xStart, yStart, passThrough):
		super().draw(xStart, yStart, passThrough)

		if self.stats['health'] < self.stats['maxHealth']:
			self.blood.emitingRate = self.stats['health']/self.stats['maxHealth']
			xToDraw = self.x - xStart 
			yToDraw = self.y - yStart
			coords = (int((xToDraw+0.5)*self.param['newPixelScale']), int((yToDraw+0.5)*self.param['newPixelScale']))
			self.blood.draw(coords)
	
	def takeDamageOf(self, damage):
		self.stats['health'] -= damage
	
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
