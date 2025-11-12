
class Rectangle:
    def __init__(self, owner, offset_x, offset_y, width, height):
        self.owner = owner

        self.offset_x = offset_x
        self.offset_y = offset_y

        self.x = owner.pos[0] + offset_x
        self.y = owner.pos[1] + offset_y

        self.width = width
        self.height = height

    @property
    def center(self):
        return (self.x + self.width / 2, self.y + self.height / 2)

    @property
    def centerx(self):
        cx = self.x + self.width / 2
        return cx
    
    @property
    def centery(self):
        cy = self.y + self.height / 2
        return cy

    def update(self):
        self.x = self.owner.pos[0] + self.offset_x
        self.y = self.owner.pos[1] + self.offset_y

    def colliderect(self, other):
        return not (
            self.x + self.width < other.x or
            self.x > other.x + other.width or
            self.y + self.height < other.y or
            self.y > other.y + other.height 
        )
    
    def move(self, dx, dy):
        return (self.x + dx, self.y + dy, self.width, self.height)