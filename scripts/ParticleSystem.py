import pygame 
from pygame.locals import *

import time
import math
import random

import gregngine.functions as gFunction
import gregngine.engine as gregngine

class ParticleSystem():
    def __init__(self, engine, color, duration, power, startSize, sizeReduction, emitingRate, emitingRadius, speed, outline=None,outlineColor=(0,0,0), shape='circle', offSetAngle=180, gravity=0):
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
        self.shape = shape
        self.offSetAngle = offSetAngle

        self.outline = outline
        self.outlineColor = outlineColor

        self.coordReference = 'local'

        self.pixelSize = self.engine.param['newPixelScale']

        self.lastTimeEmited = 0

        self.particles = []

    def draw(self, coords, vel=None, color=None,startSize=None):
        dTime = self.engine.clock.get_time()
        if self.coordReference == 'local':
            xToDraw, yToDraw = coords
        elif self.coordReference == 'global':
            xToDraw, yToDraw = 0,0
            camVelocity = self.engine.mainCamera.velocity
            xCam = camVelocity[0] * self.pixelSize
            yCam = camVelocity[1] * self.pixelSize

        for particle in self.particles:
            # draw particles
            if self.shape == 'circle':
                if self.outline is not None:
                    pygame.draw.circle(self.engine.window, self.outlineColor, (xToDraw+particle['pos'][0], yToDraw+particle['pos'][1]), particle['size']+self.outline)
                pygame.draw.circle(self.engine.window, particle['color'], (xToDraw+particle['pos'][0], yToDraw+particle['pos'][1]), particle['size'])
            elif self.shape == 'square':
                if self.outline is not None:
                    pygame.draw.rect(self.engine.window, self.outlineColor, (xToDraw+particle['pos'][0]-self.outline/2, yToDraw+particle['pos'][1]-self.outline/2, particle['size']+self.outline, particle['size']+self.outline))
                pygame.draw.rect(self.engine.window, particle['color'], (xToDraw+particle['pos'][0], yToDraw+particle['pos'][1], particle['size'], particle['size']))

            # move particles
            if self.engine.currentHUD in self.engine.states['play']:
                particle['size'] -= self.sizeReduction * dTime
                if particle['size'] < 0:
                    self.particles.remove(particle)

                else:
                    if self.coordReference == 'local':
                        particle['pos'] = (particle['pos'][0] + particle['vel'][0], particle['pos'][1] + particle['vel'][1])
                    else: #global
                        particle['pos'] = (particle['pos'][0] + particle['vel'][0] - xCam, particle['pos'][1] + particle['vel'][1] - yCam)
                
                particle['vel'][1] += self.gravity

        if self.engine.currentHUD in self.engine.states['play']:
            if time.time() >= self.lastTimeEmited:    #shoot particles
                self.lastTimeEmited = time.time() + self.emitingRate
                for i in range(self.power):
                    angle = math.radians(random.randint(0, self.emitingRadius) + int(self.emitingRadius/2) + self.offSetAngle)
                    particle = {
                        'size': self.startSize,
                        'pos': [0,0],
                        'vel': [math.cos(angle)*self.speed , math.sin(angle)*self.speed],
                        'color': self.color
                    }
                    if self.coordReference == 'global':
                        particle['pos'] = coords
                    if startSize is not None:
                        particle['size'] = startSize* self.engine.param["scaleMultiplier"]
                    if vel is not None:
                        particle['vel'] = vel
                    if color is not None:
                        particle['color'] = color
                    self.particles.append(particle)
        


