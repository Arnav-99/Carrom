from cmu_112_graphics import *
import pegClass
import random
import math
from striker import *
from Player import *
import spriteLoader
import almostEqual
from PButton import *

def appStarted(app):
    app.playButton=playingButton("PLAY!")
    app.mouseCounts=0
    app.settingPosition=True
    app.helpButton=helpButton("HELP")
    #https://myloview.com/poster-carrom-board-icon-no-D91C98C
    app.image1 = app.loadImage('carromBoardImage.png')
    app.mode="startMode"
    app.friction=1
    spriteLoader.loadSprites(app,0) #initializing spritesheet
    app.pegsInGutter=set() #stores those pegs currently in gutter
    app.player1=Player()
    app.player2=Player()
    app.player1.isTurn=True
    app.players=[app.player1,app.player2]
    app.scaleImage(app.image1, 0.5)
    app.striker=Striker()
    createPegsList(app) #initializes the pegs on board
    initiatePegs(app) #creates pegs in a somewhat circular pattern at initialisation
    app.timerDelay=1
    app.paused=True
    app.timesCalled=0
    app.atLeastOneCollision=0 
    app.boardBoundary=25
    app.startX,app.startY=0,0
    app.pointerPulsation=0
    app.boardWidth=500
    app.boardHeight=500
    app.gameOver=False
    app.winningPlayer=None
    app.forceSliderColour,app.spinSliderColour,app.directionSliderColour,app.frictionSliderColour="green","yellow","white","blue"
    app.forceSliderX,app.spinSliderX,app.directionSliderX,app.frictionSliderX=525,525,525,525
    app.sliders={"force":[app.forceSliderX,312],"friction":[app.frictionSliderX,312],"spin":[app.spinSliderX,437],"direction":[app.directionSliderX,562]}
    app.sliderR=10
    app.countPegs=0

#game mode is the main mode

def gameMode_mouseDragged(app,event):
    if app.paused: #allows player to set striker position
        if app.settingPosition:
            if (not (event.x<0 or event.x>500)) and (not (event.y<100 or event.y>600)):
                app.startX,app.startY=event.x,event.y
            if (not (app.startX<25 or app.startX>490)) and (not (app.startY<125 or app.startX>590)):
                app.striker.x=app.startX
                app.striker.y=app.startY
        if app.mouseCounts>0: #once an initial position is set, they can alter the sliders 
            for slider in app.sliders:
                x0,y0=app.sliders[slider][0],app.sliders[slider][1]
                x1,y1=event.x,event.y
                if dist(x0,y0,x1,y1)<app.sliderR:
                    propX=event.x
                    if propX<525:
                        propX=525
                    elif propX>675:
                        propX=675
                    if slider=="force":
                        app.striker.force=50000+(propX-525)*100
                        app.forceSliderX=propX
                    elif slider=="spin":
                        app.striker.spin=0+(propX-525)*0.1
                        app.spinSliderX=propX
                    elif slider=="friction":
                        app.friction=3+(propX-525)*0.1
                        app.frictionSliderX=propX
                    elif slider=="direction":
                        app.striker.direction=0+(propX-525)*2
                        app.directionSliderX=propX
                    break

def gameMode_mouseReleased(app,event): #loads sprites based on user's entered direction
    app.mouseCounts+=1
    #app.settingPosition=False
    spriteLoader.loadSprites(app,app.striker.direction)

def gameMode_timerFired(app): 
    #updates slider values
    app.sliders={"force":(app.forceSliderX,312),"friction":(app.frictionSliderX,312),"spin":(app.spinSliderX,437),"direction":(app.directionSliderX,562)}
    if not app.gameOver:
        if app.pointerPulsation%(int(5*(50000/app.striker.force)))==0: #pulsate arrow based on applied force
            app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)
        app.pointerPulsation+=1
        if app.playButton.isButtonPressed() and app.paused: #play turn if button is pressed
            app.striker.playTurn(float(app.striker.spin),int(app.striker.force),int(app.striker.direction),app.startX,app.startY)
            app.paused=False
    if (not app.paused) and (not app.gameOver):
        checkForAndHandleCollision(app)
        for j in range(len(app.pegsList)):
            checkForAndHandleCollision(app) 
            app.pegsList[j].retardVel(app.friction,app.boardWidth,app.boardHeight,app.boardBoundary)
        app.striker.retardVel(app.friction,app.boardWidth,app.boardHeight,app.boardBoundary)
        checkForAndHandleCollision(app)
        app.striker.whenMoving() #checks if striker has stopped and resets if so
        checkForAndHandleCollision(app) 
        if app.atLeastOneCollision>0 or not (almostEqual.almostEqual(app.striker.x,app.startX) and\
        almostEqual.almostEqual(app.striker.y,app.startY)):
        #this checks whether a turn has ended, only when there has at least been one collision or 
        #when the striker has moved from its starting position, to account for no-collision turns
            checkIfTurnEnded(app) 
                 #play next turn
        #note: multiple calls to check for collision as small movements can generate a collision,
        #and if not repeatedly checked, caused undetected collision

