"""Application: boucle principale + pile d'ecrans (State pattern)."""
import pygame

from tp4.audio import SoundManager
from tp4.background import ParallaxBackground
from tp4.board import GameBoardTP4
from tp4.progression import PlayerStats
from tp4.render import AssetManagerTP4, GameRendererTP4
from tp4.save import SaveManager
from tp4.screens import GameScreen, MainMenuScreen
from tp4.settings import FPS, HEIGHT, WIDTH


class App:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("2D Shooting Game - TP4")
        self.clock = pygame.time.Clock()
        self.saves = SaveManager()
        self.data = self.saves.load()
        self.audio = SoundManager(self.data.master_volume, self.data.music_volume, self.data.sfx_volume)
        self.assets = AssetManagerTP4()
        self.renderer = GameRendererTP4(self.assets)
        self.menu_background = ParallaxBackground(WIDTH, HEIGHT)
        self.fonts = {
            "tiny": pygame.font.SysFont("arial", 16),
            "small": pygame.font.SysFont("arial", 22),
            "medium": pygame.font.SysFont("arial", 32),
            "large": pygame.font.SysFont("arial", 52),
        }
        self.ticks = 0
        self.running = True
        self.stack = [MainMenuScreen(self)]
        self.audio.start_music()

    # ---- pile d'ecrans ----
    @property
    def top(self):
        return self.stack[-1]

    def push(self, screen):
        self.stack.append(screen)

    def pop(self):
        if len(self.stack) > 1:
            self.stack.pop().on_exit()

    def reset_stack(self, screen):
        while self.stack:
            self.stack.pop().on_exit()
        self.stack.append(screen)

    # ---- actions ----
    def start_new_game(self):
        stats = PlayerStats(self.data)
        stats.reset_run()
        self.reset_stack(GameScreen(self, GameBoardTP4(self.data, stats, self.audio)))

    def continue_game(self):
        if self.data.has_run:
            stats = PlayerStats(self.data)
            self.reset_stack(GameScreen(self, GameBoardTP4(self.data, stats, self.audio, resume=True)))

    def to_main_menu(self):
        self.reset_stack(MainMenuScreen(self))

    def apply_options(self):
        d = self.data
        self.audio.set_volumes(d.master_volume, d.music_volume, d.sfx_volume)

    def save(self):
        self.saves.save(self.data)

    def quit(self):
        self.running = False

    # ---- boucle ----
    def _draw(self):
        i = len(self.stack) - 1
        while i > 0 and self.stack[i].transparent:
            i -= 1
        for screen in self.stack[i:]:
            screen.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.top.handle_event(event)
            self.top.update()
            self.ticks += 1
            self._draw()
            self.clock.tick(FPS)
        self.save()
        pygame.quit()
