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
TILE_SIZE = 32

# Une zone occupe exactement TOUT l'écran : il n'y a aucun bandeau d'interface,
# l'ATH est dessiné en transparence par-dessus le jeu. La taille de la fenêtre
# est donc un multiple exact de la tuile, pour qu'une zone tombe juste. La
# caméra ne suit jamais le joueur : elle saute d'une zone à l'autre quand il
# franchit une frontière.
ZONE_COLS = 40
ZONE_ROWS = 22
WINDOW_WIDTH = ZONE_COLS * TILE_SIZE          # 1280
WINDOW_HEIGHT = ZONE_ROWS * TILE_SIZE         # 704

# Le viewport de jeu, c'est l'écran entier. Ces alias restent pour la lisibilité
# du code de rendu (moteur de lumière, fondus, jumpscare).
VIEWPORT_WIDTH = WINDOW_WIDTH
VIEWPORT_HEIGHT = WINDOW_HEIGHT

ZONE_WIDTH = ZONE_COLS * TILE_SIZE
ZONE_HEIGHT = ZONE_ROWS * TILE_SIZE
ZONES_X = 2                           # nombre de zones par étage, en largeur
ZONES_Y = 2                           # ... et en hauteur
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
#
# La valeur n'est pas libre : (hauteur de l'image - hauteur de la boite) / 2,
# soit (48 - 16) / 2 = 16. En dessous, le bas du dessin depasse sous la boite de
# collision et les pieds sont dessines PAR-DESSUS la tuile d'en bas — mur, porte
# ou coffre : le personnage a l'air de marcher sur le decor.
PLAYER_ART_LIFT = 16
PLAYER_IDLE_FPS = 6.0
PLAYER_RUN_FPS = 12.0

# Mort volontaire : le héros s'effondre à l'écran avant que la vie suivante ne
# commence. La DERNIÈRE image de cette animation est aussi le sprite du cadavre,
# ce qui rend la transition invisible — c'est bien le corps du joueur qui reste
# sur place, et c'est lui qui bloquera les fléchettes.
# ATTENTION : la bande de mort n'a PAS le même format que les autres. Elle fait
# 6 images de 48x48, parce qu'un corps allongé est plus large qu'un personnage
# debout. La découper en 32 de large coupe chaque pose en deux et donne une
# animation qui clignote.
PLAYER_DEATH_FRAME_SIZE = (48, 48)
PLAYER_DEATH_FRAME_COUNT = 6
DEATH_ANIMATION_DURATION = 0.95
CORPSE_HIT_BOX = (30, 22)            # un corps allongé est large et bas

# --------------------------------------------------------------------------- #
# Animations du décor (nombre d'images des bandes du pack)
# --------------------------------------------------------------------------- #
TORCH_FRAME_COUNT = 3
TORCH_FPS = 7.0
# Piège à pointes : visible dès le départ, et il bat en continu. Le joueur voit
# le danger, apprend le rythme et passe entre deux jaillissements ; s'il veut
# mourir dessus pour y laisser son corps, il lui suffit d'attendre.
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
MONSTER_VISIBLE_RADIUS = 160.0   # au-delà, la créature reste invisible

