"""Affichage TP4: GameRenderer etendu (animations, effets, HUD). Seule classe qui dessine le jeu."""
import math
import random

import pygame

from game_oop import AssetManager, GameRenderer, Player
from homework_monsters import HealthBarRenderer
from tp4.background import ParallaxBackground
from tp4.enemies import (FrostBoss, GolemBoss, IceMonster, PoisonMonster, TankMonster,
                         TeleportMonster, ToxicBoss)
from tp4.powerups import POWERUPS
from tp4.settings import HEIGHT, WIDTH


class AssetManagerTP4(AssetManager):
    """Ajoute les images des nouveaux monstres (optionnelles, assets/<fichier>)."""

    EXTRA = {IceMonster: "monster_ice.png", PoisonMonster: "monster_poison.png",
             TeleportMonster: "monster_teleport.png", TankMonster: "monster_tank.png",
             GolemBoss: "boss_golem.png", FrostBoss: "boss_frost.png", ToxicBoss: "boss_toxic.png"}

    def __init__(self):
        super().__init__()
        for cls, filename in self.EXTRA.items():
            self.monsters[cls] = self._load(filename, (cls.SIZE + 10, cls.SIZE + 10))


class GameRendererTP4(GameRenderer):
    def __init__(self, assets):
        super().__init__(assets)
        self.font_tiny = pygame.font.SysFont("arial", 14)
        self.font_mid = pygame.font.SysFont("arial", 22)
        self.world = pygame.Surface((WIDTH, HEIGHT))
        self.background = ParallaxBackground(WIDTH, HEIGHT, assets.background)
        self.t = 0
        self.fps = 60
        self.show_fps = True
        self._bars = {}

    # ------------------------------------------------------------------
    def draw(self, surface, board, animate=True):
        if animate:
            self.t += 1
        w = self.world
        self.background.draw(w, self.t)
        self._pickups(w, board)
        self._enemies(w, board)
        self._projectiles(w, board)
        self._player(w, board)
        self._arcs(w, board)
        board.particles.draw(w)
        ox = oy = 0
        if board.shake > 0:
            amp = min(6, board.shake // 2 + 1)
            ox, oy = random.randint(-amp, amp), random.randint(-amp, amp)
        surface.fill((0, 0, 0))
        surface.blit(w, (ox, oy))
        self._hud(surface, board)
        if board.state == "LEVEL_CLEAR":
            self._text(surface, f"LEVEL {board.level} CLEARED!", (WIDTH // 2, HEIGHT // 2 - 40),
                       self.font_large, (255, 230, 90))
            self._text(surface, "Press B to open the SHOP", (WIDTH // 2, HEIGHT // 2 + 10),
                       self.font_small, (255, 255, 255))
        elif board.state == "PLAYING" and board.frame < 100:
            label = f"BOSS LEVEL {board.level}" if board.config.boss else f"LEVEL {board.level}"
            self._text(surface, label, (WIDTH // 2, 120), self.font_large,
                       (255, 90, 90) if board.config.boss else (255, 255, 255))

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------
    def _text(self, surface, text, pos, font, color, align="center"):
        img = font.render(text, True, color)
        rect = img.get_rect()
        if align == "center":
            rect.center = pos
        elif align == "right":
            rect.topright = pos
        else:
            rect.topleft = pos
        surface.blit(img, rect)

    def _bar(self, monster):
        size = monster.SIZE
        if size not in self._bars:
            self._bars[size] = HealthBarRenderer(width=size)
        return self._bars[size]

    # ------------------------------------------------------------------
    # Creatures animees (joueur et monstres)
    # ------------------------------------------------------------------
    def _creature(self, surf, sprite, rect, color, phase, moving, face_right, flash,
                  target_x, bob_amp=3.0, key=""):
        t = self.t
        s = math.sin(t * (0.28 if moving else 0.09) + phase)
        bob = s * (bob_amp if moving else bob_amp * 0.5)
        squash = 1 + 0.06 * s
        cx, cy = rect.center
        pygame.draw.ellipse(surf, (8, 8, 14), (rect.x + 4, rect.bottom - 5, rect.w - 8, 9))
        if sprite:
            img = sprite if face_right else pygame.transform.flip(sprite, True, False)
            img = pygame.transform.rotozoom(img, s * 4 if moving else 0, squash)
            if flash > 0:
                img = img.copy()
                img.fill((120, 120, 120, 0), special_flags=pygame.BLEND_RGB_ADD)
            surf.blit(img, img.get_rect(center=(cx, cy + bob)))
        else:
            w, h = int(rect.w * (2 - squash)), int(rect.h * squash)
            body = pygame.Rect(0, 0, w, h)
            body.center = (cx, int(cy + bob))
            leg = int(math.sin(t * 0.3 + phase) * 4) if moving else 0
            dark = tuple(int(c * 0.55) for c in color)
            pygame.draw.rect(surf, dark, (body.x + 6, body.bottom - 3, 9, 6 + leg))
            pygame.draw.rect(surf, dark, (body.right - 15, body.bottom - 3, 9, 6 - leg))
            pygame.draw.rect(surf, (255, 255, 255) if flash > 0 else color, body, border_radius=10)
            look = 2 if target_x > cx else -2
            eye_y = body.y + int(h * 0.32)
            for ex in (body.centerx - int(w * 0.2), body.centerx + int(w * 0.2)):
                pygame.draw.circle(surf, (255, 255, 255), (ex, eye_y), max(3, w // 9))
                pygame.draw.circle(surf, (20, 20, 30), (ex + look, eye_y), max(2, w // 17))
        self._decoration(surf, key, rect, bob)

    def _decoration(self, surf, key, rect, bob):
        t, cx, top = self.t, rect.centerx, rect.top + bob
        if key == "flying":
            flap = math.sin(t * 0.4) * 12
            for side in (-1, 1):
                x0 = cx + side * rect.w // 2
                pygame.draw.polygon(surf, (210, 190, 255),
                                    [(x0, rect.centery), (x0 + side * 20, rect.centery - 8 - flap),
                                     (x0 + side * 8, rect.centery + 10)])
        elif key in ("ice", "boss_frost"):
            for dx in (-12, 0, 12):
                pygame.draw.polygon(surf, (210, 245, 255),
                                    [(cx + dx - 5, top + 2), (cx + dx, top - 12), (cx + dx + 5, top + 2)])
        elif key in ("poison", "boss_toxic"):
            for i in range(3):
                bx = cx - 12 + i * 12
                by = rect.centery - ((t * 0.6 + i * 17) % 40)
                pygame.draw.circle(surf, (150, 255, 90), (int(bx), int(by)), 3 + i % 2, 1)
        elif key == "teleport":
            r = 4 + int(abs(math.sin(t * 0.1)) * 8)
            pygame.draw.circle(surf, (255, 150, 255), rect.center, rect.w // 2 + r, 2)
        elif key in ("strong", "tank", "boss_golem"):
            pygame.draw.rect(surf, (200, 200, 210), rect.inflate(-6, -6), 3, border_radius=8)
        if key.startswith("boss"):
            for dx in (-18, 0, 18):
                pygame.draw.polygon(surf, (255, 215, 0),
                                    [(cx + dx - 7, top), (cx + dx, top - 18), (cx + dx + 7, top)])

    def _player(self, surf, board):
        p = board.player
        if p.iframes > 0 and (self.t // 3) % 2 == 0:
            blink = True
        else:
            blink = False
        if not blink:
            self._creature(surf, self.assets.player, p.rect, (50, 205, 50), 0.0, p.moving,
                           p.facing_right, 0, p.x + 999 if p.facing_right else p.x - 999, 2.5)
        if p.shielded:
            r = Player.SIZE // 2 + 12 + int(math.sin(self.t * 0.2) * 2)
            pygame.draw.circle(surf, (90, 170, 255), p.rect.center, r, 3)
        self.player_bar.draw(surf, p)

    def _enemies(self, surf, board):
        px = board.player.center[0]
        for e in board.enemies:
            m = e.monster
            rect = pygame.Rect(int(m.x), int(m.y), m.SIZE, m.SIZE)
            if e.slow_timer > 0:
                pygame.draw.circle(surf, (150, 220, 255), rect.center, m.SIZE // 2 + 6, 2)
            amp = 7.0 if e.key == "flying" else 3.0
            self._creature(surf, self.assets.monsters.get(type(m)), rect, e.color, e.phase, True,
                           e.facing_right, e.flash, px, amp, e.key)
            self._bar(m).draw(surf, m)
            if not e.is_boss:
                label = self.font_tiny.render(m.name, True, (255, 255, 255))
                lx = max(2, min(rect.x, WIDTH - label.get_width() - 2))
                surf.blit(label, (lx, rect.y - 26))

    # ------------------------------------------------------------------
    # Projectiles et effets
    # ------------------------------------------------------------------
    def _projectiles(self, surf, board):
        t = self.t
        for b in board.bullets:
            c, spec = b.spec.color, b.spec
            pos = (int(b.x), int(b.y))
            glow = tuple(int(v * 0.35) for v in c)
            if spec.shape == "line":
                tail = (int(b.x - b.vx * 1.3), int(b.y - b.vy * 1.3))
                pygame.draw.line(surf, glow, tail, pos, 7)
                pygame.draw.line(surf, c, tail, pos, 3)
                pygame.draw.line(surf, (255, 255, 255), tail, pos, 1)
            elif spec.shape == "rocket":
                ang = math.atan2(b.vy, b.vx)
                tail = (int(b.x - math.cos(ang) * 14), int(b.y - math.sin(ang) * 14))
                pygame.draw.line(surf, (255, 170, 40), tail, pos, 6)
                pygame.draw.circle(surf, (230, 230, 230), pos, b.radius)
                pygame.draw.circle(surf, c, pos, b.radius - 3)
            elif spec.shape == "bolt":
                ang = math.atan2(b.vy, b.vx)
                pts = [(b.x - math.cos(ang) * 22, b.y - math.sin(ang) * 22)]
                for i in range(1, 5):
                    j = random.uniform(-6, 6)
                    pts.append((b.x - math.cos(ang) * (22 - i * 5.5) - math.sin(ang) * j,
                                b.y - math.sin(ang) * (22 - i * 5.5) + math.cos(ang) * j))
                pygame.draw.lines(surf, c, False, pts, 3)
                pygame.draw.circle(surf, (255, 255, 255), pos, 3)
            elif spec.shape == "plasma":
                r = b.radius + int(math.sin(t * 0.4) * 2)
                pygame.draw.circle(surf, glow, pos, r + 5)
                pygame.draw.circle(surf, c, pos, r)
                pygame.draw.circle(surf, (255, 255, 255), pos, max(2, r // 3))
            else:
                pygame.draw.circle(surf, glow, pos, b.radius + 4)
                pygame.draw.circle(surf, c, pos, b.radius)
                pygame.draw.circle(surf, (255, 255, 255), pos, max(1, b.radius // 3))

    def _arcs(self, surf, board):
        for x1, y1, x2, y2, life in board.arcs:
            pts = [(x1, y1)]
            for i in range(1, 5):
                k = i / 5
                pts.append((x1 + (x2 - x1) * k + random.uniform(-9, 9),
                            y1 + (y2 - y1) * k + random.uniform(-9, 9)))
            pts.append((x2, y2))
            pygame.draw.lines(surf, (190, 210, 255), False, pts, 4)
            pygame.draw.lines(surf, (255, 255, 255), False, pts, 1)

    def _pickups(self, surf, board):
        for pk in board.pickups:
            if pk.ttl < 180 and (pk.ttl // 6) % 2 == 0:
                continue                       # clignote avant de disparaitre
            y = int(pk.y + math.sin((self.t + pk.age) * 0.1) * 3)
            pos = (int(pk.x), y)
            if pk.kind == "coin":
                pygame.draw.circle(surf, (255, 200, 30), pos, 8)
                pygame.draw.circle(surf, (255, 240, 130), pos, 5, 2)
            else:
                pu = POWERUPS[pk.kind]
                pygame.draw.circle(surf, tuple(int(c * 0.4) for c in pu.color), pos, 15)
                pygame.draw.circle(surf, pu.color, pos, 11)
                img = self.font_tiny.render(pu.icon, True, (20, 20, 30))
                surf.blit(img, img.get_rect(center=pos))

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------
    def _hud(self, surf, board):
        p, st = board.player, board.stats
        # HP
        pygame.draw.rect(surf, (60, 20, 30), (12, 10, 210, 18), border_radius=4)
        pygame.draw.rect(surf, (230, 60, 80), (12, 10, int(210 * p.health.ratio), 18), border_radius=4)
        self._text(surf, f"HP {p.health.hp}/{p.health.max_hp}", (117, 19), self.font_tiny, (255, 255, 255))
        # XP
        ratio = min(1.0, st.xp / st.xp_to_next)
        pygame.draw.rect(surf, (20, 30, 60), (12, 32, 210, 14), border_radius=4)
        pygame.draw.rect(surf, (70, 140, 255), (12, 32, int(210 * ratio), 14), border_radius=4)
        self._text(surf, f"Lv.{st.level}  XP {st.xp}/{st.xp_to_next}", (117, 39), self.font_tiny, (255, 255, 255))
        # Coins et arme
        self._text(surf, f"Coins: {board.data.coins}", (12, 54), self.font_small, (255, 210, 60), "left")
        weapon = board.current_weapon
        owned = [w.name for w in board.owned_weapons()]
        self._text(surf, f"Weapon: {weapon.name} [{owned.index(weapon.name) + 1}/{len(owned)}]",
                   (12, 78), self.font_small, weapon.color, "left")
        # Infos a droite
        right = WIDTH - 12
        self._text(surf, f"Level {board.level}", (right, 10), self.font_mid, (255, 255, 255), "right")
        self._text(surf, f"Enemies left: {board.remaining}", (right, 38), self.font_small, (255, 255, 255), "right")
        self._text(surf, f"Score: {board.score}", (right, 60), self.font_small, (255, 255, 255), "right")
        if self.show_fps:
            self._text(surf, f"FPS: {int(self.fps)}", (right, 82), self.font_tiny, (160, 255, 160), "right")
        # Power-ups actifs
        x = 12
        for name, frames in p.effects.items():
            pu = POWERUPS[name]
            pygame.draw.circle(surf, pu.color, (x + 12, HEIGHT - 40), 13)
            self._text(surf, pu.icon, (x + 12, HEIGHT - 40), self.font_tiny, (20, 20, 30))
            self._text(surf, f"{frames // 60 + 1}s", (x + 12, HEIGHT - 18), self.font_tiny, (255, 255, 255))
            x += 36
        self._text(surf, "WASD/Arrows move | SPACE fire | 1-7 or Q/E weapon | P pause",
                   (WIDTH - 12, HEIGHT - 20), self.font_tiny, (170, 170, 190), "right")
        # Barre du boss
        boss = board.boss
        if boss:
            bw = 320
            x0 = WIDTH // 2 - bw // 2
            pygame.draw.rect(surf, (50, 20, 20), (x0, 8, bw, 14), border_radius=4)
            pygame.draw.rect(surf, (230, 40, 40), (x0, 8, int(bw * boss.hp_ratio), 14), border_radius=4)
            self._text(surf, boss.monster.name, (WIDTH // 2, 36), self.font_small, (255, 200, 200))
