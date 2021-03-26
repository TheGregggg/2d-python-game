# Gregoire Layet
# 23-03-2021
# Grafical and physical 2d engine with pygame

import pygame 
from pygame.locals import *

import gregngine.functions as gFunction

import shelve
import json

import math
import time

class Camera(object):
    def __init__(self, xInit=0, yInit=0, xOffsetInit=0, yOffsetInit=0):
        self.x = xInit
        self.y = yInit
        self.xOffset = xOffsetInit
        self.yOffset = yOffsetInit
        self.attachedTo = None

    def getPos(self):
        """
        return (x,y)
        """
        return (self.x + self.xOffset, self.y + self.yOffset)
    
    def move(self,x,y):
        """
        move by x and y
        """
        self.x += x
        self.y += y
    
    def setPos(self, x, y):
        """
        setpos by x and y
        """
        self.x = x
        self.y = y

class Animator(object):
    def __init__(self,data,param):
        self.tilemap = pygame.image.load(data["tilemap"]["src"])
        size = self.tilemap.get_size()
        tilemap = data["tilemap"]
        self.tilemapSettings = {
            'start': ((size[0]/tilemap["totalColumns"])*tilemap["colStart"],(size[1]/tilemap["totalRow"])*tilemap["rowStart"]),
            'size': (size[0]/tilemap["totalColumns"],size[1]/tilemap["totalRow"]),
            'rows': tilemap["rows"],
            'columns': tilemap["columns"],
            'animation order': tilemap["animation order"]
            }
        self.animationSettings = data["animation"]

        self.pixelSize = param['pixelSize']
        self.scaleMultiplier = param['scaleMultiplier']
        self.newTileScale = param['pixelSize'] * param['scaleMultiplier']

        self.lastFrame = time.time()

        self.animation = 'BOTTOM WALK'
        self.lastAnimation = 'BOTTOM WALK'
        self.state = 1
        self.reversed = False
        self.animations = {
            'TOP WALK': [],
            'BOTTOM WALK': [],
            'RIGHT WALK': [],
            'LEFT WALK': [],
        }

        self.getFrames()

    def getFrames(self):
        for j in range(self.tilemapSettings['rows']):
            for i in range(self.tilemapSettings['columns']):
                location = (self.tilemapSettings['start'][0]+self.tilemapSettings['size'][0]*i, self.tilemapSettings['start'][1]+self.tilemapSettings['size'][1]*j)
                anim = self.tilemapSettings['animation order'].get(str(j))
                self.animations[anim].append(self.tilemap.subsurface(pygame.Rect(location, self.tilemapSettings['size'])))
        
        self.sprite = self.animations[self.lastAnimation][self.animationSettings['default state']]
    
    def setFrame(self):
        currentTime = time.time()   
        temps = currentTime-self.lastFrame
        if temps >= self.animationSettings['time']:
            self.lastFrame = currentTime

            if not self.reversed:
                self.state +=1
            else:
                self.state -=1

            if self.state >= self.tilemapSettings['columns']-1:
                self.reversed = True
            elif self.state == 0:
                self.reversed = False

            if self.animation == 'IDLE':
                sprite = self.animations[self.lastAnimation][self.animationSettings['default state']]
            else:
                sprite = self.animations[self.animation][self.state]

            self.sprite = pygame.transform.scale(sprite.convert_alpha(),(self.newTileScale,self.newTileScale))

    def setAnimation(self, animation):
        if self.animation != animation:
            self.lastAnimation = self.animation
            self.animation = animation
            self.state = self.animationSettings['default state']
            self.lastFrame = 0

class Entity(object):
    def __init__(self,param):
        """
        Entity object 

        param = {
            "name" : x,
            "entityRepr" : y,
            "pixelSize": 16,
            "scaleMultiplier": 6,
        }
        """
        self.param = param
        self.name = param['name']

        self.param['newPixelScale'] = self.param["pixelSize"]*self.param["scaleMultiplier"]

        self.x = param['x']
        self.y = param['y']

        self.rect = Rect(0,0,0,0)

        with open("entities/" + param['entityRepr'] + ".json","r") as file:
            self.data = json.load(file)

        self.col = self.data['collider']
        self.colAngleSize = self.col['angleSize']*self.param['newPixelScale']

        self.stats = self.data["stats"]
        self.stats["health"] = self.stats["maxHealth"]

        self.animator = Animator(self.data,param)

    def move(self, dtime):
        pass

    def draw(self, xStart, yStart, passThrough):
        xToDraw = self.x - xStart 
        yToDraw = self.y - yStart

        self.animator.setFrame()

        self.rect = Rect((xToDraw+self.col['offSets']['left'])*self.param['newPixelScale'], (yToDraw+self.col['offSets']['top'])*self.param['newPixelScale'], self.col['size']['width']*self.param['newPixelScale'], self.col['size']['height']*self.param['newPixelScale'])
        if passThrough['debug'] == True:
            pygame.draw.rect(passThrough['window'],(255,0,0),self.rect)

        passThrough['window'].blit(self.animator.sprite , (xToDraw*self.param['newPixelScale'], yToDraw*self.param['newPixelScale']))

    def drawHud(self, xPos, yPos, passThrough):
        scale = passThrough['HudScale']

        xToDraw = (self.x - xPos)*self.param['newPixelScale']
        yToDraw = (self.y - yPos)*self.param['newPixelScale']

        value = ((self.stats["health"] * 100) / self.stats["maxHealth"]) / 100 if self.stats["health"] > 0 else 0

        if self.stats["health"] < self.stats["maxHealth"]:
            rect = gFunction.createRectOutlined(value,xToDraw,yToDraw,100,20,6)
            pygame.draw.rect(passThrough['window'],(0,0,0),rect[0])
            pygame.draw.rect(passThrough['window'],(255,0,0),rect[1])

