from pygame import *

def normalize(x,y):
    if x != 0 and y != 0:
        x /= 1.5
        y /= 1.5

        x,y = round(x,2),round(y,2)
    
    return x,y

def createRectOutlined(value ,xPos ,yPos , width, height, outlineSize):
    outline = Rect(xPos                   ,yPos                   , width                , height)
    rect    = Rect(xPos + (outlineSize/2) ,yPos + (outlineSize/2) , value*(width - outlineSize), height - outlineSize)
  
    return (outline,rect)

def createRectFromRight(screenWidth,right, top, width, height):
    rect = Rect(screenWidth - width - right, top, width, height)
    return rect