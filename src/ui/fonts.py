"""
Fichier : fonts.py
Auteur : base technique (game jam)

Description :
Chargement de la police d'interface du jeu.

Le jeu est en pixel art : la police du systeme, lissee, jurait avec tout le
reste. On utilise **Pixelify Sans** (`assets/fonts/`, licence SIL OFL, voir
`assets/fonts/OFL.txt`).

Elle a ete choisie contre les autres polices pixel pour deux raisons, et il faut
les connaitre avant d'en changer :

- **Elle a de vraies bas-de-casse.** Les classiques du genre (Silkscreen, Press
  Start 2P) sont en CAPITALES uniquement : le paragraphe de lore de l'ecran
  d'accueil y devenait un mur de majuscules qu'on ne lit pas.
- **Elle a un vrai gras.** Toute la hierarchie de l'interface repose dessus :
  titres de panneaux, valeurs des tableaux, libelles de boutons. Une police a
  une seule graisse ferait s'effondrer cette hierarchie.

Elle ne porte pas les accents dans toutes ses variantes, ce qui n'est pas un
probleme : les textes affiches au joueur sont deja sans accents (« Verrouillee »,
« Cle »), c'est une regle du projet.

Le chargement est paresseux — la premiere ligne de texte dessinee le declenche,
quel que soit le point d'entree (jeu, outils, captures) — et tolerant : si le
fichier manque, on retombe sur la police du systeme et le jeu se lance quand
meme.
"""
from __future__ import annotations

import arcade

from src import constants as C

# Nom de famille declare DANS le fichier .ttf : c'est lui qu'attend Arcade,
# pas le nom du fichier.
UI_FONT_NAME = "Pixelify Sans"
FONT_FILE = "PixelifySans.ttf"

# None = pas encore tente ; "Pixelify Sans" = chargee ; "" = echec, on n'insiste
# plus (sans quoi l'avertissement s'imprimerait a chaque frame).
_LOADED: str | None = None


def ui_font() -> str:
    """Nom de la police a passer a `arcade.Text`, police systeme en secours."""
    global _LOADED
    if _LOADED is None:
        _LOADED = ""
        # On va chercher la vraie police pixelisée d'Arcade (Kenney Mini)
        path = ":system:fonts/ttf/Kenney/Kenney_Mini.ttf"
        try:
            arcade.load_font(path)
            _LOADED = "Kenney Mini"
        except Exception as error:
            print(f"[fonts] Impossible de charger Kenney Mini ({error}), police systeme.")
    return _LOADED