class EntitiesManager(object):
    def __init__(self):
        self.entities = []
        self.visibleEntities = []

    def addEntity(self,entity):
        self.entities.append(entity)

    def getVisibleEntities(self,coords):
        self.visibleEntities = []
        for entity in self.entities:
            if entity.x >= coords['xStart'] and entity.x <= coords['xEnd'] and entity.y >= coords['yStart'] and entity.y <= coords['yEnd']:
                self.visibleEntities.append(entity)

    def killEntity(self,name):
        for entity in self.entities:
            if entity.name == name:
                del self.entities[entity]

class Engine(object):
    def __init__(self,param):
        """
        Principal engine class

        engine do each loop:
            - transmit input
            - apply physical changes
            - Draw all visible entities
            - Draw all HUD

        param = {
            "height" : HEIGHT,
            "width" : WIDTH,
            "saves": "saves/saves",
            "pixelSize": 16,
            "scaleMultiplier": 6,
            "debug": False/True
        }
        """
        self.param = param
        self.debugMode = param["debug"]

        self.param['newPixelScale'] = self.param["pixelSize"]*self.param["scaleMultiplier"]
        self.calculatesTilesOnAxis()

        self.window = pygame.display.set_mode((param["width"], param["height"]),RESIZABLE)

        self.mainCamera = Camera()

        self.savePath = param["saves"]

        self.entitiesManager = EntitiesManager()

        #self.loadSaves()
        self.clock = pygame.time.Clock()

    def calculatesTilesOnAxis(self):  
        self.tilesOnX = int(self.param['width']/self.param['newPixelScale'])+1
        self.tilesOnY = int(self.param['height']/self.param['newPixelScale'])+1
    
    def loadSaves(self):
        with shelve.open(self.savePath) as data:
            if 'miscs' in data:
                if 'windowsHeight' in data['miscs'] and 'windowsWidth' in data['miscs']:
                    self.rezizeWindow(data['miscs']['windowsHeight'],data['miscs']['windowsWidth'],False)
            else:
                data['miscs'] = {}

    def rezizeWindow(self,h,w,saveData=True):
        self.window = pygame.display.set_mode((w, h),RESIZABLE)
        self.param['height'] = h
        self.param['width'] = w
        self.calculatesTilesOnAxis()
        self.player.setCameraOffset(self.tilesOnX-1,self.tilesOnY-1)

        if saveData:
            with shelve.open(self.savePath) as data:
                dictio = data['miscs']
                dictio['windowsHeight'] = h
                dictio['windowsWidth'] = w
                data['miscs'] = dictio

    def getTilesOnScreen(self):
        CameraPosX, CameraPosY = self.mainCamera.getPos()
        
        if CameraPosX < 0:
            xStart = 0
        else:
            xStart = math.floor(CameraPosX)
            
        if CameraPosY < 0:
            yStart = 0
        else:
            yStart = math.floor(CameraPosY)

        xEnd = xStart + self.tilesOnX + 1
        yEnd = yStart + self.tilesOnY + 1

        offx = round(CameraPosX - xStart,3)
        offy = round(CameraPosY - yStart,3)

        dic = {
            "yStart":yStart,
            "yEnd":yEnd,
            "xStart":xStart,
            "xEnd":xEnd,
            "offx":offx,
            "offy":offy,
        }

        self.ScreenToWorldCoords = dic

    def engineLoop(self):
        active = True
        while active:
            inputEvent = pygame.event.get()
            for event in inputEvent:
                if event.type == QUIT:
                    pygame.quit()
                    quit()
                if event.type == VIDEORESIZE:
                    self.rezizeWindow(event.h,event.w)
            
            self.main(inputEvent, pygame.key.get_pressed())

            self.applyPhysicalChanges(self.clock.get_time())

            self.Draws()

            self.DrawHUDs()

            pygame.display.update()
            self.clock.tick(120)

    def main(self,inputEvent,inputPressed):
        pass

    def applyPhysicalChanges(self,deltaTime):
        for entitie in self.entitiesManager.entities:
            entitie.move(self.clock.get_time())

    def Draws(self):
        self.getTilesOnScreen()
        self.DrawWorld()

        coords = self.ScreenToWorldCoords

        entities = self.entitiesManager.visibleEntities
        entities = sorted(entities, key=lambda ent: ent.y)

        for entitie in entities:
            entitie.draw(coords['xStart']+coords['offx'],coords['yStart']+coords['offy'],{'debug':self.debugMode,'window':self.window})
    
    def DrawWorld(self):
        self.window.fill((0,0,0)) 
        self.entitiesManager.getVisibleEntities(self.ScreenToWorldCoords)

    def DrawHUDs(self):
        coords = self.ScreenToWorldCoords
        for entitie in self.entitiesManager.entities:
            entitie.drawHud(coords['xStart']+coords['offx'],coords['yStart']+coords['offy'],{"window":self.window,"HudScale":self.param['HudScale']})
