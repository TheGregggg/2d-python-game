import gregngine.engine as gregngine

import random

from scripts.Item import *


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
