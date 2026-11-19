# TP4 - Shooter 2D (POO + SOLID)

Lancer : `py game_tp4.py`   (Python 3 + `pip install pygame`)
Tests logique : `py -m pip install pytest` puis `py -m pytest test_tp4.py`

## Fichiers
- `game_oop.py`, `homework_monsters.py` : le TP3, NON modifies
- `game_tp4.py` : point d'entree
- `tp4/` : toutes les nouveautes (voir tableau)

| Module | Role (SRP) |
|---|---|
| `entities.py` | PlayerTP4 (herite de Player), Projectile (herite de Bullet), Pickup |
| `board.py` | GameBoardTP4 (herite de GameBoard) : regles, niveaux, drops, XP |
| `render.py` | GameRendererTP4 (herite de GameRenderer) : animations, effets, HUD |
| `enemies.py` | nouveaux monstres, comportements IA (Strategy), attaques, fabrique |
| `weapons.py` | 7 armes + effets d'impact (explosion, glace, eclair) |
| `powerups.py` | Health, Shield, Double Damage, Double Speed, Rapid Fire, Magnet |
| `progression.py` | XP/niveaux joueur, niveaux illimites + boss, boutique |
| `effects.py`, `background.py` | particules, parallaxe |
| `audio.py` | musique + sons generes par le code, volumes |
| `save.py` | savegame.json (high score, coins, niveau, unlocks) |
| `screens.py`, `app.py` | menu, options, credits, pause, level up, boutique, game over |

## Controles
Fleches/WASD bouger | ESPACE tirer (maintenir) | 1-7 ou Q/E arme | P ou Echap pause | B boutique (entre deux niveaux)

## Optionnel
- Images : `assets/` (hero.png, background.png, monster_*.png, boss_*.png) - sinon formes animees par defaut
- Sons : `assets/sounds/<nom>.wav` remplace le son genere (shoot, laser, rocket, hit, explosion, coin, powerup, levelup, hurt, click, teleport, boss, music)
