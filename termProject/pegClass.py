
import math
import almostEqual
from dist import *
class Peg():
    gutter1=(40,135)
    gutter2=(460,135)
    gutter3=(40,565)
    gutter4=(460,565)
    gutters={gutter1,gutter2,gutter3,gutter4}
    def __init__(self,myRank):
        self.distance=0
        self.atRest=True
        self.hasCollided=False
        self.iVel,self.vel=0,0
        self.direction=0
        self.signX=1
        self.signY=1
        if myRank=="queen":
            self.colour="pink"
            self.mass=6
            self.r=8
            self.pts=50
        elif myRank=="lowRank":
            self.colour="orange"
            self.mass=5
            self.r=5
            self.pts=10
        elif myRank=="highRank":
            self.colour="grey"
            self.mass=5.5 
            self.r=6 
            self.pts=20 
        self.cx,self.cy=0,0
        self.velX,self.velY=0,0
        self.offsetAng=50
        self.inGutter=False
        
    def setPosition(self,psX,psY):
        self.cx=psX
        self.cy=psY
    
    def setVelocityUponCollision(self,strikerMass,strikerVel,direction,direction2,isElastic):
        self.atRest=False 
        self.direction=-1*(direction-2*self.offsetAng) #had to manually alter physics-based direction to avoid bugs
        self.signX*=-1
        self.signY*=-1
        if isElastic:
            self.direction=-direction
            self.iVel=((strikerMass*strikerVel+self.mass*self.vel)/(self.mass+strikerMass))
            return self.iVel #momentum conserved
        else:
            #elastic collision equations
            a=self.mass+((self.mass)**2)/strikerMass
            b=-(2*self.mass*strikerVel+(2*((self.mass)**2)*self.vel)/(strikerMass*10))
            c=self.mass*(self.vel)**2+2*self.mass*strikerVel*self.vel-((self.mass*self.vel)**2)/strikerMass
            if (b**2-4*a*c>=0):
                self.iVel=((-b+math.sqrt(abs((b**2-4*a*c))))/2*a)+300
                self.iVel%=700
            else:
                self.iVel=strikerVel
            return (strikerMass*strikerVel+self.mass*self.vel-self.mass*self.iVel)/(strikerMass*1.5)

    def whenStopped(self):
        #reset when peg is stopped
        if almostEqual.almostEqual3(self.vel,0):
            self.vel=0
            self.atRest=True
            self.distance=0
            self.direction=0
            self.iVel=0
            self.velX,self.velY=0,0

    def setSecondaryVelocity(self,direction,strikerNewVel,isElastic=False):
        if isElastic:
            self.direction+=-1*(direction+self.offsetAng)
        else:
            self.direction+=(direction+self.offsetAng*1)
        self.signX*=-1
        self.signY*=-1
        self.iVel=strikerNewVel
        self.atRest=False
    
    def checkInGutter(self): #check if peg in gutter
        for gutter in Peg.gutters:
            if dist(self.cx,self.cy,gutter[0],gutter[1])<self.r:
                self.inGutter=True
                break
    
    def retardVel(self,friction,maxWidth,maxHt,boardBoundary): 
        self.distance+=(self.vel*0.1) #log distance
        self.checkInGutter()
        if self.inGutter:
            self.vel=0
        else:
            if (self.iVel)**2-2*friction*9.8*self.distance>=0: #retard velocity
                self.vel=math.sqrt(((self.iVel)**2-2*friction*9.8*self.distance))
            else:
                self.vel*=0.9
            #ensures pegs don't exit the bpard
            if self.cx+self.r>maxWidth-boardBoundary+5 or self.cx-self.r<boardBoundary+4:
                self.signX=-1*self.signX
            if self.cy+self.r>maxHt-boardBoundary+88 or self.cy-self.r<boardBoundary+100:
                self.signY=-1*self.signY
            tempX=self.signX*(self.vel*math.cos(self.direction*(math.pi/180)))*0.01
            tempY=self.signY*(self.vel*math.sin(self.direction*(math.pi/180)))*0.01
            self.cx+=tempX
            self.cy+=tempY
        self.whenStopped()
        
        

