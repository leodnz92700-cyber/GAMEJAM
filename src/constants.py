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
UI_DIR = ASSETS_DIR / "ui"          # images d'interface (logo), pas du decor
LOGO_PATH = UI_DIR / "logo.png"     # titre du jeu, dessine sur l'ecran d'accueil
AUDIO_DIR = ASSETS_DIR / "audio"
FONTS_DIR = ASSETS_DIR / "fonts"    # police pixel de l'interface (voir src/ui/fonts.py)
MAPS_DIR = ROOT_DIR / "map" / "tiled"
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
ZONE_ROWS = 20
WINDOW_WIDTH = ZONE_COLS * TILE_SIZE          # 1280
WINDOW_HEIGHT = ZONE_ROWS * TILE_SIZE         # 640 (ZONE_ROWS est passe de 22 a 20)

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
INVENTORY_CAPACITY = 3                # inventaire volontairement étriqué
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
MONSTER_RELEASE_TIME = 60.0           # 1 minute comme demandé
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
    (0.00, "calm"),      # silence : seuls les bruits d'ambiance aleatoires
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
        "description": "5 minutes pour trouver la sortie, morts illimitees.",
        "max_deaths": None,
        "time_limit": 300.0,
    },
}

# --------------------------------------------------------------------------- #
# Niveau
# --------------------------------------------------------------------------- #
# Le jeu ne contient volontairement QU'UN SEUL niveau : il n'y a ni ascension
# d'etages, ni ecran de selection. Atteindre la sortie, c'est gagner la partie.
# Si un jour la tour reprend plusieurs etages, c'est ici que ca recommence — et
# il faudra reintroduire un enchainement dans `LevelManager`.
LEVEL_NAME = "map.tmx"
TEST_LEVEL = "level_test.tmx"

# --------------------------------------------------------------------------- #
# Couleurs
# --------------------------------------------------------------------------- #
# La palette de l'INTERFACE est relevee sur le logo du jeu : un lisere dore
# (255, 244, 149) autour de lettres rouge sang (88, 19, 15). D'ou un accent or
# chaud sur un noir legerement rougi, et des gris tirant sur le brun plutot que
# sur le bleu. Le rouge profond du logo est trop sombre pour du texte : le rouge
# de danger est la meme teinte, remontee jusqu'a etre lisible.
COLOR_BACKGROUND = (12, 9, 9)

# --- Interface : panneaux et bordures --------------------------------------- #
# Les menus sont faits de panneaux sombres a bord net (aucun arrondi : le jeu
# est en pixel art) que l'on pose sur le fond noir.
COLOR_PANEL_FILL = (20, 15, 15)
COLOR_PANEL_FILL_SOFT = (29, 22, 21)   # fond des lignes paires d'un tableau
COLOR_HUD_BORDER = (68, 54, 46)        # bord au repos (ATH, panneaux, cases)
COLOR_PANEL_BORDER_ACTIVE = (214, 172, 94)    # bord d'un element selectionne
COLOR_RULE = (52, 40, 34)              # filets de separation dans les tableaux

# L'ATH est posé en transparence sur le jeu : sans ombre portée, le texte
# devient illisible dès qu'il passe sur une zone éclairée.
COLOR_TEXT_SHADOW = (0, 0, 0, 190)
COLOR_KEYCAP_FILL = (28, 21, 20, 215)
COLOR_KEYCAP_BORDER = (140, 122, 104)
COLOR_KEYCAP_LABEL = (234, 226, 212)
COLOR_TEXT = (230, 222, 210)
COLOR_TEXT_DIM = (148, 132, 118)
COLOR_TEXT_FAINT = (98, 84, 74)        # sous-titre d'un element non selectionne
COLOR_ACCENT = (243, 214, 124)         # l'or du lisere du logo
COLOR_ACCENT_DIM = (148, 112, 58)      # le meme, en retrait
COLOR_DANGER = (203, 66, 54)           # le rouge du logo, remonte pour etre lisible

# --- Lumieres du JEU (rien a voir avec la palette de l'interface) ------------ #
# Ces deux teintes doivent rester tres differentes l'une de l'autre : dans le
# noir, c'est a leur couleur que le joueur reconnait de loin une torche plantee
# d'un cadavre. Le cadavre reste donc FROID meme si l'interface est chaude —
# deux lueurs dorees seraient impossibles a distinguer.
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

