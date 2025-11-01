
import random
from .cloud import Cloud
import scripts.core.settings as settings
from scripts.utills.debug import Debug

class Clouds:
    def __init__(self, cloud_images, count=16):
        self.clouds = []
        for i in range(count):
            self.clouds.append(Cloud((random.random() * 99999,
                                    random.random() * 99999),       # posição inicial aleatória
                                    random.choice(cloud_images),    # imagem aleatória
                                    random.random() * 0.05 + 0.05,  # velocidade aleatória
                                    random.random() * 0.6 + 0.2     # profundidade aleatória
                                    ))
        self.clouds.sort(key=lambda x: x.depth) 
    
    def update(self):
        for cloud in self.clouds:
            cloud.update()
    
    def render(self, surf, offset=(0, 0)):
        for i, cloud in enumerate(self.clouds):
            cloud.render(surf, offset=offset)