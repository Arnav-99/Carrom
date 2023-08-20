
class playingButton():
    def __init__(self,message):
        self.message=message
        self.x=600
        self.y=650
        self.isPressed=False
        self.size=25
    
    def getDimensions(self):
        return (self.x,self.y,self.size)
    
    def isButtonPressed(self):
        if self.isPressed:
            return True
        else:
            return False
    
    def changeState(self):
        self.isPressed=not self.isPressed

class helpButton(playingButton):
    def __init__(self,message):
        super().__init__(message)
        self.size=50
        self.x=350
        self.y=450