# --------------------------------------------------------------------------- #
# Son
# --------------------------------------------------------------------------- #
# Tout le mixage du jeu est ici : c'est le seul endroit a ouvrir pour regler le
# son sans lire une ligne de code. `src/mechanics/audio_manager.py` ne connait
# que les CHEMINS des fichiers, jamais leur volume.
#
# Regle de game design qui commande tout ce bloc : il n'y a AUCUN compte a
# rebours affiche. Le son est la seule horloge du joueur — les quatre alertes du
# monstre, la respiration qui s'affole, la musique de poursuite. Baisser ces
# volumes, c'est retirer au joueur sa seule information.
AUDIO_MASTER_VOLUME = 0.8             # volume general, applique a tout le reste

# Volume de chaque son, par nom logique (voir SOUND_FILES dans audio_manager).
#
# Ces valeurs ne sont PAS choisies a l'oreille, elles sont CALCULEES : les
# fichiers livres n'ont pas du tout le meme niveau d'enregistrement (34 dB
# d'ecart entre le clic de menu et la respiration, soit un facteur 50), donc un
# meme coefficient donne un resultat completement different d'un son a l'autre.
# Chaque valeur ramene son fichier au niveau de sortie voulu pour son ROLE.
#
# `.venv/bin/python tools/check_audio_levels.py` mesure les fichiers, verifie
# que tout sort au bon niveau et donne la valeur a mettre ici. **Relancez-le
# apres avoir remplace un fichier audio** : un son enregistre plus fort que
# l'ancien desequilibre tout le mixage sans que rien ne le signale en jeu.
#
# Les quatre niveaux de sortie, du plus discret au plus present :
#   repetitif  ce qui sonne plusieurs fois par seconde (pas, fleches, survol)
#   discret    le decor et l'ambiance : presents, sans attirer l'oreille
#   normal     les actions du joueur : ramasser, ouvrir, planter
#   marquant   ce qui previent d'un danger ou fait sursauter
#   boucle     les sons continus, qui fatiguent vite s'ils sont forts
#   souffle    la respiration seule : un fond permanent, elle passe sous tout
#
# Le dBFS indique en commentaire est le niveau du FICHIER : plus il est bas,
# plus le fichier a ete enregistre faible, et plus son coefficient doit monter.
AUDIO_VOLUMES = {
    # --- Joueur ---------------------------------------------------------- #
    "footstep": 0.08,          # repetitif — fichier tres fort (-10 dBFS)
    "breathing": 0.40,         # souffle — volume de base, monte par la tension
    "pain": 0.51,              # marquant
    # --- Objets ---------------------------------------------------------- #
    "potion_get": 0.77,        # normal
    "potion_use": 0.24,        # marquant — la mort volontaire doit s'entendre
    "key_get": 0.80,           # normal — fichier faible (-23 dBFS)
    "key_use": 0.49,           # normal — se superpose a l'ouverture de la porte
    "torch_get": 0.80,         # normal — fichier faible (-23 dBFS)
    "torch_use": 0.70,         # normal
    "pickup": 0.19,            # normal — objets sans son dedie (le bouclier)
    # --- Environnement ---------------------------------------------------- #
    "door_open": 0.75,         # normal
    "door_locked": 0.79,       # normal — c'est une reponse a une action du joueur
    "plate_press": 0.32,       # discret
    "plate_release": 0.25,     # discret
    "spike_strike": 0.12,      # discret — fichier tres fort (-10 dBFS)
    "arrow_shot": 0.09,        # repetitif — une toutes les 0,3 s, le moindre exces sature
    # --- Ambiance ---------------------------------------------------------- #
    "water_drop": 0.24,        # discret
    "squeak": 0.30,            # discret
    "menu_music": 0.45,        # boucle — MP3, seul reglage encore fait a l'oreille
    # --- Interface --------------------------------------------------------- #
    "ui_hover": 0.81,          # repetitif — fichier tres faible (-30 dBFS)
    "ui_click": 0.13,          # normal — fichier le plus fort du jeu (-7 dBFS)
    # --- Le monstre -------------------------------------------------------- #
    "alert_far": 0.80,         # marquant — fichier faible (-20 dBFS)
    "alert_near": 0.27,        # marquant
    "alert_close": 0.81,       # marquant — fichier faible (-20 dBFS)
    "alert_released": 0.37,    # marquant
    "monster_released": 0.64,  # marquant — se superpose a l'alerte du lacher
    "monster_chase": 0.31,     # boucle
    "monster_kill": 0.80,      # marquant — fichier faible (-20 dBFS)
    # --- Fin de partie ----------------------------------------------------- #
    "victory": 0.23,           # marquant
    "game_over": 0.24,         # marquant
}

