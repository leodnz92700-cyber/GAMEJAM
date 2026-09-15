"""
Fichier : constants.py
Auteur : base technique (game jam)

Description :
Toutes les constantes globales du jeu : fenêtre, zones, timings de la créature,
vitesses, couleurs, chemins des assets.

C'est LE fichier à ouvrir pour équilibrer le jeu. Aucune valeur de gameplay ne
doit être écrite en dur ailleurs : si vous avez besoin d'un nombre magique dans
un module, ajoutez-le ici.
"""
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Chemins
# --------------------------------------------------------------------------- #
ROOT_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT_DIR / "assets"
SPRITES_DIR = ASSETS_DIR / "sprites"
AUDIO_DIR = ASSETS_DIR / "audio"
MAPS_DIR = ASSETS_DIR / "maps"
DATA_DIR = ROOT_DIR / "data"
LEADERBOARD_PATH = DATA_DIR / "leaderboard.json"

# --------------------------------------------------------------------------- #
# Fenêtre et découpage en zones
# --------------------------------------------------------------------------- #
WINDOW_TITLE = "Labyrinth of Shadow"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

HUD_HEIGHT = 80                       # bandeau d'interface en bas de l'écran
VIEWPORT_WIDTH = WINDOW_WIDTH
VIEWPORT_HEIGHT = WINDOW_HEIGHT - HUD_HEIGHT

TILE_SIZE = 32
# Une zone occupe exactement le viewport : la caméra ne suit jamais le joueur,
# elle saute d'une zone à l'autre quand il franchit une frontière.
ZONE_COLS = VIEWPORT_WIDTH // TILE_SIZE      # 40
ZONE_ROWS = VIEWPORT_HEIGHT // TILE_SIZE     # 20
ZONE_WIDTH = ZONE_COLS * TILE_SIZE
ZONE_HEIGHT = ZONE_ROWS * TILE_SIZE
ZONE_TRANSITION_DURATION = 0.22              # petit fondu au noir au changement de zone

# --------------------------------------------------------------------------- #
# Joueur
# --------------------------------------------------------------------------- #
PLAYER_SPEED = 185.0                  # pixels par seconde
PLAYER_SPRITE_SCALE = 1.0
INVENTORY_CAPACITY = 2                # inventaire volontairement étriqué
INTERACTION_RADIUS = 46.0             # portée de la touche "interagir"

# Les sprites du pack font 32x48 alors que les couloirs les plus étroits font
# une seule tuile (32 px) : la boîte de collision est un petit rectangle centré,
# la tête et les pieds débordant volontairement sur les murs. Élargir cette
# boîte au-delà de 32 px rendrait les couloirs étroits infranchissables —
# `tools/walk_test.py` le détecte.
PLAYER_FRAME_SIZE = (32, 48)
PLAYER_HIT_BOX = (20, 16)
# Le sprite est dessine plus haut que son point de collision, pour que les pieds
# se posent au bord du couloir au lieu de s'enfoncer dans le mur d'en bas. Ce
# sont alors la tete et les epaules qui debordent sur le mur du haut, ce qui est
# la convention en vue de dessus : le personnage passe DEVANT le mur du fond.
PLAYER_ART_LIFT = 10
PLAYER_IDLE_FPS = 6.0
PLAYER_RUN_FPS = 12.0

# --------------------------------------------------------------------------- #
# Animations du décor (nombre d'images des bandes du pack)
# --------------------------------------------------------------------------- #
TORCH_FRAME_COUNT = 3
TORCH_FPS = 7.0
# Piège à pointes : une fois déclenché, il bat en continu. C'est ce qui le rend
# franchissable — dans un couloir d'une seule tuile, un piège mortel en
# permanence condamnerait le niveau. Le joueur apprend le rythme et passe entre
# deux jaillissements ; s'il veut mourir dessus, il lui suffit d'attendre.
SPIKE_FRAME_COUNT = 7
SPIKE_SAFE_DURATION = 1.9        # pointes rentrées : on peut traverser
SPIKE_STRIKE_DURATION = 1.1      # jaillissement puis redescente
SPIKE_CYCLE_DURATION = SPIKE_SAFE_DURATION + SPIKE_STRIKE_DURATION
SPIKE_LETHAL_FRAMES = (1, 2, 3)  # images où les pointes sont réellement sorties
PLATE_FRAME_COUNT = 3
MONSTER_FRAME_SIZE = (32, 48)
MONSTER_FPS = 6.0

# --------------------------------------------------------------------------- #
# La créature (le timer incarné)
# --------------------------------------------------------------------------- #
# Aucun compte à rebours n'est affiché : ces durées ne servent qu'à déclencher
# les signaux sonores. Le joueur doit apprendre à les lire.
MONSTER_RELEASE_TIME = 48.0           # secondes avant que la bête soit lâchée
MONSTER_SPEED = 165.0                 # légèrement plus lente que le joueur
MONSTER_KILL_RADIUS = 26.0
MONSTER_REPATH_INTERVAL = 0.45        # recalcul du chemin vers le joueur
MONSTER_VISIBLE_RADIUS = 160.0        # au-delà, elle reste invisible