def checkIfTurnEnded(app): #checks if every peg has stopped
    for pegIndex in range(len(app.pegsList)):
        if not app.pegsList[pegIndex].vel==0:
            return
    if not app.striker.vel==0:
        return
    else:
        currPlayer=getCurrPlayerTurn(app)
        app.countPegs=0
        if currPlayer.hasStruckQueen: #if a queen was struck in the previous turn, the new turn must have a score
            for peg in app.pegsList:
                if peg.inGutter and not (peg in app.pegsInGutter):
                    app.countPegs+=1
            if app.countPegs==0:
                app.pegsInGutter.remove(app.pegsList[0]) #the queen is removed from the gutters set
                currPlayer.hasStruckQueen=False
                app.showMessage("Hard luck, you lost the queen.")
            else:
                currPlayer.currScore+=app.pegsList[0].pts
                app.pegsList[0].inGutter=True #add queen to gutter
                app.showMessage("You got the queen!")
                currPlayer.hasStruckQueen=False
        app.paused=True #pause timer if the turn has ended
        #resets all other settings for the next turn
        app.playButton.isPressed=False
        app.pointerPulsation=0
        app.mouseCounts=0
        app.striker.direction=90
        app.striker.force=50000
        app.striker.spin=0
        app.forceSliderX,app.spinSliderX,app.directionSliderX,app.frictionSliderX=525,525,525,525
        app.atLeastOneCollision=0 #reset for next turn
        app.startX,app.startY=0,0
        for peg in range(len(app.pegsList)):
            #update current player score based on pegs newly added to gutter
            if app.pegsList[peg].inGutter and not app.pegsList[peg] in app.pegsInGutter:
                if not (app.pegsList[peg] is app.pegsList[0]):
                    app.pegsInGutter.add(app.pegsList[peg])
                    currPlayer.currScore+=app.pegsList[peg].pts
                else:
                    currPlayer.hasStruckQueen=True

        if not currPlayer.hasStruckQueen: #only change the turn if the player has not struck queen
            for playerInd in range(len(app.players)):
                app.players[playerInd].isTurn=not app.players[playerInd].isTurn #switch turns
        else:
            app.showMessage("Play again! Strike another peg, any peg, to get the queen!")
        if app.striker.inGutter: #penalty if striker is guttered
            if currPlayer.currScore==0:
                m="You fouled! Thankfully you have no points to be penalized :)!"
                app.showMessage(m)
            else:
                m="YOU FOULED! You have been penalized!"
                app.showMessage(m)
            if currPlayer.currScore>=10: #penalize for fouls
                currPlayer.currScore-=10
            elif currPlayer.currScore>=20:
                currPlayer.currScore-=20
        app.striker.inGutter=False
        if currPlayer.currScore>=160:
            app.winningPlayer=currPlayer
            app.gameOver=True

def getCurrPlayerTurn(app):
    for j in range(len(app.players)):
        if app.players[j].isTurn==True:
            if j==0:
                return app.player1
            else:
                return app.player2

def gameMode_keyPressed(app,event):
    if (event.key=="R" or event.key=="r") and app.gameOver:
        appStarted(app)