# --- Pas du joueur ---------------------------------------------------------- #
AUDIO_FOOTSTEP_INTERVAL = 0.34        # secondes entre deux pas (cale sur PLAYER_SPEED)

# --- Respiration ------------------------------------------------------------ #
# Deux regimes : un souffle qui revient de temps en temps quand tout est calme,
# et un halettement continu quand la bete se rapproche.
#
# Elle est volontairement RARE et DISCRETE. C'est un son de fond permanent : dix
# secondes de trop ou trois decibels de trop et elle passe de "le personnage a
# peur" a "quelqu'un souffle dans le micro". Le halettement continu ne demarre
# qu'au palier `close`, l'avant-dernier : arrive des `near`, il tournait pendant
# la moitie de la partie et ne signalait plus rien.
# Attention en reglant ces deux valeurs : la phase calme ne dure qu'une
# quarantaine de secondes par vie (ensuite le halettement continu prend le
# relais). Un delai mini superieur a ~40 s revient a ne plus jamais entendre le
# souffle occasionnel.
AUDIO_BREATH_RANDOM_MIN = 30.0        # delai mini entre deux souffles au calme
AUDIO_BREATH_RANDOM_MAX = 60.0        # ... et delai maxi
AUDIO_BREATH_CALM_VOLUME = 0.75       # le souffle occasionnel, un peu sous le halettement
AUDIO_BREATH_PANIC_STAGES = ("close", "released")   # a partir d'ici, en continu

# --- Ambiance aleatoire ----------------------------------------------------- #
# Il n'y a PLUS de nappe de fond : le silence est le fond sonore du jeu, troue
# de temps en temps par une goutte d'eau ou un grincement. C'est ce silence qui
# rend les alertes du monstre audibles.
AUDIO_AMBIENCE_MIN_DELAY = 7.0        # delai mini entre deux bruits d'ambiance
AUDIO_AMBIENCE_MAX_DELAY = 20.0       # ... et delai maxi

# Poids de tirage de chaque bruit d'ambiance. La goutte d'eau est courte et
# discrete, on peut l'entendre souvent sans lasser ; le grincement dure dix
# secondes et devient vite envahissant. D'ou quatre gouttes pour un grincement.
AUDIO_AMBIENCE_WEIGHTS = {
    "water_drop": 4,
    "squeak": 1,
}

# --- Sons du decor : pieges a pointes et fleches ----------------------------- #
# Ces deux sons se repetent sans arret (un piege toutes les 3 s, une fleche
# toutes les 0,3 s). Ils sont donc attenues avec la distance au joueur : c'est ce
# qui permet de localiser le danger a l'oreille dans le noir, au lieu de subir un
# vacarme permanent.
#
# Trois reglages, et ils comptent tous les trois :
#   - RANGE decide a partir d'ou on commence a percevoir quelque chose ;
#   - MIN_VOLUME est le "tout petit peu" qu'on entend a cette limite. Sans lui, le
#     son apparait a zero et le joueur a l'impression d'un interrupteur ;
#   - CURVE courbe la montee. A 1.0 elle est lineaire ; plus la valeur monte,
#     plus le son reste discret de loin et grimpe vite dans les dernieres tuiles.
AUDIO_NEAR_RANGE = 8 * TILE_SIZE      # au-dela de 8 tuiles, silence complet
AUDIO_NEAR_MIN_VOLUME = 0.12          # volume percu pile a la limite de portee
AUDIO_NEAR_CURVE = 2.0                # 1 = lineaire, 2 = discret de loin, franc de pres

# --- Musique de poursuite --------------------------------------------------- #
# La creature n'est DESSINEE qu'a tres courte distance (MONSTER_VISIBLE_RADIUS).
# La musique, elle, se declenche plus tot : le joueur doit l'entendre arriver
# avant de la voir, sinon il meurt avant d'avoir compris. Le delai d'arret evite
# que la musique clignote quand elle tourne autour de lui.
AUDIO_CHASE_RADIUS = 340.0            # distance a laquelle la poursuite se declenche
AUDIO_CHASE_RELEASE_DELAY = 3.0       # secondes de musique apres qu'elle s'est eloignee
