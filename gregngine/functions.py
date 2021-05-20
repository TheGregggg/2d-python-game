from pygame import *
import random

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

def createRectWithRoundCorner(left, top, width, height,radius):
    width = int(width)
    height = int(height)

    rects = [
        [(left+radius, top),(width-radius*2, height)],
        [(left, top+radius),(width, height-radius*2)]
    ]
    circles = [
        (left+radius, top+radius),
        (left+width-radius, top+radius),
        (left+radius, top+height-radius),
        (left+width-radius, top+height-radius)
    ]

    return (rects,circles)

def generateRandomString(length):
    """
    abc - 97 -> 123
    ABC - 65 -> 90
    012 - 48 -> 57
    """
    string = ''
    for i in range(length):
        nbr = random.randint(0,61)
        if nbr < 10:
            nbr += 48
        elif nbr >= 10 and nbr < 36:
            nbr += 55
        elif nbr >= 36:
            nbr += 61
        string += chr(nbr)
    
    return string

if __name__ == '__main__':
    print(generateRandomString(10))