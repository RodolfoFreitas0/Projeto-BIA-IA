import pygame
import sys

import scripts.core.settings as settings

def handle_events(game, controller):
    for event in pygame.event.get():
            # Fechar o jogo
            if event.type == pygame.QUIT:
                game.running = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.running = False
                pygame.quit()
                sys.exit()
                    
            if game.game_active == True:
                if event.type == pygame.KEYDOWN:
                    
                    if event.key == pygame.K_SPACE:
                        controller.shooting = True

                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        controller.rotation[0] = True
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        controller.rotation[1] = True

                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        controller.movement[1] = True
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        controller.movement[0] = True

                    if event.key == pygame.K_i:
                        from scripts.entities.enemy import Enemy

                        enemy = Enemy(game, game.render_scroll, (3, 3))
                        game.enemy_manager.add(enemy)

                        print(len(game.enemy_manager.enemies))

                    if event.key == pygame.K_b:
                        if settings.DEBUG_MODE:
                            settings.DEBUG_MODE = False
                            print("Debug Mode: OFF")
                        else:
                            settings.DEBUG_MODE = True
                            print("Debug Mode: ON")

                elif event.type == pygame.KEYUP:

                    if event.key == pygame.K_SPACE:
                        controller.shooting = False

                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        controller.rotation[0] = False
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        controller.rotation[1] = False

                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        controller.movement[1] = False
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        controller.movement[0] = False
                        
                elif event.type == settings.SPAWN_EVENT:
                    from scripts.entities.missile import Missile

                    missile = Missile(game, game.render_scroll, (3, 3))
                    game.missile_manager.add(missile)
                    
                    settings.SPAWN_TIME = max(500, settings.SPAWN_TIME - 50)
                    pygame.time.set_timer(settings.SPAWN_EVENT, settings.SPAWN_TIME)
                        
                elif event.type == settings.SCORE_EVENT:
                    game.score += 1
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game.game_active = True
                    game.reset()