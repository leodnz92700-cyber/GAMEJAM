"""
Fichier : main.py
Auteur : base technique (game jam)

Description :
Point d'entrée du jeu.

    python main.py                 # lance le jeu depuis l'ecran d'accueil
    python main.py --level 2       # demarre directement a l'etage 2
    python main.py --map level_test.tmx --skip-menu   # saute le menu (debug)

Tout le reste vit dans `src/`. Ce fichier ne contient volontairement aucune
logique de jeu : il crée la fenêtre et affiche la première vue.
"""
from __future__ import annotations

import argparse

import arcade

from src import constants as C


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Labyrinth of Shadow")
    parser.add_argument(
        "--level", type=int, default=1,
        help="etage de depart (1 = premier etage)",
    )
    parser.add_argument(
        "--map", type=str, default=None,
        help="charger une carte precise (ex: level_test.tmx), utile pour tester",
    )
    parser.add_argument(
        "--skip-menu", action="store_true",
        help="demarrer directement la partie, sans passer par l'ecran d'accueil",
    )
    parser.add_argument(
        "--mode", type=str, default=C.MODE_FREE, choices=list(C.GAME_MODES),
        help="mode de jeu utilise avec --skip-menu",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    window = arcade.Window(C.WINDOW_WIDTH, C.WINDOW_HEIGHT, C.WINDOW_TITLE)
    window.background_color = C.COLOR_BACKGROUND

    if args.skip_menu or args.map:
        from src.views.game_view import GameView

        level_names = [args.map] if args.map else None
        view = GameView(
            mode=args.mode,
            level_index=0 if args.map else max(0, args.level - 1),
            level_names=level_names,
        )
        view.setup()
    else:
        from src.views.main_menu import MainMenuView

        view = MainMenuView(level_index=max(0, args.level - 1))

    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
