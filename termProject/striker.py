import almostEqual
import math
from dist import *

class Striker():
    impactTime=0.1
    gutter1=(42,142)
    gutter2=(456,141)
    gutter3=(42,556)
    gutter4=(456,555)
    gutters={gutter1,gutter2,gutter3,gutter4}
    def __init__(self):
        self.direction=0
        self.spin=0
        self.force=50000
        self.mass=30
        self.vel=0
        self.isStationary=True
        self.distance=0
        self.refTime=0
        self.timeOfMotion=0
        self.x,self.y=100,150
        self.signX=1
        self.signY=1
        self.velX,self.velY=0,0
        self.spinTime=0
        self.inGutter=False
        self.radius=11
        self.dirChange=0
    
    def playTurn(self,spin,force,direction,startX,startY):
        self.spin=spin
        self.force=force
        self.direction=direction
        self.iVel=(0.1*self.force)/self.mass
        self.isStationary=False
        self.x=startX
        self.y=startY

    def whenMoving(self): 
        if almostEqual.almostEqual(self.vel,0.1):
            self.isStationary=True
            self.vel=0
            self.resetWhenStopped()
            self.signX=1
            self.signY=1

    def resetWhenStopped(self):
        self.direction=0
        self.spin=0
        self.iVel=0
        self.distance=0
        self.timeOfMotion=0
    
    def setVelocityUponCollision(self,direction,strikerNewVel,isElastic=False): 
        if isElastic: #direction change if collision elastic
            self.direction=-direction
            self.iVel=strikerNewVel
        else: #none if inelastic
            self.direction+=0
            self.iVel=strikerNewVel/10

    def checkInGutter(self): #checks if the striker is in gutter
        for gutter in Striker.gutters:
            if dist(self.x,self.y,gutter[0],gutter[1])<self.radius:
                self.inGutter=True
                break

    def retardVel(self,friction,maxWidth,maxHt,boardBoundary):
        self.checkInGutter()
        if self.isStationary or self.inGutter: #set velocity to 0 when not moving
            self.vel=0
        else:
            self.distance+=0.05*self.vel #log distance travelled
            if (self.iVel)**2-2*friction*9.8*self.distance>=0:
                self.vel=math.sqrt(abs((self.iVel)**2-2*friction*9.8*self.distance))
            else:
                self.vel*=0.9 #if the friction formula yields unwieldy results manually reduce velocity
            #applying lateral motion that is accelerated using exponential function
            self.x+=self.signX*(self.spin*math.e**(-2-self.spinTime))
            if (self.direction>180 or self.direction<0) and self.dirChange==0:
                self.signY=-1
                self.dirChange+=1
            tempX=self.signX*(self.vel*math.cos(self.direction*(math.pi/180)))*0.1
            tempY=self.signY*(self.vel)*0.1
            self.x-=tempX
            self.y-=tempY
            if self.x+11>maxWidth-boardBoundary or self.x-11<boardBoundary:
                self.signX=-1*self.signX
            elif self.y+11>maxHt-boardBoundary+90 or self.y-11<boardBoundary+100:
                self.signY=-1*self.signY #change y component dir when out of bounds
            self.spinTime+=0.001

        

    
    
    
