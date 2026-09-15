"""
Fichier : hud.py
Auteur : base technique (game jam)

Description :
Bandeau d'interface en bas de l'écran : étage courant, inventaire, rappel des
touches, et contraintes du mode de jeu.

Règle de game design à respecter : le HUD n'affiche JAMAIS le temps restant
avant l'arrivée de la créature. Le joueur ne dispose que des signaux sonores et
du vacillement des torches. Le seul chronomètre autorisé est celui du mode
"Contre-la-montre", qui est une règle de mode, pas la créature.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.entities.items import ITEM_TEXTURES
from src.entities.textures import load_single
from src.ui.text_cache import draw_text_cached

SLOT_SIZE = 46


class HUD:
    """Bandeau inférieur + messages temporaires affichés au-dessus."""

    def __init__(self):
        self.message = ""
        self.message_timer = 0.0

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
    def draw(self, player, level, score, whisper: str = "") -> None:
        self._draw_band()
        self._draw_floor_and_zone(level)
        self._draw_inventory(player)
        self._draw_mode_info(score)
        self._draw_controls()
        self._draw_overlay_texts(whisper)

    def _draw_band(self) -> None:
        arcade.draw_lbwh_rectangle_filled(
            0, 0, C.WINDOW_WIDTH, C.HUD_HEIGHT, C.COLOR_HUD_BACKGROUND
        )
        arcade.draw_line(0, C.HUD_HEIGHT, C.WINDOW_WIDTH, C.HUD_HEIGHT, C.COLOR_HUD_BORDER, 2)

    def _draw_floor_and_zone(self, level) -> None:
        draw_text_cached("ETAGE", 20, C.HUD_HEIGHT - 26, C.COLOR_TEXT_DIM, 11)
        draw_text_cached(
            str(getattr(level, "floor_number", 1)), 20, C.HUD_HEIGHT - 56, C.COLOR_TEXT, 20
        )
        zone_x, zone_y = level.zone
        draw_text_cached(
            f"zone {zone_x + 1}-{zone_y + 1}", 56, C.HUD_HEIGHT - 52, C.COLOR_TEXT_DIM, 11
        )

    def _draw_inventory(self, player) -> None:
        draw_text_cached("SAC", 150, C.HUD_HEIGHT - 26, C.COLOR_TEXT_DIM, 11)
        for index in range(player.inventory.capacity):
            left = 150 + index * (SLOT_SIZE + 10)
            bottom = C.HUD_HEIGHT - 64
            arcade.draw_lbwh_rectangle_outline(
                left, bottom, SLOT_SIZE, SLOT_SIZE, C.COLOR_HUD_BORDER, 2
            )
            if index >= len(player.inventory.items):
                continue
            item = player.inventory.items[index]
            # On affiche le vrai sprite de l'objet : dans le noir, le joueur
            # doit reconnaitre son inventaire d'un coup d'oeil.
            texture = load_single(ITEM_TEXTURES.get(item.type, "item_key.png"))
            arcade.draw_texture_rect(
                texture,
                arcade.LBWH(left + 7, bottom + 7, SLOT_SIZE - 14, SLOT_SIZE - 14),
                pixelated=True,
            )
            draw_text_cached(item.label, left, bottom - 15, C.COLOR_TEXT_DIM, 10)

    def _draw_mode_info(self, score) -> None:
        stats = score.stats
        draw_text_cached("MORTS", 330, C.HUD_HEIGHT - 26, C.COLOR_TEXT_DIM, 11)
        draw_text_cached(
            str(stats.deaths_total), 330, C.HUD_HEIGHT - 56, C.COLOR_TEXT, 20
        )

        remaining_deaths = score.deaths_remaining()
        if remaining_deaths is not None:
            color = C.COLOR_DANGER if remaining_deaths <= 2 else C.COLOR_TEXT_DIM
            draw_text_cached(
                f"il t'en reste {remaining_deaths}", 380, C.HUD_HEIGHT - 52, color, 11
            )

        remaining_time = score.time_remaining()
        if remaining_time is not None:
            minutes, seconds = divmod(int(remaining_time), 60)
            color = C.COLOR_DANGER if remaining_time <= 30 else C.COLOR_TEXT
            draw_text_cached("TEMPS", 520, C.HUD_HEIGHT - 26, C.COLOR_TEXT_DIM, 11)
            draw_text_cached(
                f"{minutes:02d}:{seconds:02d}", 520, C.HUD_HEIGHT - 56, color, 20
            )

    def _draw_controls(self) -> None:
        draw_text_cached(
            "ZQSD / fleches : avancer     E : interagir     F : planter une torche"
            "     R : boire la fiole     ECHAP : menu",
            C.WINDOW_WIDTH - 20,
            C.HUD_HEIGHT - 50,
            C.COLOR_TEXT_DIM,
            11,
            anchor_x="right",
        )

    def _draw_overlay_texts(self, whisper: str) -> None:
        """Messages flottants juste au-dessus du bandeau."""
        if self.message:
            draw_text_cached(
                self.message,
                C.WINDOW_WIDTH / 2,
                C.HUD_HEIGHT + 22,
                C.COLOR_TEXT,
                15,
                anchor_x="center",
            )
        if whisper:
            draw_text_cached(
                whisper,
                C.WINDOW_WIDTH / 2,
                C.WINDOW_HEIGHT - 44,
                C.COLOR_DANGER,
                16,
                anchor_x="center",
                italic=True,
            )