def checkForAndHandleCollision(app,isElastic=False):
    x3=app.striker.x
    y3=app.striker.y
    for j in range(len(app.pegsList)):
        for k in range(len(app.pegsList)):
            if j==k:
                continue
            x1=app.pegsList[j].cx
            x2=app.pegsList[k].cx
            y1=app.pegsList[j].cy
            y2=app.pegsList[k].cy
            if almostEqual.almostEqual(dist(x1,y1,x2,y2)-app.pegsList[k].r-app.pegsList[j].r,0)\
            and not (app.pegsList[j].vel==0 and app.pegsList[k].vel==0)\
            and not (app.pegsList[j].inGutter or app.pegsList[k].inGutter): #while checking for closeness,ensure pegs aren't stationary/in gutter
                app.atLeastOneCollision+=1
                #here we note down the colliding elements of the board
                colElem1=app.pegsList[j]
                colElem2=app.pegsList[k]
                direction=math.tan(0.25*((y1-y2)/(x1-x2)))*180/math.pi #direction depends on the orientation of the collision
                if colElem1.signX*colElem2.signX==-1 or colElem1.signY*colElem2.signY==-1: #the definition of an elastic collision
                    isElastic=True
                else:
                    pass
                handleCollision(app,direction,direction,isElastic,colElem1,colElem2)
            if almostEqual.almostEqual(dist(x1,y1,x3,y3),11+app.pegsList[j].r) and not (app.pegsList[j].inGutter or app.striker.inGutter): 
                #a separate check for peg-striker collisions
                app.atLeastOneCollision+=1
                colElem1=app.pegsList[j]
                colElem2=app.striker
                direction=math.tan(0.25*((y1-y3)/(x1-x3)))*180/math.pi
                if colElem1.signX*colElem2.signX==-1 or colElem1.signY*colElem2.signY==-1:
                    isElastic=True
                handleCollision(app,direction,direction,isElastic,colElem1,colElem2)

def setSuitableDir(app,x1,x2,y1,y2,colElem1,colElem2):
    d1Dir,d2Dir=0,0
    if colElem2 is app.striker:
        d1Dir=getDir(app,x1,x2,y1,y2,colElem1)
        d2Dir=0.25*d1Dir #direction change of the heavier striker is lesser
    else:
        if colElem1.vel>colElem2.vel:
            d2Dir=getDir(app,x1,x2,y1,y2,colElem2,colElem2)
            d1Dir=1/2*d2Dir #direction change of faster colliding element is lesser
        else:
            d1Dir=getDir(app,x1,x2,y1,y2,colElem1,colElem1)
            d2Dir=1/2*d1Dir
    return (d1Dir,d2Dir)

def getDir(app,x1,x2,y1,y2,colElem1,isFound=False):
    n=1
    d1Dir=0
    d1Dir=n*0.75*abs(math.tan((y1-y2)/(x1-x2)))*180/math.pi
    return d1Dir

def handleCollision(app,direction1,direction2,isElastic,colElem1,colElem2): #function performs conservation of momentum
    #set initial velocity for the first collising element, fixed to be a peg of some sort
    strikerNewVel=colElem1.setVelocityUponCollision(colElem2.mass,colElem2.vel,direction1,colElem2.direction,isElastic)
    #calling different methods based on peg-peg or peg-striker collision to set initial velocity for 2nd element
    
    if colElem2 is app.striker:
        colElem2.setVelocityUponCollision(direction1,strikerNewVel,isElastic)
    else:
        colElem2.setSecondaryVelocity(direction1,(strikerNewVel+200)%700,isElastic)

def createPegsList(app): #creates pegs
    app.pegsList=[pegClass.Peg("queen")]
    app.pegsList.extend([pegClass.Peg("highRank") for i in range(9)])
    app.pegsList.extend([pegClass.Peg("lowRank") for i in range(9)])

#a backup version of the initiatePegs function follows:
def initiatePegs(app):
    #aim: find the smallest possible bounding circle for the initial peg distribution
    lCircleCx=app.width/2-100
    lCircleCy=app.height/2
    for pegs in range(len(app.pegsList)):
        if app.pegsList[pegs].colour=="pink":
            #pink queen peg must always be at centre
            app.pegsList[pegs].setPosition(app.width/2,app.height/2)
    initiatePegsHelper(app,lCircleCx,lCircleCy)

