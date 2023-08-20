import cmu_112_graphics
class Button():
    def __init__(self,message):
        self.message=message
        self.x=600
        self.y=650
        self.isPressed=False
        self.size=25