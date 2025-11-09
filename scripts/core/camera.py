
class Camera:
    def __init__(self, target, display_size):
        self.scroll = [0, 0]
        self.target = target
        self.display_width, self.display_height = display_size

    def update_logic(self):
        
        if self.target.pos[0] >= 50 + self.scroll[0] + self.display_width / 2:
            self.scroll[0] += (self.target.rect().centerx - self.display_width / 2 - self.scroll[0]) / 20
        else:
            self.scroll[0] += 1.5

        self.scroll[1] += (self.target.rect().centery - self.display_height / 2 - self.scroll[1]) / 15
    
    def instant_focus(self):
        self.scroll[0] = self.target.rect().centerx - self.display_width / 2
        self.scroll[1] = self.target.rect().centery - self.display_height / 2
    
    def get_offset(self):
        return (int(self.scroll[0]), int(self.scroll[1]))
