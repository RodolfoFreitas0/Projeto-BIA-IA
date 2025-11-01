import pygame
import os

BASE_IMG_PATH =  "00_resources/data/images/"

def load_img(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_imgs(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_img(path + "/" + img_name))
    return images