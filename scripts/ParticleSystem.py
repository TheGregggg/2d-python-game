import pygame 
from pygame.locals import *

import time
import math
import random

import gregngine.functions as gFunction
import gregngine.engine as gregngine

class ParticleSystem():
    def __init__(self, engine, color, duration, power, startSize, sizeReduction, emitingRate, emitingRadius, speed, outline=None,outlineColor=(0,0,0), gravity=0):
        self.engine = engine
        self.color = color
        self.duration = duration
        self.power = power
        self.startSize = startSize * self.engine.param["scaleMultiplier"]
        self.sizeReduction = sizeReduction
        self.emitingRate = emitingRate
        self.emitingRadius = emitingRadius
        self.gravity = gravity
        self.speed = speed

        self.outline = outline
        self.outlineColor = outline

        self.pixelSize = self.engine.param['newPixelScale']

        self.lastTimeEmited = 0

        self.particles = []

    def draw(self, coords):
        dTime = self.engine.clock.get_time()
        xToDraw, yToDraw = coords

        for particle in self.particles:
            # draw particles
            if self.outline is not None:
                pygame.draw.circle(self.engine.window, self.outlineColor, (xToDraw+particle['pos'][0], yToDraw+particle['pos'][1]), particle['size']+self.outline)
            pygame.draw.circle(self.engine.window, self.color, (xToDraw+particle['pos'][0], yToDraw+particle['pos'][1]), particle['size'])

            # move particles
            particle['size'] -= self.sizeReduction * dTime
            if particle['size'] < 0:
                self.particles.remove(particle)

            else:
                particle['pos'] = (particle['pos'][0] + particle['vel'][0], particle['pos'][1] + particle['vel'][1])
            
            particle['vel'][1] += self.gravity

        if time.time() >= self.lastTimeEmited:    #shoot particles
            self.lastTimeEmited = time.time() + self.emitingRate
            for i in range(self.power):
                angle = math.radians(random.randint(0, self.emitingRadius) + int(self.emitingRadius/2) + 180)
                particle = {
                    'size': self.startSize,
                    'pos': [0,0],
                    'vel': [math.cos(angle)*self.speed , math.sin(angle)*self.speed]
                }
                self.particles.append(particle)
        


