import gregngine.engine as gregngine
import gregngine.functions as gFunction

import world

import math
import time

import pickle
import shelve
import json

import pygame 
from pygame.locals import *

actions = {
    "up":     pygame.K_UP,
    "down":   pygame.K_DOWN,
    "right":  pygame.K_RIGHT,
    "left":   pygame.K_LEFT,
    "sprint": pygame.K_LSHIFT,
    "attack": pygame.K_SPACE,
}

class Item():
    def __init__(self,param):
        """
        param = {
            itemRepr
        }
        """
    
        self.param = param

        with open("items/" + param['itemRepr'] + ".json","r") as file:
            self.data = json.load(file)

        self.name = self.data['displayedName']
        
        tilemap = self.data['tilemap']
        self.tilemap = pygame.image.load(self.data["tilemap"]["src"])
        size = self.tilemap.get_size()

        self.tilemapSettings = {
            'start': ((size[0]/tilemap["totalColumns"])*tilemap["colStart"],(size[1]/tilemap["totalRow"])*tilemap["rowStart"]),
            'size': (size[0]/tilemap["totalColumns"],size[1]/tilemap["totalRow"]),
        }
        
        location = (self.tilemapSettings['start'][0], self.tilemapSettings['start'][1])
        self.sprite = self.tilemap.subsurface(pygame.Rect(location, self.tilemapSettings['size']))

class Inventory():
    def __init__(self):
        self.slots = [[None,None,None],[None,None,None],[None,None,None]]
        self.hands = None
    
    def drawHud(self,passThrough):
        scale = passThrough['HudScale']

        width, height = passThrough['window'].get_size()

        coords = {
            'right': 8,
            'top': 8,
            'height': 50,
            'width': 50
        }

        s = pygame.Surface((coords['width']*scale,coords['height']*scale))  
        s.set_alpha(128)                
        s.fill((0,0,0))           
        passThrough['window'].blit(s, (width - coords['width']*scale - coords['right']*scale, coords['top']*scale))

        if self.hands is not None:
            if self.hands.data['type'] == 'sword':
                itemScale = (int(coords['width']*scale/1.5),int(coords['height']*scale*1.5))

            sprite = pygame.transform.scale(self.hands.sprite.convert_alpha(),itemScale)
            passThrough['window'].blit(sprite, (width - coords['width']*scale - coords['right']*scale, coords['top']*scale))

class Player(gregngine.Entity):
    def __init__(self, param):
        super().__init__(param)

        self.speed = self.stats["normalSpeed"]
        self.running = False

        self.camera = None
        self.inventory = Inventory()
        self.inventory.hands = Item({"itemRepr":'normal_sword'})

        self.velocity = {"x": 0, "y": 0}

        self.health = self.stats["maxHealth"]
        self.energy = self.stats["maxEnergy"]

        self.lastAttackTime = time.time()

        self.animator.setFrame()

    def drawHud(self, xPos, yPos, passThrough):
        scale = passThrough['HudScale']

        x = ((self.energy * 100) / self.stats["maxEnergy"]) /100 if self.energy > 0 else 0

        rect = gFunction.createRectOutlined(x, 8*scale, 8*scale, 100*scale, 20*scale, 4*scale)
        pygame.draw.rect(passThrough['window'],(0,0,0),rect[0])

        if x > 0:
            pygame.draw.rect(passThrough['window'],(0,80,255),rect[1])
        
        self.inventory.drawHud(passThrough)

    def move(self,dTime):
        x,y = self.velocity['x'],self.velocity['y']

        if self.running and self.energy > 0 and (x != 0 or y !=0):
            x,y = x*self.stats["maxSpeed"],y*self.stats["maxSpeed"]
            if self.energy < 1:
                self.energy -= 10
            else:
                self.energy -= 30*dTime*0.001
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

    def setVelocity(self,x,y):
        self.velocity = {"x": x, "y": y}

    def increaseEnergy(self,dtime):
    
        if self.energy < self.stats['maxEnergy']:
            self.energy += 10*dtime*0.001
            if self.stats['maxEnergy'] < self.energy:
                self.energy = self.stats['maxEnergy']

    def setCameraOffset(self,x,y):
        self.camera.xOffset = -(x/2) + self.param['x']
        self.camera.yOffset = -(y/2) + self.param['y']

    def attack(self):
        currentTime = time.time()   
        if currentTime-self.lastAttackTime >= self.stats['atkPerSec']:
            self.lastAttackTime = currentTime 

            dico = {
                'TOP WALK': 'top',
                'BOTTOM WALK': 'bottom',
                'RIGHT WALK': 'right',
                'LEFT WALK': 'left',
            }

            anim = self.animator.animation if self.animator.animation != 'IDLE' else self.animator.lastAnimation
            lookingTo = dico.get(anim)

            attackRect = self.rect

            if lookingTo == 'left':
                attackRect.left -= self.param['newPixelScale']
            elif lookingTo == 'right':
                attackRect.left += self.param['newPixelScale']
            elif lookingTo == 'top':
                attackRect.top -= self.param['newPixelScale']
            elif lookingTo == 'bottom':
                attackRect.top += self.param['newPixelScale']

            return {'attackRect':attackRect,'damage':self.stats['atkBaseDamage']}

        else:
            return None

