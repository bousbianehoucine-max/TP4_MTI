"""GameBoardTP4: les regles du jeu etendues (niveaux, XP, drops, armes...). Aucun dessin."""
import math
import random

import pygame

from game_oop import GameBoard
from tp4.effects import ParticleSystem
from tp4.enemies import AIContext, EnemyFactory
from tp4.entities import Pickup, PlayerTP4, Projectile
from tp4.powerups import POWERUPS, random_powerup_kind
from tp4.progression import LevelManager
from tp4.settings import HEIGHT, WIDTH
from tp4.weapons import ENEMY_SHOTS, WEAPONS, get_weapon


def _rect_of(enemy):
    s = enemy.monster.SIZE
    return pygame.Rect(int(enemy.x), int(enemy.y), s, s)


class GameBoardTP4(GameBoard):
    LEVEL_CLEAR_FRAMES = 150
    POWERUP_CHANCE = 0.18

    def __init__(self, data, stats, audio, resume=False):
        self.data, self.stats, self.audio, self.resume = data, stats, audio, resume
        self.levels = LevelManager()
        self.factory = EnemyFactory()
        self.particles = ParticleSystem()
        self.pending_upgrades = 0
        self.needs_save = False
        super().__init__()                 # appelle reset()

    # ------------------------------------------------------------------
    # Debut de partie / de niveau
    # ------------------------------------------------------------------
    def reset(self):
        self.player = PlayerTP4(self.stats)
        self.bullets, self.enemies, self.pickups, self.arcs = [], [], [], []
        self.score = self.data.score if self.resume else 0
        self.level = self.data.game_level if self.resume else 1
        self.resume = False
        self.state = "PLAYING"            # PLAYING / LEVEL_CLEAR / GAME_OVER
        self.frame = self.shake = self.banner = 0
        self.weapon_name = "Bullet"
        self._begin_level()

    def _begin_level(self):
        self.config = self.levels.config(self.level)
        self.spawn_queue = self.levels.build_queue(self.config)
        self.spawn_timer = 0
        self.state = "PLAYING"
        if self.config.boss:
            self.audio.play("boss")

    def _next_level(self):
        self.level += 1
        self.player.heal(int(self.player.health.max_hp * 0.25))
        self._begin_level()

    @property
    def remaining(self):
        return len(self.spawn_queue) + sum(1 for e in self.enemies if e.alive)

    @property
    def boss(self):
        return next((e for e in self.enemies if e.is_boss and e.alive), None)

    # ------------------------------------------------------------------
    # Armes
    # ------------------------------------------------------------------
    def owned_weapons(self):
        return [w for w in WEAPONS if w.name in self.data.unlocks]

    @property
    def current_weapon(self):
        spec = get_weapon(self.weapon_name)
        return spec if spec.name in self.data.unlocks else self.owned_weapons()[0]

    def select_weapon(self, index):
        owned = self.owned_weapons()
        if 0 <= index < len(owned):
            self.weapon_name = owned[index].name

    def cycle_weapon(self, step):
        owned = self.owned_weapons()
        idx = [w.name for w in owned].index(self.current_weapon.name)
        self.weapon_name = owned[(idx + step) % len(owned)].name

    def nearest_enemy(self, x, y, exclude=(), max_dist=1e9):
        best, best_d = None, max_dist
        for e in self.enemies:
            if e.alive and id(e) not in exclude:
                d = math.hypot(e.cx - x, e.cy - y)
                if d <= best_d:
                    best, best_d = e, d
        return best

    def fire(self, weapon=None):
        if self.state != "PLAYING" or self.player.cooldown > 0:
            return False
        p = self.player
        spec = weapon or self.current_weapon
        px, py = p.center
        target = self.nearest_enemy(px, py)
        if target:
            dx, dy = target.cx - px, target.cy - py
        else:
            dx, dy = (1 if p.facing_right else -1), 0
        angle = math.atan2(dy, dx)
        rate = self.stats.fire_rate_mult * (2 if "rapid_fire" in p.effects else 1)
        p.cooldown = max(2, int(spec.cooldown / rate))
        cos, sin = math.cos(angle), math.sin(angle)
        self.bullets.append(Projectile(px + cos * 22, py + sin * 22, cos * spec.speed, sin * spec.speed,
                                       spec.make_shot_weapon(p.damage_mult), spec))
        self.particles.emit_muzzle(px + cos * 22, py + sin * 22, angle, spec.color)
        self.audio.play(spec.sound)
        return True

    # ------------------------------------------------------------------
    # Services utilises par les effets d'armes
    # ------------------------------------------------------------------
    def damage_enemy(self, enemy, weapon):
        dealt = enemy.monster.take_hit(weapon)
        enemy.flash = 6
        self.score += max(1, dealt // 5)
        self.particles.emit_sparks(enemy.cx, enemy.cy, enemy.color)
        self.audio.play("hit")
        return dealt

    def explode(self, x, y, radius, color):
        self.particles.emit_explosion(x, y, color, count=int(radius / 3), speed=5)
        self.particles.add_ring(x, y, radius, color)
        self.shake = max(self.shake, 8)
        self.audio.play("explosion")

    def add_arc(self, x1, y1, x2, y2):
        self.arcs.append([x1, y1, x2, y2, 8])

    # ------------------------------------------------------------------
    # Mise a jour d'une image
    # ------------------------------------------------------------------
    def update(self):
        self.particles.update()
        self.shake = max(0, self.shake - 1)
        self.arcs = [[a[0], a[1], a[2], a[3], a[4] - 1] for a in self.arcs if a[4] > 1]
        if self.state == "GAME_OVER":
            return
        p = self.player
        p.tick()
        self._update_poison()
        self._update_pickups()
        if self.state == "LEVEL_CLEAR":
            self.banner -= 1
            if self.banner <= 0:
                self._next_level()
            return

        self.frame += 1
        self._spawn()
        self._update_enemies()
        self._update_projectiles()
        self._handle_kills()
        if not self.spawn_queue and not self.enemies and self.state == "PLAYING":
            self._level_cleared()
        if p.health.is_dead and self.state != "GAME_OVER":
            self._game_over()

    def _spawn(self):
        if not self.spawn_queue:
            return
        self.spawn_timer -= 1
        if self.spawn_timer > 0:
            return
        self.spawn_timer = self.config.spawn_interval
        key = self.spawn_queue.pop(0)
        size = self.factory.monster_class(key).SIZE
        enemy = self.factory.create(key, WIDTH - size - 10, random.randint(40, HEIGHT - size - 40),
                                    self.config.hp_mult, self.config.speed_mult)
        self.enemies.append(enemy)
        self.particles.add_ring(enemy.cx, enemy.cy, 55, enemy.color)

    def _update_poison(self):
        p = self.player
        if p.poison_timer > 0 and p.poison_timer % 30 == 0:
            p.health.take_damage(2)
            self.particles.emit_sparks(p.center[0], p.center[1], (120, 255, 60), 4)

    def _update_enemies(self):
        p = self.player
        px, py = p.center
        shots = [b for b in self.bullets if b.from_player]
        ctx = AIContext(px, py, self.enemies, self.frame, shots)
        for e in self.enemies:
            if not e.alive:
                continue
            for x, y, vx, vy, key in e.update(ctx):
                spec = ENEMY_SHOTS[key]
                self.bullets.append(Projectile(x, y, vx, vy, spec, spec, from_player=False))
        for ev in ctx.events:
            if ev[0] == "teleport":
                self.particles.emit_explosion(ev[1], ev[2], (230, 80, 230), 12, 3)
                self.particles.emit_explosion(ev[3], ev[4], (230, 80, 230), 12, 3)
                self.audio.play("teleport")
        # contact monstre / joueur
        prect = p.rect
        for e in self.enemies:
            if e.alive and prect.colliderect(_rect_of(e)) and p.hurt(e.contact_damage):
                self.audio.play("hurt")
                self.shake = max(self.shake, 6)

    def _update_projectiles(self):
        p = self.player
        for b in list(self.bullets):
            b.update()
            b.age += 1
            if b.off_screen():
                self.bullets.remove(b)
                continue
            if b.spec.shape in ("rocket", "plasma", "bolt") and b.age % 2 == 0:
                self.particles.emit_trail(b.x, b.y, b.spec.color)
            if b.from_player:
                point = (int(b.x), int(b.y))
                for e in self.enemies:
                    if not e.alive or id(e) in b.hit_ids:
                        continue
                    if _rect_of(e).inflate(b.radius * 2, b.radius * 2).collidepoint(point):
                        b.hit_ids.add(id(e))
                        self.damage_enemy(e, b.weapon)
                        b.spec.effect.apply(self, e, b)
                        if b.pierce_left > 0:
                            b.pierce_left -= 1
                        else:
                            self.bullets.remove(b)
                        break
            elif p.rect.inflate(b.radius * 2, b.radius * 2).collidepoint((int(b.x), int(b.y))):
                self.bullets.remove(b)
                if p.hurt(b.weapon.damage, 20):
                    if b.weapon.kind == "frost":
                        p.slow_timer = 120
                    elif b.weapon.kind == "poison":
                        p.poison_timer = 240
                    self.audio.play("hurt")
                    self.particles.emit_sparks(b.x, b.y, b.spec.color)

    def _update_pickups(self):
        p = self.player
        px, py = p.center
        rng = self.stats.magnet_range + (260 if "magnet" in p.effects else 0)
        for pk in list(self.pickups):
            d = pk.update(px, py, rng)
            if d < 24:
                self._collect(pk)
                self.pickups.remove(pk)
            elif pk.expired:
                self.pickups.remove(pk)

    def _collect(self, pk):
        if pk.kind == "coin":
            self.data.coins += pk.value
            self.audio.play("coin")
        else:
            POWERUPS[pk.kind].apply(self.player)
            self.audio.play("powerup")
            self.particles.add_ring(pk.x, pk.y, 50, POWERUPS[pk.kind].color)

    # ------------------------------------------------------------------
    # Mort des monstres, fin de niveau, fin de partie
    # ------------------------------------------------------------------
    def _handle_kills(self):
        dead = [e for e in self.enemies if not e.alive]
        for e in dead:
            self._on_kill(e)
        self.enemies = [e for e in self.enemies if e.alive]

    def _on_kill(self, e):
        self.score += e.xp * 2
        self.particles.emit_explosion(e.cx, e.cy, e.color, count=40 if e.is_boss else 26)
        self.particles.add_ring(e.cx, e.cy, 90 if e.is_boss else 55, e.color)
        self.shake = max(self.shake, 14 if e.is_boss else 7)
        self.audio.play("explosion")
        ups = self.stats.gain_xp(e.xp)
        if ups:
            self.pending_upgrades += ups
            self.audio.play("levelup")
            px, py = self.player.center
            self.particles.add_ring(px, py, 80, (255, 255, 120))
        n = min(5, max(1, e.coins // 5))
        for i in range(n):
            value = e.coins // n + (e.coins % n if i == 0 else 0)
            self.pickups.append(Pickup("coin", e.cx + random.randint(-25, 25),
                                       e.cy + random.randint(-25, 25), value))
        if e.is_boss or random.random() < self.POWERUP_CHANCE:
            self.pickups.append(Pickup(random_powerup_kind(), e.cx, e.cy))

    def snapshot(self, level):
        """Copie l'etat de la partie dans SaveData (pour Continue)."""
        self.stats.export()
        d = self.data
        d.has_run, d.game_level, d.score = True, level, self.score
        d.high_score = max(d.high_score, self.score)

    def _level_cleared(self):
        self.state = "LEVEL_CLEAR"
        self.banner = self.LEVEL_CLEAR_FRAMES
        self.snapshot(self.level + 1)
        self.needs_save = True
        self.audio.play("levelup")

    def _game_over(self):
        self.state = "GAME_OVER"
        d = self.data
        d.high_score = max(d.high_score, self.score)
        d.has_run, d.game_level, d.score = False, 1, 0
        self.stats.reset_run()
        self.stats.export()
        self.needs_save = True
        px, py = self.player.center
        self.particles.emit_explosion(px, py, (50, 205, 50), 50, 6)
        self.audio.play("explosion")
