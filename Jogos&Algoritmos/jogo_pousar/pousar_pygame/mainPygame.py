import pygame
import sys
import math
import random

pygame.init()

from settings import *
from start_screen import StartScreen

pygame.display.set_caption("Treino IA - Lunar Lander (Física Real)")

class Ship:
    def __init__(self):
        self.width = 60
        self.height = 80
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (150, 130, 220), (10, 10, 40, 40))
        pygame.draw.line(self.image, (150, 130, 220), (10, 50), (0, 70), 5)
        pygame.draw.line(self.image, (150, 130, 220), (50, 50), (60, 70), 5)
        
        self.x = (WINDOW_WIDTH // 2) + random.randint(-150, 150)
        self.y = WINDOW_HEIGHT // 4
        self.angle = 0.0
        
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        self.x_vel = 0.0
        self.y_vel = 0.0
        self.angular_vel = 0.0
        
        self.gravity = 0.05
        self.thrust_power = 0.15
        self.torque_power = 0.15
        
        self.fuel = 1000
        self.is_thrusting = False

    def update_logic(self, keys):
        self.is_thrusting = False
        self.y_vel += self.gravity

        if self.fuel > 0:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.angular_vel += self.torque_power
                self.fuel -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.angular_vel -= self.torque_power
                self.fuel -= 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                rad = math.radians(self.angle)
                self.x_vel -= math.sin(rad) * self.thrust_power
                self.y_vel -= math.cos(rad) * self.thrust_power
                self.fuel -= 2
                self.is_thrusting = True

        self.angle += self.angular_vel
        self.x += self.x_vel
        self.y += self.y_vel

    def render(self):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
        
        SCREEN.blit(rotated_image, self.rect.topleft)
        
        if self.is_thrusting:
            rad = math.radians(self.angle)
            flame_x = self.x + math.sin(rad) * 30
            flame_y = self.y + math.cos(rad) * 30
            pygame.draw.circle(SCREEN, "orange", (int(flame_x), int(flame_y)), random.randint(5, 10))

class LandingPad:
    def __init__(self):
        self.width = 300
        self.height = 20
        pad_x = random.randint(50, WINDOW_WIDTH - self.width - 50)
        
        self.rect = pygame.Rect(pad_x, WINDOW_HEIGHT - 60, self.width, self.height)
        self.flag_left = pygame.Rect(self.rect.left, self.rect.top - 40, 5, 40)
        self.flag_right = pygame.Rect(self.rect.right - 5, self.rect.top - 40, 5, 40)

    def render(self):
        pygame.draw.rect(SCREEN, (220, 220, 220), self.rect)
        pygame.draw.rect(SCREEN, "white", self.flag_left)
        pygame.draw.rect(SCREEN, "white", self.flag_right)
        pygame.draw.polygon(SCREEN, "yellow", [(self.flag_left.right, self.flag_left.top), (self.flag_left.right + 20, self.flag_left.top + 10), (self.flag_left.right, self.flag_left.top + 20)])
        pygame.draw.polygon(SCREEN, "yellow", [(self.flag_right.left, self.flag_right.top), (self.flag_right.left - 20, self.flag_right.top + 10), (self.flag_right.left, self.flag_right.top + 20)])

class HUD:
    def __init__(self):
        self.font_small = pygame.font.SysFont("Monocraft", 24) 
        self.font_big = pygame.font.SysFont("Monocraft", 60)

    def draw_stats(self, surf, fuel, y_vel, angle, timer):
        fuel_color = "white" if fuel > 0 else "red"
        fuel_text = self.font_small.render(f"Combustivel: {fuel}", False, fuel_color)
        
        speed_color = "green" if y_vel < 2.5 else "red"
        speed_text = self.font_small.render(f"Velocidade Queda: {y_vel:.1f}", False, speed_color)

        angle_color = "green" if abs(angle % 360) < 15 or abs(angle % 360) > 345 else "red"
        angle_text = self.font_small.render(f"Angulo: {int(angle % 360)}", False, angle_color)

        surf.blit(fuel_text, (30, 30))
        surf.blit(speed_text, (30, 70))
        surf.blit(angle_text, (30, 110))
        
        if timer > 0:
            time_left = max(0, 60 - timer)
            timer_text = self.font_big.render(f"{time_left//60 + 1}", False, "yellow")
            surf.blit(timer_text, timer_text.get_rect(center=(WINDOW_WIDTH//2, 100)))
    
    def draw_winner_screen(self, result):
        SCREEN.fill((0, 0, 0))
        color = "green" if result == "POUSO PERFEITO!" else "red"
        text = self.font_big.render(result, True, color)
        SCREEN.blit(text, text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50)))

        info = self.font_small.render("Aperte ESPACO para reiniciar ou ESC para o menu", True, "white")
        SCREEN.blit(info, info.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50)))
        