class Engine(gregngine.Engine):
    def __init__(self, param):
        super().__init__(param)

        self.world = world
        self.newPixelScale = self.param['newPixelScale']

        self.collisionsDistance = 2.2
        self.collisionsDistance *= self.newPixelScale
        self.collisions = {}

        self.rezizeSprites()

        playerParam = {
            "name" : 'player',
            "entityRepr" : 'player',
            "pixelSize": self.param['pixelSize'],
            "scaleMultiplier": self.param['scaleMultiplier'],
            'x':6,
            'y':6}
        self.player = Player(playerParam)
        self.player.camera = self.mainCamera
        self.mainCamera.setPos(0,0)
        self.player.setCameraOffset

        self.entitiesManager.addEntity(self.player)
        self.entitiesManager.addEntity(gregngine.Entity({"name" : "slim","entityRepr" : "slim","pixelSize": self.param['pixelSize'],"scaleMultiplier": self.param['scaleMultiplier'],'x':10,'y':10}))

    def rezizeSprites(self):
        elems = ["g","s","r"]
        for sprite in elems:
            self.world.sprites[sprite] = pygame.transform.scale(self.world.sprites[sprite].convert_alpha(),(self.newPixelScale,self.newPixelScale))

    def main(self,inputEvent,inputPressed):
        self.playerInput(inputPressed)
        
    def playerInput(self,inputPressed):
        playerSpeedY,playerSpeedX = 0, 0

        walls = self.checkWorld()

        if inputPressed[actions["sprint"]]:
            self.player.running = True
            if self.player.energy > 0:
                self.player.animator.animationSettings['time'] = self.player.animator.animationSettings['maxSpeed']
            else:
                self.player.animator.animationSettings['time'] = self.player.animator.animationSettings['normalSpeed']
        else:
            self.player.running = False
            self.player.animator.animationSettings['time'] = self.player.animator.animationSettings['normalSpeed']

        self.player.increaseEnergy(self.clock.get_time())

        if inputPressed[actions["up"]]:
            if (inputPressed[actions["left"]] and inputPressed[actions["right"]]) or (not inputPressed[actions["left"]] and not inputPressed[actions["right"]]):
                self.player.animator.setAnimation('TOP WALK')
            if "Top" not in walls:
                playerSpeedY -= 1

        if inputPressed[actions["down"]]:
            if (inputPressed[actions["left"]] and inputPressed[actions["right"]]) or (not inputPressed[actions["left"]] and not inputPressed[actions["right"]]):
                self.player.animator.setAnimation('BOTTOM WALK')
            if "Bottom" not in walls:
                playerSpeedY += 1

        if inputPressed[actions["left"]]:
            if not (inputPressed[actions["left"]] and inputPressed[actions["right"]]):
                self.player.animator.setAnimation('LEFT WALK')
            if "Left" not in walls:
                playerSpeedX -= 1

        if inputPressed[actions["right"]]:
            if (not inputPressed[actions["left"]] and inputPressed[actions["right"]]):
                self.player.animator.setAnimation('RIGHT WALK')
            if "Right" not in walls:
                playerSpeedX += 1

        if playerSpeedX == 0 and playerSpeedY == 0:
            self.player.animator.setAnimation('IDLE') 
        
        if playerSpeedX != 0 or playerSpeedY != 0:
            self.player.setVelocity(playerSpeedX, playerSpeedY)
        
        # attack code

        if inputPressed[actions["attack"]]:
            attackinfo = self.player.attack()

            if attackinfo is not None:
                for entity in self.entitiesManager.visibleEntities:
                    if attackinfo['attackRect'].colliderect(entity.rect) and entity.data['type'] == 'monster':
                        print("Hit " + entity.name)
                        entity.stats['health'] -= attackinfo['damage']

    def DrawWorld(self):
        super().DrawWorld()

        widthBy2 = self.param['width']/2
        heightBy2 = self.param['height']/2

        self.collisions = {}

        coords = self.ScreenToWorldCoords

        for y_index,y in enumerate(self.world.world[coords['yStart']:coords['yEnd']]):
            for x_index,x in enumerate(y[coords['xStart']:coords['xEnd']]):
                coord = ((x_index*self.newPixelScale)-(coords['offx']*self.newPixelScale) , (y_index*self.newPixelScale)-(coords['offy']*self.newPixelScale))
                
                wall = self.world.walls[coords['yStart']+y_index][coords['xStart']+x_index]
                if wall == " ":
                    self.window.blit(self.world.sprites[x], coord)

                else:
                    self.window.blits(((self.world.sprites[x], coord),(self.world.sprites[wall], coord)))
                    dist = math.hypot(coord[0]-widthBy2, coord[1]-heightBy2)
                    if abs(dist) < self.collisionsDistance:
                        self.collisions[(y_index,x_index)] = coord
                    
                        if self.debugMode == True:
                            pygame.draw.rect(self.window,(255,0,0),Rect(coord,(self.newPixelScale,self.newPixelScale)))
        
    def checkWorld(self):
        walls = []

        yPlayerMin, yPlayerMax = math.floor(self.player.y), math.ceil(self.player.y)
        xPlayerMin, xPlayerMax = math.floor(self.player.x), math.ceil(self.player.x)

        points = {
            "topleft": {
                "value": 0,
                "pos": self.player.rect.topleft
            },
            "topleftbottom": {
                "value": 0,
                "pos": (self.player.rect.topleft[0],self.player.rect.topleft[1]+self.player.colAngleSize)
            },
            "toplefttop": {
                "value": 0,
                "pos": (self.player.rect.topleft[0]+self.player.colAngleSize,self.player.rect.topleft[1])
            },

            "topright": {
                "value": 0,
                "pos": self.player.rect.topright
            },
            "toprighttop": {
                "value": 0,
                "pos": (self.player.rect.topright[0]-self.player.colAngleSize,self.player.rect.topright[1])
            },
            "toprightbottom": {
                "value": 0,
                "pos": (self.player.rect.topright[0],self.player.rect.topright[1]+self.player.colAngleSize)
            },

            "bottomright": {
                "value": 0,
                "pos": self.player.rect.bottomright
            },
            "bottomrighttop": {
                "value": 0,
                "pos": (self.player.rect.bottomright[0],self.player.rect.bottomright[1]-self.player.colAngleSize)
            },
            "bottomrightbottom": {
                "value": 0,
                "pos": (self.player.rect.bottomright[0]-self.player.colAngleSize,self.player.rect.bottomright[1])
            },

            "bottomleft": {
                "value": 0,
                "pos": self.player.rect.bottomleft
            },
            "bottomlefttop": {
                "value": 0,
                "pos": (self.player.rect.bottomleft[0],self.player.rect.bottomleft[1]-self.player.colAngleSize)
            },
            "bottomleftbottom": {
                "value": 0,
                "pos": (self.player.rect.bottomleft[0]+self.player.colAngleSize,self.player.rect.bottomleft[1])
            }
        }

        for collisions in self.collisions.keys():
            rect = Rect(self.collisions[collisions],(self.newPixelScale,self.newPixelScale))

            for point in points.keys():
                if points[point]["value"] == 0:
                    points[point]["value"] = rect.collidepoint(points[point]["pos"])
        
        for entity in self.entitiesManager.visibleEntities:
            if entity.data['type'] != "player":
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

        return walls

engineParameters = {
    "height" : 800,
    "width" : 1200,
    "saves": "saves/saves",
    "pixelSize": 16,
    "scaleMultiplier": 6,
    "HudScale": 1.5,
    "debug": False
}
engine = Engine(engineParameters)
engine.engineLoop()