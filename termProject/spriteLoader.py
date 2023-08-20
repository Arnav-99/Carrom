
import math
from PIL import Image
#basic sprite creation template from https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
def loadSprites(app,angle):
    spritestrip = app.loadImage('arrowSprite.png') #arrows in various positions
    app.sprites = [ ]
    for i in range(9):
        pixelList=[]
        pixelDictTransformed=dict()
        pixelDict=dict()
        app.pixelListTransformed=list()
        sprite = spritestrip.crop((5+220*i, 35, 220+220*i, 250)) #get a sprite image
        pixels=list(sprite.getdata()) 
        for i in range(len(pixels)):
            if pixels[i]==(255,255,255,0): #replace white pixels with carrom board color pixels
                pixels[i]=(37,150,90,0)
        pixels.extend([(0,0,0,0) for j in range(25)]) #make the image square-dimensional
        rows=int(math.sqrt(len(pixels)))
        cols=rows
        for j in range(rows): #create a 2d list of rgba values
            addedRow=pixels[j*cols:(j+1)*cols]
            pixelList.append(addedRow)
        for row in range(len(pixelList)):
            addRow=[]
            for col in range(len(pixelList[0])): #encode the centre of the image as (0,0) as a reference in dictionary
                pixelDict[(col-cols//2,rows//2-row)]=pixelList[row][col]
                addRow.append((255,255,255,255))
            app.pixelListTransformed.append(addRow)
        for key in pixelDict:
            x0=key[0]
            y0=key[1] #now, use the (0,0) to rotate (row,col) pairs as vectors
            x1=(x0*math.cos(angle*math.pi/180)-y0*math.sin(angle*math.pi/180))
            y1=(y0*math.cos(angle*math.pi/180)+x0*math.sin(angle*math.pi/180))
            if x1<-107:
                x1=-107
            if x1>107:
                x1=107
            if y1>107:
                y1=107
            if y1<-107:
                y1=-107
            transKey=(x1,y1)
            pixelDictTransformed[transKey]=pixelDict[key] #map original key values to transformed position
        for key in pixelDictTransformed:
            nCol=key[0]
            nRow=key[1]
            col=round(nCol+cols//2) #decode (row,col) pairs, rounding if they got mapped to non-integer values
            row=round(rows//2-nRow)
            app.pixelListTransformed[row][col]=pixelDictTransformed[key]
            if app.pixelListTransformed[row][col]==(255,255,255,255):
                app.pixelListTransformed[row][col]=(37,150,90,0) #remove whitespace
        sprite=Image.new(mode="RGBA",size=sprite.size)
        for i in range(sprite.width): #reconstruct the rotated image
            for j in range(sprite.height):
                if app.pixelListTransformed[i][j]!=(255,255,255,255):
                    sprite.putpixel((i,j),app.pixelListTransformed[i][j])          
        sprite=app.scaleImage(sprite,1/4)
        app.sprites.append(sprite)
    app.spriteCounter = 0