# Paliers de tension, en fraction de MONSTER_RELEASE_TIME.
# À chaque palier franchi, monster_manager déclenche un signal d'ambiance.
TENSION_STAGES = (
    (0.00, "calm"),      # silence, nappe d'ambiance seule
    (0.45, "far"),       # grondements lointains
    (0.68, "near"),      # grattements contre les murs
    (0.86, "close"),     # pas qui courent, torches qui vacillent fort
    (1.00, "released"),  # elle est dans le labyrinthe
)

# --------------------------------------------------------------------------- #
# Lumière
# --------------------------------------------------------------------------- #
DARKNESS_ALPHA = 245                  # opacité du calque d'obscurité (0 = plein jour)
PLAYER_LIGHT_RADIUS = 180.0
TORCH_LIGHT_RADIUS = 260.0
CORPSE_LIGHT_RADIUS = 122.0
EXIT_LIGHT_RADIUS = 150.0
FLICKER_AMPLITUDE = 0.06              # vacillement normal des torches
FLICKER_PANIC_AMPLITUDE = 0.26        # vacillement quand la créature approche

# --------------------------------------------------------------------------- #
# Environnement
# --------------------------------------------------------------------------- #
DART_DEFAULT_INTERVAL = 1.8           # secondes entre deux tirs
DART_DEFAULT_SPEED = 260.0
DART_LIFETIME = 6.0

# --------------------------------------------------------------------------- #
# Modes de jeu (écran d'accueil)
# --------------------------------------------------------------------------- #
MODE_FREE = "free"
MODE_LIMITED_DEATHS = "limited_deaths"
MODE_TIMED = "timed"

GAME_MODES = {
    MODE_FREE: {
        "label": "Exploration",
        "description": "Ni limite de morts, ni chronometre. Pour decouvrir la tour.",
        "max_deaths": None,
        "time_limit": None,
    },
    MODE_LIMITED_DEATHS: {
        "label": "Sursis",
        "description": "8 morts maximum. Chaque sacrifice doit servir a quelque chose.",
        "max_deaths": 8,
        "time_limit": None,
    },
    MODE_TIMED: {
        "label": "Contre-la-montre",
        "description": "5 minutes pour atteindre le sommet, morts illimitees.",
        "max_deaths": None,
        "time_limit": 300.0,
    },
}

# --------------------------------------------------------------------------- #
# Niveaux (étages de la tour)
# --------------------------------------------------------------------------- #
LEVELS = ["level_01.tmx", "level_02.tmx"]
TEST_LEVEL = "level_test.tmx"

# --------------------------------------------------------------------------- #
# Couleurs
# --------------------------------------------------------------------------- #
COLOR_BACKGROUND = (10, 10, 14)
COLOR_HUD_BACKGROUND = (18, 18, 24)
COLOR_HUD_BORDER = (52, 52, 66)
COLOR_TEXT = (216, 216, 228)
COLOR_TEXT_DIM = (124, 124, 142)
COLOR_ACCENT = (198, 164, 96)
COLOR_DANGER = (188, 68, 68)
COLOR_CORPSE_GLOW = (120, 200, 220)
# Un cadavre qui porte encore des objets vire au doré et éclaire plus loin.
COLOR_CORPSE_LOOT_GLOW = (235, 200, 120)
CORPSE_LOOT_LIGHT_FACTOR = 1.35
COLOR_TORCH_GLOW = (255, 176, 88)

# --------------------------------------------------------------------------- #
# Types d'objets ramassables
# --------------------------------------------------------------------------- #
ITEM_KEY = "key"
ITEM_VIAL = "vial"
ITEM_TORCH = "torch"

# Objets UNIQUES et indispensables : s'ils disparaissent du niveau (bus, ou
# detruits avec le joueur par la creature), ils reviennent a l'endroit exact ou
# ils avaient ete poses par le level design. Sans cela, se faire devorer en
# portant la cle rendrait l'etage definitivement infinissable.
RESPAWNING_ITEM_TYPES = (ITEM_VIAL, ITEM_KEY)

ITEM_LABELS = {
    ITEM_KEY: "Cle",
    ITEM_VIAL: "Fiole",
    ITEM_TORCH: "Torche",
}

# --------------------------------------------------------------------------- #
# Causes de mort (death_manager)
# --------------------------------------------------------------------------- #
DEATH_VIAL = "vial"          # mort volontaire : cadavre + inventaire conserves
DEATH_TRAP = "trap"          # mort par piege : cadavre + inventaire conserves
DEATH_DEVOURED = "devoured"  # mort par la creature : aucun cadavre, tout est perdu
