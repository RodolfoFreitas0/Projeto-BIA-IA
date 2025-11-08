
from mainCore import CoreGame
from mainPygame import PygameGame
import scripts.core.settings as settings

def main():
    if settings.PYGAME_MODE == True:
        game = PygameGame()
    else:
        game = CoreGame()
    game.run()


# Chamando a def que inicia o jogo
if __name__ == "__main__":
    main()
