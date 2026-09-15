"""
Fichier : interaction_manager.py
Auteur : base technique (game jam)

Description :
Tout ce que le joueur déclenche volontairement : ramasser, fouiller un cadavre,
ouvrir une porte, parler à un PNJ, planter une torche, boire la fiole.

Une seule touche sert à interagir. L'ordre de priorité est important pour que le
jeu reste lisible dans le noir : on fouille un cadavre avant de ramasser un
objet au sol, et on ouvre une porte en dernier.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.entities.items import Item


def _nearest(sprites, x: float, y: float, radius: float):
    """Sprite le plus proche du point donné, dans le rayon d'interaction."""
    best = None
    best_distance = radius
    for sprite in sprites:
        distance = arcade.math.get_distance(sprite.center_x, sprite.center_y, x, y)
        if distance <= best_distance:
            best = sprite
            best_distance = distance
    return best


def _nearest_wide(sprites, x: float, y: float, radius: float):
    """
    Comme `_nearest`, mais mesure la distance au BORD du sprite.

    Indispensable pour les portes : elles font la largeur du passage (souvent
    4 tuiles), donc leur centre peut être très loin du joueur alors qu'il est
    collé contre le battant.
    """
    best = None
    best_distance = radius
    for sprite in sprites:
        nearest_x = min(max(x, sprite.left), sprite.right)
        nearest_y = min(max(y, sprite.bottom), sprite.top)
        distance = arcade.math.get_distance(nearest_x, nearest_y, x, y)
        if distance <= best_distance:
            best = sprite
            best_distance = distance
    return best


class InteractionManager:
    """Applique les actions du joueur sur le monde."""

    def __init__(self, audio, score):
        self.audio = audio
        self.score = score

    # ------------------------------------------------------------------ #
    # Touche "interagir"
    # ------------------------------------------------------------------ #
    def interact(self, player, level) -> str:
        """Exécute l'interaction la plus pertinente et renvoie un message pour le HUD."""
        x, y = player.position
        radius = C.INTERACTION_RADIUS

        # 1. Fouiller une dépouille : c'est ainsi qu'on récupère ce qu'on a
        #    laissé lors d'une vie précédente.
        corpse = _nearest(
            [corpse for corpse in level.corpse_list if corpse.has_items], x, y, radius
        )
        if corpse is not None:
            if player.inventory.is_full:
                return "Inventaire plein : impossible de fouiller."
            item = corpse.take_item()
            player.pick_up(item)
            self.score.stats.corpses_looted += 1
            self.audio.play("pickup")
            return f"Tu reprends {item.label.lower()} sur ton ancien corps."

        # 2. Ramasser un objet au sol.
        item_sprite = _nearest(level.item_list, x, y, radius)
        if item_sprite is not None:
            if player.inventory.is_full:
                return "Inventaire plein : laisse quelque chose derriere toi."
            player.pick_up(item_sprite.item)
            item_sprite.remove_from_sprite_lists()
            self.score.stats.items_picked += 1
            self.audio.play("pickup")
            return f"{item_sprite.item.label} ramassee."

        # 3. Ouvrir une porte.
        door = _nearest_wide(
            [door for door in level.door_list if not door.is_open], x, y, radius
        )
        if door is not None:
            return self._try_open_door(player, level, door)

        # 4. Parler à un PNJ.
        npc = _nearest(level.npc_list, x, y, radius + 12)
        if npc is not None:
            return npc.next_line()

        return ""

    def _try_open_door(self, player, level, door) -> str:
        if door.needs_key:
            key = player.has_key(door.key_id)
            if key is None:
                return "Verrouillee. Il te faut la cle."
            player.inventory.remove(key)
            level.open_door(door)
            self.score.stats.doors_opened += 1
            self.audio.play("door_open")
            return "La serrure cede."
        return "Cette porte est commandee par une plaque de pression."

    # ------------------------------------------------------------------ #
    # Torches
    # ------------------------------------------------------------------ #
    def plant_torch(self, player, level) -> str:
        """Plante une torche : la seule façon d'éclairer durablement le labyrinthe."""
        torch_item = player.inventory.find(C.ITEM_TORCH)
        if torch_item is None:
            return "Aucune torche a planter."
        player.inventory.remove(torch_item)
        level.add_torch(player.center_x, player.center_y)
        self.score.stats.torches_placed += 1
        self.audio.play("torch_place")
        return "Torche plantee. Cette zone restera eclairee."

    # ------------------------------------------------------------------ #
    # Sacrifice
    # ------------------------------------------------------------------ #
    def consume_vial(self, player) -> bool:
        """
        Retire une fiole de l'inventaire. Renvoie False si le joueur n'en a pas.

        La mort elle-même n'est PAS gérée ici : c'est `death_manager` qui décide
        des conséquences. Ce module ne fait que consommer l'objet.
        """
        vial: Item | None = player.inventory.find(C.ITEM_VIAL)
        if vial is None:
            return False
        player.inventory.remove(vial)
        return True