def initiatePegsHelper(app,lCircleCx,lCircleCy,n=1):
    #this order the pegs in the pegs list in decreasing order of size
    tempPegsList=list()
    i=0
    while i<len(app.pegsList):
        if app.pegsList[i].colour=="grey":
            tempPegsList.append(app.pegsList[i])
        i+=1
    i=0
    while i<len(app.pegsList):
        if app.pegsList[i].colour=="orange":
            tempPegsList.append(app.pegsList[i])
        i+=1
    while(True): #try different circle sizes
        lCircleRad=n*5
        result=tryPegPositions(app,lCircleRad,lCircleCx,lCircleCy,tempPegsList)
        if result==None:
            n+=0.01 #increase bounding circle size if prev size didn't work
        else:
            break
#backup version ends

def tryPegPositions(app,lCircleRad,lCircleCx,lCircleCy,tempPegsList,piece=0):
    if piece>=len(tempPegsList)-1:
        return "done"
    else:
        for failLim in range(3): #failure limit: try to place in 3 positions else give up
            #choose random abscissa within bounds of larger circle
            testX=random.uniform(lCircleCx-lCircleRad+tempPegsList[piece].r,\
            lCircleCx+lCircleRad-tempPegsList[piece].r)
            #choose random ordinate within bounds of larger circle
            testY=random.uniform(lCircleCy-lCircleRad+tempPegsList[piece].r,\
            lCircleCy+lCircleRad-tempPegsList[piece].r)
            
            if isValidPos(app,testX,testY,piece,tempPegsList):
                tempPegsList[piece].setPosition(testX,testY)
                result=tryPegPositions(app,lCircleRad,lCircleCx,lCircleCy,tempPegsList,piece+1)
                if result!=None:
                    return result
                tempPegsList[piece].setPosition(0,0) #backtrack case
        return None

def gameMode_mousePressed(app,event):
    if app.paused and not app.playButton.isButtonPressed():
        if dist(event.x,event.y,app.playButton.x,app.playButton.y)<app.playButton.size:
            if isValidStrikerPos(app):
                app.playButton.changeState()
            else:
                app.showMessage("Enter a valid striker position!")

def isValidStrikerPos(app):
    if 108<app.striker.x<389 and 205<app.striker.y<487:
        return False
    elif app.striker.x<82 or app.striker.x>425:
        return False
    elif app.striker.y<180 or app.striker.y>515:
        return False
    else:
        return True

def isValidPos(app,testX,testY,piece,tempPegsList):
    #basically to ensure that candidate pos is not alreadt occupied by peg
    for pegIndex in range(len(app.pegsList)):
        if app.pegsList[pegIndex] is tempPegsList[piece]:
            continue
        test2X=app.pegsList[pegIndex].cx
        test2Y=app.pegsList[pegIndex].cy
        if dist(testX,testY,test2X,test2Y)<(app.pegsList[piece-1].r+app.pegsList[pegIndex].r):
            return False
    return True

def dist(testX,testY,test2X,test2Y):
    return math.sqrt((test2Y-testY)**2+(test2X-testX)**2)

def gameMode_redrawAll(app,canvas):
    canvas.create_image(250, 350, image=ImageTk.PhotoImage(app.image1))
    if not app.striker.inGutter:
        canvas.create_oval(app.striker.x-11,app.striker.y-11,app.striker.x+11,app.striker.y+11,fill="yellow")
    for pegIndex in range(len(app.pegsList)):
        if not app.pegsList[pegIndex].inGutter:
            r=app.pegsList[pegIndex].r
            cx=app.pegsList[pegIndex].cx
            cy=app.pegsList[pegIndex].cy
            colour=app.pegsList[pegIndex].colour
            canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill=colour)

    sprite = app.sprites[app.spriteCounter]
    if app.paused:
        canvas.create_image(app.striker.x, app.striker.y-30, image=ImageTk.PhotoImage(sprite))
    canvas.create_rectangle(0,0,245,100,fill="yellow",width=10,outline="black")
    canvas.create_rectangle(255,0,500,100,fill="light blue",width=10,outline="black")
    canvas.create_text(122.5,40,text="PLAYER 1",font="Arial 20 bold")
    canvas.create_text(367.5,40,text="PLAYER 2",font="Arial 20 bold")
    canvas.create_text(122.5,75,text=str(app.player1.currScore),font="Arial 16 bold")
    canvas.create_text(367.5,75,text=str(app.player2.currScore),font="Arial 16 bold")
    displayMessage(app,canvas)
    canvas.create_rectangle(500,0,700,700,fill="bisque")
    if app.paused:
        createControlsPanel(app,canvas)