# Jumpscare : quand la créature dévore le joueur, sa gueule remplit l'écran
# avant le noir. Sans ça, la mort la plus punitive du jeu passait inaperçue.
SCREAMER_FLASH_DURATION = 0.10       # éclair blanc
SCREAMER_FACE_DURATION = 0.85        # la gueule à l'écran, qui tremble
SCREAMER_FADE_DURATION = 0.45        # fondu au noir avant la vie suivante
SCREAMER_DURATION = (
    SCREAMER_FLASH_DURATION + SCREAMER_FACE_DURATION + SCREAMER_FADE_DURATION
)
SCREAMER_SHAKE = 26.0                # amplitude du tremblement, en pixels

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
# --- Le squelette archer ---------------------------------------------------- #
# Ce n'est plus une grille percée dans un mur mais un TIREUR : un squelette
# planté dans une grande salle, qui décoche ses flèches en travers de la pièce.
# On ne peut pas le tuer, on ne peut pas le contourner : il fait partie du décor,
# comme un piège. La seule parade est le CADAVRE, qui arrête les flèches.
#
# La cadence est volontairement infernale : une flèche toutes les 0,30 s, deux
# fois plus rapides que le joueur. La fenêtre pour traverser la ligne de tir
# existe, mais elle est si courte qu'on ne la trouve pas à l'aveugle : la
# première traversée se paie d'une mort, et c'est voulu. Poser son corps en
# travers de la trajectoire est la vraie réponse — pas un contournement.
ARCHER_DEFAULT_INTERVAL = 0.30        # secondes entre deux flèches
ARCHER_DEFAULT_SPEED = 330.0          # pixels par seconde (le joueur en fait 185)
ARCHER_SHOOT_ANIMATION = 0.26         # geste de tir, plus court que la cadence
ARCHER_RELEASE_FRAME = 5              # image où l'arc se détend (bande de tir : 6 images)
ARCHER_FRAME_SIZE = (32, 48)        # bandes du pack : 4 images au repos, 6 au tir
ARROW_RANGE = 9 * TILE_SIZE           # la flèche finit sa course : le danger reste dans la salle
ARROW_LIFETIME = 6.0                  # sécurité : une flèche perdue finit par disparaître
ARROW_HIT_BOX = (12, 6)               # petite boîte : c'est la pointe qui tue

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
COLOR_HUD_BACKGROUND = (18, 18, 24)   # encore utilisé par les menus
COLOR_HUD_BORDER = (52, 52, 66)
# L'ATH est posé en transparence sur le jeu : sans ombre portée, le texte
# devient illisible dès qu'il passe sur une zone éclairée.
COLOR_TEXT_SHADOW = (0, 0, 0, 190)
COLOR_KEYCAP_FILL = (26, 26, 34, 215)
COLOR_KEYCAP_BORDER = (126, 126, 148)
COLOR_KEYCAP_LABEL = (222, 222, 234)
COLOR_TEXT = (216, 216, 228)
COLOR_TEXT_DIM = (124, 124, 142)
COLOR_ACCENT = (198, 164, 96)
COLOR_DANGER = (188, 68, 68)
COLOR_CORPSE_GLOW = (120, 200, 220)
COLOR_TORCH_GLOW = (255, 176, 88)

# --------------------------------------------------------------------------- #
# Interface (tout est dessiné en transparence, sans aucun bandeau)
# --------------------------------------------------------------------------- #
UI_MARGIN = 22                        # marge depuis les bords de l'écran
UI_SLOT_SIZE = 50                     # case d'inventaire
UI_SLOT_GAP = 10
UI_KEYCAP_SIZE = 22                   # touche de clavier dessinée
UI_ROW_HEIGHT = 30                    # hauteur d'une ligne de rappel de touche

# --------------------------------------------------------------------------- #
# Types d'objets ramassables
# --------------------------------------------------------------------------- #
ITEM_KEY = "key"
ITEM_VIAL = "vial"
ITEM_TORCH = "torch"
ITEM_SHIELD = "shield"

# Objets UNIQUES et indispensables : s'ils disparaissent du niveau (bus, ou
# detruits avec le joueur par la creature), ils reviennent a l'endroit exact ou
# ils avaient ete poses par le level design. Sans cela, se faire devorer en
# portant la cle rendrait l'etage definitivement infinissable.
RESPAWNING_ITEM_TYPES = (ITEM_VIAL, ITEM_KEY, ITEM_SHIELD)

ITEM_LABELS = {
    ITEM_KEY: "Cle",
    ITEM_VIAL: "Fiole",
    ITEM_TORCH: "Torche",
    ITEM_SHIELD: "Bouclier",
}

# Même objet, mais tourné pour entrer dans une phrase : "Ramasser la fiole",
# "Tu reprends la cle". Évite les formulations télégraphiques de l'invite.
ITEM_PHRASES = {
    ITEM_KEY: "la cle",
    ITEM_VIAL: "la fiole",
    ITEM_TORCH: "la torche",
    ITEM_SHIELD: "le bouclier",
}

# --------------------------------------------------------------------------- #
# Causes de mort (death_manager)
# --------------------------------------------------------------------------- #
DEATH_VIAL = "vial"          # mort volontaire : cadavre + inventaire conserves
DEATH_TRAP = "trap"          # mort par piege : cadavre + inventaire conserves
DEATH_ARROW = "arrow"        # fleche de l'archer : mêmes conséquences qu'un piege
DEATH_DEVOURED = "devoured"  # mort par la creature : aucun cadavre, tout est perdu
