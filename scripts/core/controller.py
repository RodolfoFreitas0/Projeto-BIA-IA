class InputController:
    def __init__(self):
        self.movement = [False, False]
        self.rotation = [False, False]
        self.shooting = False
    
    def reset(self):
        self.movement = [False, False]
        self.rotation = [False, False]
        self.shooting = False
    
    def rotation_value(self):
        return self.rotation[0] - self.rotation[1]