def createControlsPanel(app,canvas):
    canvas.create_text(600,125,text="FRICTION",font="Arial 16 bold")
    canvas.create_line(525,187,675,187,width=4)
    canvas.create_rectangle(app.frictionSliderX-app.sliderR,187-app.sliderR,app.frictionSliderX+app.sliderR,187+app.sliderR,fill=app.frictionSliderColour)
    canvas.create_text(600,250,text="FORCE",font="Arial 16 bold")
    canvas.create_line(525,312,675,312,width=4)
    canvas.create_rectangle(app.forceSliderX-app.sliderR,312-app.sliderR,app.forceSliderX+app.sliderR,312+app.sliderR,fill=app.forceSliderColour)
    canvas.create_text(600,375,text="SPIN",font="Arial 16 bold")
    canvas.create_line(525,437,675,437,width=4)
    canvas.create_rectangle(app.spinSliderX-app.sliderR,437-app.sliderR,app.spinSliderX+app.sliderR,437+app.sliderR,fill=app.spinSliderColour)
    canvas.create_text(600,500,text="DIRECTION",font="Arial 16 bold")
    canvas.create_line(525,562,675,562,width=4)
    canvas.create_rectangle(app.directionSliderX-app.sliderR,562-app.sliderR,app.directionSliderX+app.sliderR,562+app.sliderR,fill=app.directionSliderColour)
    (x,y,size)=app.playButton.getDimensions()
    canvas.create_rectangle(x-size,y-size,x+size,y+size,fill="green")
    canvas.create_text(x,y,text=app.playButton.message,font="Arial 14 bold")
    canvas.create_text(x,y-25,text=app.striker.force)

def displayMessage(app,canvas,count=0):
    if not app.gameOver:
        for playerInd in range(len(app.players)): #cheking for which player's turn
            if app.players[playerInd].isTurn:
                if app.players[playerInd] is app.player1:
                    the_text="It is player 1's turn"
                else:
                    the_text="It is player 2's turn"
                    break
        canvas.create_text(250,620,text=the_text,font="Arial 18 bold")
    else:
        for player in range(len(app.players)):
            if app.players[player].currScore>=10:
                the_text=f"Player {player+1} has won! Press R to reset"
                break
        canvas.create_text(250,630,text=the_text,font="Arial 18 bold")

###############starting mode################

def startMode_redrawAll(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height,fill="light blue")
    canvas.create_text(app.width/2,app.height/2,text="Let's Play Carrom! Press any key to start, OR get",font="Arial 26 bold")
    x,y,size=app.helpButton.getDimensions()
    canvas.create_rectangle(x-size,y-size,x+size,y+size,fill="purple")
    canvas.create_text(x,y,text=app.helpButton.message,font="Arial 20 bold")

def startMode_mousePressed(app,event):
    x0,y0=app.helpButton.x,app.helpButton.y
    x1,y1=event.x,event.y
    if dist(x0,y0,x1,y1)<app.helpButton.size:
        app.mode="helpMode"

def startMode_keyPressed(app,event):
    app.mode="gameMode"

###############starting mode################


###############help mode#################

def helpMode_redrawAll(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height,fill="bisque3")
    text1="Each of smaller (orange) pegs is worth 10 points"
    text2="Each of larger (grey) pegs is worth 20 points"
    text3="Pegs must be struck into the black enclosures to get points"
    text4="The striker must not fall into the enclosure (max 20 point penalty)"
    text5="Queen Peg:50 points. Requires scoring stroke in next turn."
    text6="First to 170 points wins!"
    canvas.create_text(app.width/2,100,text=text1,font="Arial 20 bold")
    canvas.create_text(app.width/2,200,text=text2,font="Arial 20 bold")
    canvas.create_text(app.width/2,300,text=text3,font="Arial 20 bold")
    canvas.create_text(app.width/2,400,text=text4,font="Arial 20 bold")
    canvas.create_text(app.width/2,500,text=text5,font="Arial 20 bold")
    canvas.create_text(app.width/2,600,text=text6,font="Arial 20 bold")

def helpMode_keyPressed(app,canvas):
    app.mode="startMode"

################help mode#################

runApp(width=700,height=700)


