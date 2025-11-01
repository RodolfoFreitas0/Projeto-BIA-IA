
import scripts.core.settings as settings
from scripts.utills.debug import Debug

class EnemyManager:
        def __init__(self):
            self.enemies = []
            
        def add(self, enemy):
            self.enemies.append(enemy)

        def update(self, display, scroll, player):
            for enemy in self.enemies[:]:
                enemy.update(display, scroll)
                enemy.render(display, offset=scroll)
                
                # Remove inimigo caso ele morra
                if not enemy.alive:
                    self.enemies.remove(enemy)
                    continue

                    # Gameover caso o jogador toque no inimigo
                if settings.DEBUG_MODE == False:
                    if enemy.rect().colliderect(player.rect()):
                        print("Colided")
                        player.HP -= 1
                        self.enemies.remove(enemy)
                else:
                    if enemy.rect().colliderect(player.rect()):
                        print("Colided")
                        self.enemies.remove(enemy)

                
            self.enemy_count = len(self.enemies)
            if self.enemy_count > settings.MAX_ENEMIES:
                self.enemies.clear()