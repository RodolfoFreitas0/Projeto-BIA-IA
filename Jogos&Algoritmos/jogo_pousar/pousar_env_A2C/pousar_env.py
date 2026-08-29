import pygame
import random
import sys
import math

pygame.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
MAX_FRAMES = 1000

class Ship:
    def __init__(self):
        self.width = 60
        self.height = 80
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (150, 130, 220), (10, 10, 40, 40))
        pygame.draw.line(self.image, (150, 130, 220), (10, 50), (0, 70), 5)
        pygame.draw.line(self.image, (150, 130, 220), (50, 50), (60, 70), 5)
        
        self.reset()
        
    def reset(self):
        self.x = (WINDOW_WIDTH // 2) + random.randint(-200, 200)
        self.y = WINDOW_HEIGHT // 4
        self.angle = 0.0
        
        self.x_vel = 0.0
        self.y_vel = 0.0
        self.angular_vel = 0.0
        
        self.gravity = 0.05
        self.thrust_power = 0.15
        self.torque_power = 0.08
        self.max_angular_velocity = 4.0
        self.angular_damping = 0.99
        
        self.fuel = 1000
        self.is_thrusting = False

    def update_logic(self, thrust, left, right):
        self.is_thrusting = False
        self.y_vel += self.gravity

        if self.fuel > 0:
            if left:
                self.angular_vel += self.torque_power
                self.fuel -= 1
            if right:
                self.angular_vel -= self.torque_power
                self.fuel -= 1
            if thrust:
                rad = math.radians(self.angle)
                self.x_vel -= math.sin(rad) * self.thrust_power
                self.y_vel -= math.cos(rad) * self.thrust_power
                self.fuel -= 2
                self.is_thrusting = True

        self.angular_vel *= self.angular_damping
        self.angular_vel = max(-self.max_angular_velocity, min(self.max_angular_velocity, self.angular_vel))
        self.angle = (self.angle + self.angular_vel) % 360.0
        self.x += self.x_vel
        self.y += self.y_vel

class LandingPad:
    def __init__(self):
        self.width = 300
        self.height = 20
        self.reset()
        
    def reset(self):
        pad_x = random.randint(100, WINDOW_WIDTH - self.width - 100)
        self.rect = pygame.Rect(pad_x, WINDOW_HEIGHT - 60, self.width, self.height)
        self.flag_left = pygame.Rect(self.rect.left, self.rect.top - 40, 5, 40)
        self.flag_right = pygame.Rect(self.rect.right - 5, self.rect.top - 40, 5, 40)

class LunarLanderEnv:
    ANGULAR_VEL_SNAP_THRESHOLD = 0.1

    def __init__(self, render=False):
        self.render_mode = render
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        
        if self.render_mode:
            pygame.display.set_caption("Treino IA - Lunar Lander")
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont("Consolas", 24)
            
        self.action_space = 4
        self.observation_space = 10 
        self.reset()

    def reset(self):
        self.ship = Ship()
        self.pad = LandingPad()
        self.frames = 0
        self.done = False
        self.outcome = "running"
        self.landing_timer = 0
        
        self.l_hit = False
        self.r_hit = False
        
        self.prev_shaping = None
        
        return self.get_state()

    def calculate_shaping(self):
        pad_center_x = self.pad.rect.centerx
        pad_center_y = self.pad.rect.top
        
        dx = abs(self.ship.x - pad_center_x) / (self.window_width / 2.0)
        dy = abs(self.ship.y - pad_center_y) / self.window_height
        
        vel = math.hypot(self.ship.x_vel, self.ship.y_vel) / 10.0
        
        angle = ((self.ship.angle + 180.0) % 360.0) - 180.0
        abs_angle = abs(angle)
        angle_score = max(0.0, 1.0 - abs_angle / 45.0)

        altitude_factor = 1.0 - min(dy, 1.0)
        angle_bonus = 30.0 * angle_score * altitude_factor

        alignment_bonus = 60.0 * (1.0 - min(dx, 1.0))

        pad_dx = abs(self.ship.x - pad_center_x) / (self.pad.rect.width / 2.0)
        center_bonus = 25.0 * max(0.0, 1.0 - min(pad_dx, 1.0)) * altitude_factor

        shaping = alignment_bonus + angle_bonus + center_bonus - (35.0 * dy) - (35.0 * vel)
        shaping -= 1.5 * abs(self.ship.angular_vel)
        
        if self.l_hit: shaping += 10.0
        if self.r_hit: shaping += 10.0
        
        return shaping

    def get_state(self):
        state = [
            (self.ship.x - self.pad.rect.centerx) / self.window_width,
            (self.ship.y - self.pad.rect.top) / self.window_height,
            self.ship.x_vel / 10.0,
            self.ship.y_vel / 10.0,
            math.sin(math.radians(self.ship.angle)),
            math.cos(math.radians(self.ship.angle)),
            self.ship.angular_vel / 5.0,
            self.ship.fuel / 1000.0,
            1.0 if self.l_hit else 0.0,
            1.0 if self.r_hit else 0.0
        ]
        return state

    def step(self, action):
        reward = -0.01
        self.frames += 1
        
        thrust = (action == 1)
        left = (action == 2)
        right = (action == 3)

        was_grounded = self.l_hit or self.r_hit
        if was_grounded:
            left = False
            right = False

        leg_offset_l = pygame.math.Vector2(-30, 30)
        leg_offset_r = pygame.math.Vector2(30, 30)

        prev_center = pygame.math.Vector2(self.ship.x, self.ship.y)
        prev_leg_l = prev_center + leg_offset_l.rotate(-self.ship.angle)
        prev_leg_r = prev_center + leg_offset_r.rotate(-self.ship.angle)

        self.ship.update_logic(thrust, left, right)
        
        center = pygame.math.Vector2(self.ship.x, self.ship.y)
        leg_l = center + leg_offset_l.rotate(-self.ship.angle)
        leg_r = center + leg_offset_r.rotate(-self.ship.angle)
        
        pad = self.pad.rect

        def leg_touches_top(leg, prev_leg):
            if not (pad.left <= leg.x <= pad.right):
                return False
            came_from_above = prev_leg.y <= pad.top + 1.0
            return came_from_above and leg.y >= pad.top

        self.l_hit = leg_touches_top(leg_l, prev_leg_l)
        self.r_hit = leg_touches_top(leg_r, prev_leg_r)
        
        body_offsets = [
            pygame.math.Vector2(-20, -30), pygame.math.Vector2(20, -30),
            pygame.math.Vector2(-20, 10), pygame.math.Vector2(20, 10)
        ]
        
        body_hit = False
        for offset in body_offsets:
            p = center + offset.rotate(-self.ship.angle)
            if pad.left <= p.x <= pad.right and p.y >= pad.top:
                body_hit = True
                break

        if self.ship.y + (self.ship.height / 2) >= WINDOW_HEIGHT - 10 or self.ship.x - (self.ship.width / 2) < 0 or self.ship.x + (self.ship.width / 2) > WINDOW_WIDTH or self.ship.y - (self.ship.height / 2) < 0:
            self.done = True
            self.outcome = "crash"
            reward -= 100.0  
        
        elif body_hit:
            self.done = True
            self.outcome = "crash"
            reward -= 100.0  
            
        elif self.frames >= MAX_FRAMES:
            self.done = True
            self.outcome = "timeout"
            reward -= 100.0
            
        elif self.l_hit or self.r_hit:
            if self.ship.y_vel >= 2.5:
                self.done = True
                self.outcome = "crash"
                reward -= 100.0  
            else:
                max_y = max(leg_l.y if self.l_hit else -999, leg_r.y if self.r_hit else -999)
                self.ship.y -= (max_y - pad.top)
                
                self.ship.y_vel *= -0.1
                self.ship.x_vel *= 0.8
                
                if abs(self.ship.y_vel) < 0.1: self.ship.y_vel = 0
                if abs(self.ship.x_vel) < 0.1: self.ship.x_vel = 0
                
                if self.l_hit and not self.r_hit:
                    lever_arm = self.ship.x - leg_l.x
                    self.ship.angular_vel -= lever_arm * 0.002
                    self.ship.angular_vel *= 0.8
                elif self.r_hit and not self.l_hit:
                    lever_arm = self.ship.x - leg_r.x
                    self.ship.angular_vel -= lever_arm * 0.002
                    self.ship.angular_vel *= 0.8
                elif self.l_hit and self.r_hit:
                    self.ship.angular_vel *= 0.5 

                norm_angle = abs(self.ship.angle % 360)
                near_upright = norm_angle < 3 or norm_angle > 357
                if near_upright and abs(self.ship.angular_vel) < self.ANGULAR_VEL_SNAP_THRESHOLD:
                    self.ship.angle = 0
                    self.ship.angular_vel = 0
                    norm_angle = 0

                if self.l_hit and self.r_hit:
                    total_kinetic_energy = abs(self.ship.x_vel) + abs(self.ship.y_vel) + abs(self.ship.angular_vel)
                    is_upright = norm_angle < 15 or norm_angle > 345
                    
                    if is_upright and total_kinetic_energy < 0.5:
                        self.landing_timer += 1
                        if self.landing_timer >= 60:
                            self.done = True
                            self.outcome = "landed"
                            reward += 100.0  
                    else:
                        self.landing_timer = 0
                else:
                    self.landing_timer = 0
        else:
            self.landing_timer = 0

        if not self.done:
            shaping = self.calculate_shaping()
            if self.prev_shaping is not None:
                reward += shaping - self.prev_shaping
            self.prev_shaping = shaping

        if self.render_mode:
            self.render()
            
        return self.get_state(), reward, self.done

    def render(self):
        if not self.render_mode:
            return
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill((0, 0, 0))
        
        pygame.draw.rect(self.screen, (50, 50, 50), (0, WINDOW_HEIGHT - 10, WINDOW_WIDTH, 10))
        
        pygame.draw.rect(self.screen, (220, 220, 220), self.pad.rect)
        pygame.draw.rect(self.screen, "white", self.pad.flag_left)
        pygame.draw.rect(self.screen, "white", self.pad.flag_right)
        pygame.draw.polygon(self.screen, "yellow", [(self.pad.flag_left.right, self.pad.flag_left.top), (self.pad.flag_left.right + 20, self.pad.flag_left.top + 10), (self.pad.flag_left.right, self.pad.flag_left.top + 20)])
        pygame.draw.polygon(self.screen, "yellow", [(self.pad.flag_right.left, self.pad.flag_right.top), (self.pad.flag_right.left - 20, self.pad.flag_right.top + 10), (self.pad.flag_right.left, self.pad.flag_right.top + 20)])

        rotated_image = pygame.transform.rotate(self.ship.image, self.ship.angle)
        rect = rotated_image.get_rect(center=(int(self.ship.x), int(self.ship.y)))
        self.screen.blit(rotated_image, rect.topleft)
        
        if self.ship.is_thrusting:
            rad = math.radians(self.ship.angle)
            flame_x = self.ship.x + math.sin(rad) * 30
            flame_y = self.ship.y + math.cos(rad) * 30
            pygame.draw.circle(self.screen, "orange", (int(flame_x), int(flame_y)), random.randint(5, 10))

        fuel_color = (255, 255, 255) if self.ship.fuel > 0 else (255, 100, 100)
        fuel_txt = self.font.render(f"Fuel: {self.ship.fuel}", True, fuel_color)
        self.screen.blit(fuel_txt, (10, 10))

        vel_color = (100, 255, 100) if self.ship.y_vel < 2.5 else (255, 100, 100)
        vel_txt = self.font.render(f"Y Vel: {self.ship.y_vel:.1f}", True, vel_color)
        self.screen.blit(vel_txt, (10, 40))

        norm_angle = abs(self.ship.angle % 360)
        angle_color = (100, 255, 100) if norm_angle < 15 or norm_angle > 345 else (255, 100, 100)
        angle_txt = self.font.render(f"Angle: {int(norm_angle)}", True, angle_color)
        self.screen.blit(angle_txt, (10, 70))

        pygame.display.flip()
        self.clock.tick(60)