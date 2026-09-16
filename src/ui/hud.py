"""
Fichier : hud.py
Auteur : base technique (game jam)

Description :
L'ATH, dessiné intégralement EN TRANSPARENCE par-dessus le jeu : il n'y a aucun
bandeau, le labyrinthe occupe tout l'écran. Chaque information est poussée dans
un coin pour laisser le centre libre.

  - en haut à gauche : l'étage et la zone ;
  - en haut à droite : le temps de la partie et le nombre de morts ;
  - en haut au centre : ce que le personnage entend (la créature qui approche) ;
  - en bas à droite : l'inventaire, surmonté des rappels de touches ;
  - en bas au centre : l'invite d'interaction et les messages temporaires.

Deux règles de game design à respecter :

  1. l'ATH n'affiche JAMAIS le temps restant avant l'arrivée de la créature. Le
     joueur ne dispose que des signaux sonores et du vacillement des torches. Le
     seul chronomètre autorisé est celui du mode « Contre-la-montre », qui est
     une règle de mode, pas la créature ;
  2. l'invite « E » n'apparaît que lorsqu'une interaction est réellement à
     portée (voir `mechanics/interaction_manager.find_target`). Pas de rappel de
     touche permanent : si le joueur voit « E », c'est qu'il y a quelque chose.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.entities.items import ITEM_TEXTURES
from src.entities.textures import load_single
from src.ui.key_icons import draw_keycap
from src.ui.text_cache import draw_text_shadowed

DIM_ALPHA = 105                # opacité d'un rappel de touche indisponible


class HUD:
    """Interface en surimpression : coins de l'écran, rien au centre."""

    def __init__(self):
        self.message = ""
        self.message_timer = 0.0
        # L'invite d'interaction doit être centrée AVEC sa touche : il faut donc
        # connaître la largeur du texte, d'où un objet Text conservé.
        self._prompt = arcade.Text(
            "", 0, 0, C.COLOR_TEXT, 14, anchor_y="baseline"
        )

    def show_message(self, text: str, duration: float = 2.8) -> None:
        if not text:
            return
        self.message = text
        self.message_timer = duration

    def update(self, delta_time: float) -> None:
        if self.message_timer <= 0:
            return
        self.message_timer -= delta_time
        if self.message_timer <= 0:
            self.message = ""

    # ------------------------------------------------------------------ #
    # Rendu
    # ------------------------------------------------------------------ #
    def draw(self, player, level, score, whisper: str = "", target=None) -> None:
        self._draw_floor_and_zone(level)
        self._draw_run_info(score)
        self._draw_inventory(player)
        self._draw_key_hints(player)
        self._draw_interaction_prompt(target)
        self._draw_center_texts(whisper)

    # -- haut gauche ---------------------------------------------------- #
    def _draw_floor_and_zone(self, level) -> None:
        top = C.WINDOW_HEIGHT - C.UI_MARGIN
        draw_text_shadowed(
            f"ETAGE {getattr(level, 'floor_number', 1)}",
            C.UI_MARGIN, top - 16, C.COLOR_TEXT, 17, bold=True,
        )
        zone_x, zone_y = level.zone
        draw_text_shadowed(
            f"zone {zone_x + 1}-{zone_y + 1}",
            C.UI_MARGIN, top - 34, C.COLOR_TEXT_DIM, 11,
        )

    # -- haut droite ---------------------------------------------------- #
    def _draw_run_info(self, score) -> None:
        right = C.WINDOW_WIDTH - C.UI_MARGIN
        top = C.WINDOW_HEIGHT - C.UI_MARGIN
        stats = score.stats

        # En mode chronométré, c'est le temps RESTANT qui compte pour le joueur.
        remaining_time = score.time_remaining()
        seconds = remaining_time if remaining_time is not None else stats.elapsed
        minutes, secs = divmod(int(seconds), 60)
        time_color = (
            C.COLOR_DANGER
            if remaining_time is not None and remaining_time <= 30
            else C.COLOR_TEXT
        )
        draw_text_shadowed(
            f"{minutes:02d}:{secs:02d}", right, top - 16, time_color, 17,
            anchor_x="right", bold=True,
        )

        remaining_deaths = score.deaths_remaining()
        if remaining_deaths is None:
            deaths = f"{stats.deaths_total} morts"
            color = C.COLOR_TEXT_DIM
        else:
            deaths = f"{stats.deaths_total} morts — {remaining_deaths} restantes"
            color = C.COLOR_DANGER if remaining_deaths <= 2 else C.COLOR_TEXT_DIM
        draw_text_shadowed(deaths, right, top - 34, color, 11, anchor_x="right")

    # -- bas droite : inventaire ---------------------------------------- #
    def _inventory_geometry(self, player) -> tuple[float, float, float]:
        """(x du bord gauche des cases, y du bas des cases, y du haut du bloc)."""
        capacity = player.inventory.capacity
        width = capacity * C.UI_SLOT_SIZE + (capacity - 1) * C.UI_SLOT_GAP
        left = C.WINDOW_WIDTH - C.UI_MARGIN - width
        bottom = C.UI_MARGIN
        return left, bottom, bottom + C.UI_SLOT_SIZE

    def _draw_inventory(self, player) -> None:
        left, bottom, top = self._inventory_geometry(player)
        draw_text_shadowed(
            "INVENTAIRE",
            C.WINDOW_WIDTH - C.UI_MARGIN, top + 10, C.COLOR_TEXT_DIM, 11,
            anchor_x="right",
        )

        for index in range(player.inventory.capacity):
            slot_left = left + index * (C.UI_SLOT_SIZE + C.UI_SLOT_GAP)
            arcade.draw_lbwh_rectangle_filled(
                slot_left, bottom, C.UI_SLOT_SIZE, C.UI_SLOT_SIZE, (14, 14, 20, 170)
            )
            arcade.draw_lbwh_rectangle_outline(
                slot_left, bottom, C.UI_SLOT_SIZE, C.UI_SLOT_SIZE, C.COLOR_HUD_BORDER, 1
            )
            if index >= len(player.inventory.items):
                continue
            # Le sprite de l'objet suffit à le reconnaître : pas de texte sous
            # la case, qui déborderait sur l'objet lui-même.
            item = player.inventory.items[index]
            texture = load_single(ITEM_TEXTURES.get(item.type, "item_key.png"))
            inset = 6
            arcade.draw_texture_rect(
                texture,
                arcade.LBWH(
                    slot_left + inset, bottom + inset,
                    C.UI_SLOT_SIZE - 2 * inset, C.UI_SLOT_SIZE - 2 * inset,
                ),
                pixelated=True,
            )

    # -- bas droite : rappels de touches, au-dessus de l'inventaire ------ #
    def _draw_key_hints(self, player) -> None:
        """
        Colonne discrète : boire la fiole, planter une torche.

        Une touche dont l'action n'est pas disponible est grisée plutôt que
        masquée : le joueur apprend qu'elle existe avant même d'avoir l'objet.

        Le déplacement n'est PAS rappelé : ZQSD est un réflexe acquis, l'afficher
        n'apprend rien et alourdit un coin qu'on veut discret.
        """
        right = C.WINDOW_WIDTH - C.UI_MARGIN
        _, _, top = self._inventory_geometry(player)
        row_y = top + 24 + C.UI_ROW_HEIGHT / 2        # au-dessus du titre INVENTAIRE

        for key, label, available in (
            ("F", "planter une torche", player.has_torch()),
            ("R", "boire la fiole", player.has_vial()),
        ):
            alpha = 255 if available else DIM_ALPHA
            draw_keycap(right - C.UI_KEYCAP_SIZE / 2, row_y, key, alpha=alpha)
            draw_text_shadowed(
                label,
                right - C.UI_KEYCAP_SIZE - 8, row_y - 4,
                (*C.COLOR_TEXT_DIM, alpha), 11, anchor_x="right",
            )
            row_y += C.UI_ROW_HEIGHT

    # -- bas centre : invite d'interaction ------------------------------ #
    def _draw_interaction_prompt(self, target) -> None:
        """L'invite n'existe que si une interaction est à portée."""
        if target is None:
            return
        self._prompt.text = target.prompt
        self._prompt.color = C.COLOR_TEXT if target.actionable else C.COLOR_TEXT_DIM

        keycap_width = C.UI_KEYCAP_SIZE + 10 if target.actionable else 0
        total = keycap_width + self._prompt.content_width
        left = (C.WINDOW_WIDTH - total) / 2
        row_y = C.UI_MARGIN + 52

        if target.actionable:
            draw_keycap(left + C.UI_KEYCAP_SIZE / 2, row_y, "E")
        # Ombre portée, puis le texte : même principe que draw_text_shadowed.
        self._prompt.x = left + keycap_width + 1
        self._prompt.y = row_y - 6
        original_color = self._prompt.color
        self._prompt.color = C.COLOR_TEXT_SHADOW
        self._prompt.draw()
        self._prompt.x -= 1
        self._prompt.y += 1
        self._prompt.color = original_color
        self._prompt.draw()

    # -- bas centre : messages, haut centre : la créature ---------------- #
    def _draw_center_texts(self, whisper: str) -> None:
        if self.message:
            draw_text_shadowed(
                self.message,
                C.WINDOW_WIDTH / 2, C.UI_MARGIN + 92, C.COLOR_TEXT, 14,
                anchor_x="center",
            )
        if whisper:
            draw_text_shadowed(
                whisper,
                C.WINDOW_WIDTH / 2, C.WINDOW_HEIGHT - C.UI_MARGIN - 16,
                C.COLOR_DANGER, 15, anchor_x="center", italic=True,
            )