class Game:
    def __init__(self):
        self.ship = Ship()
        self.pad = LandingPad()
        self.HUD = HUD()

        self.result_message = ""
        self.game_over = False
        self.landing_timer = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.ship.update_logic(keys)
    
    def check_collisions(self):
        if self.ship.rect.bottom >= WINDOW_HEIGHT or self.ship.rect.left < 0 or self.ship.rect.right > WINDOW_WIDTH:
            self.result_message = "NAVE DESTRUIDA! (Fora da Área)"
            self.game_over = True
            return

        center = pygame.math.Vector2(self.ship.x, self.ship.y)
        
        leg_offset_l = pygame.math.Vector2(-30, 30) 
        leg_offset_r = pygame.math.Vector2(30, 30)
        
        leg_l = center + leg_offset_l.rotate(-self.ship.angle)
        leg_r = center + leg_offset_r.rotate(-self.ship.angle)
        
        pad = self.pad.rect
        
        l_hit = pad.left <= leg_l.x <= pad.right and leg_l.y >= pad.top
        r_hit = pad.left <= leg_r.x <= pad.right and leg_r.y >= pad.top
        
        body_offsets = [
            pygame.math.Vector2(-20, -30),
            pygame.math.Vector2(20, -30),
            pygame.math.Vector2(-20, 10),
            pygame.math.Vector2(20, 10)
        ]
        
        body_hit = False
        for offset in body_offsets:
            p = center + offset.rotate(-self.ship.angle)
            if pad.left <= p.x <= pad.right and p.y >= pad.top:
                body_hit = True
                break

        if body_hit:
            self.result_message = "NAVE DESTRUIDA! (Tombou)"
            self.game_over = True
            return

        if l_hit or r_hit:
            if self.ship.y_vel >= 2.5:
                self.result_message = "POUSO MUITO BRUSCO!"
                self.game_over = True
                return
            
            max_y = max(leg_l.y if l_hit else -999, leg_r.y if r_hit else -999)
            self.ship.y -= (max_y - pad.top)
            
            self.ship.y_vel *= -0.1
            self.ship.x_vel *= 0.8
            
            if abs(self.ship.y_vel) < 0.1: 
                self.ship.y_vel = 0
            if abs(self.ship.x_vel) < 0.1: 
                self.ship.x_vel = 0
            
            if l_hit and not r_hit:
                lever_arm = self.ship.x - leg_l.x
                self.ship.angular_vel -= lever_arm * 0.01
                self.ship.angular_vel *= 0.9
            elif r_hit and not l_hit:
                lever_arm = self.ship.x - leg_r.x
                self.ship.angular_vel -= lever_arm * 0.01
                self.ship.angular_vel *= 0.9
            elif l_hit and r_hit:
                self.ship.angular_vel *= 0.5 
                
                norm_angle = abs(self.ship.angle % 360)
                if (norm_angle < 3 or norm_angle > 357) and abs(self.ship.angular_vel) < 0.1:
                    self.ship.angle = 0
                    self.ship.angular_vel = 0
                    norm_angle = 0 
                
                total_kinetic_energy = abs(self.ship.x_vel) + abs(self.ship.y_vel) + abs(self.ship.angular_vel)
                is_upright = norm_angle < 15 or norm_angle > 345
                
                if is_upright and total_kinetic_energy < 0.5:
                    self.landing_timer += 1
                    if self.landing_timer >= 60:
                        self.result_message = "POUSO PERFEITO!"
                        self.game_over = True
                else:
                    self.landing_timer = 0
        else:
            self.landing_timer = 0

    def update(self):
        self.check_collisions()

    def render(self):
        SCREEN.fill((0, 0, 0))
        screen_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(SCREEN, (255, 255, 255), screen_rect, 4)

        self.pad.render()
        self.ship.render()
        self.HUD.draw_stats(SCREEN, self.ship.fuel, self.ship.y_vel, self.ship.angle, self.landing_timer)

        pygame.display.update()
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    return

                if self.game_over and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return "RESTART"
                    elif event.key == pygame.K_ESCAPE:
                        return "MENU"
                    
            if not self.game_over:
                self.handle_input()
                self.update()
                self.render()
            else:
                self.HUD.draw_winner_screen(result=self.result_message)
                pygame.display.update()
                
            CLOCK.tick(60)

if __name__ == "__main__":
    while True:
        start = StartScreen(SCREEN, CLOCK, TITLE)
        result = start.run()

        if result == "PLAY":
            playing = True
            while playing:
                game = Game()
                game_result = game.run()
                
                if game_result == "MENU":
                    playing = False
        else:
            break
        
    pygame.quit()
    sys.exit()