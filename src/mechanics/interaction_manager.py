"""
Fichier : interaction_manager.py
Auteur : base technique (game jam)

Description :
Tout ce que le joueur déclenche volontairement : ramasser un objet au sol,
ouvrir une porte, parler à un PNJ, planter une torche, boire la fiole.

Une seule touche sert à interagir. L'ordre de priorité est important pour que le
jeu reste lisible dans le noir : on ramasse d'abord ce qui est au sol, on ouvre
une porte ensuite, on parle en dernier.

`find_target` répond à la question « que puis-je faire ici ? » et sert à la fois
à l'affichage de l'invite et à l'exécution de l'action, si bien que l'invite ne
peut jamais mentir.

Il n'y a PAS d'interaction avec les cadavres : les affaires d'une vie précédente
sont posées par terre autour du corps, et se ramassent comme le reste.
"""
from __future__ import annotations

from dataclasses import dataclass

import arcade

from src import constants as C
from src.entities.items import Item


@dataclass
class InteractionTarget:
    """
    Ce que le joueur peut faire, ici et maintenant.

    Cet objet est la source de vérité UNIQUE partagée par l'ATH et par l'action :
    l'invite « E » ne s'affiche que si `find_target` renvoie quelque chose, et
    appuyer sur E exécute exactement ce que l'invite annonçait. Impossible que
    l'affichage et le comportement divergent.
    """

    kind: str              # "item", "door" ou "npc"
    sprite: object
    prompt: str            # ce que lit le joueur : "Ramasser la cle"
    actionable: bool = True    # False = trop plein, porte verrouillee, etc.


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
    def find_target(self, player, level) -> InteractionTarget | None:
        """
        Ce que le joueur peut faire à sa position actuelle, ou None.

        Appelé à chaque frame par l'ATH : c'est ce qui permet de n'afficher
        l'invite « E » qu'au moment où une interaction est réellement à portée,
        au lieu d'un rappel de touches permanent.
        """
        x, y = player.position
        radius = C.INTERACTION_RADIUS

        # 1. Ramasser un objet au sol. Les affaires tombées d'un ancien corps
        #    sont des objets au sol comme les autres : rien à fouiller.
        item_sprite = _nearest(level.item_list, x, y, radius)
        if item_sprite is not None:
            full = player.inventory.is_full
            return InteractionTarget(
                kind="item",
                sprite=item_sprite,
                prompt=(
                    "Inventaire plein"
                    if full
                    else f"Ramasser {item_sprite.item.phrase}"
                ),
                actionable=not full,
            )

        # 2. Ouvrir une porte.
        door = _nearest_wide(
            [door for door in level.door_list if not door.is_open], x, y, radius
        )
        if door is not None:
            if not door.needs_key:
                return InteractionTarget(
                    kind="door",
                    sprite=door,
                    prompt="Commandee par une plaque de pression",
                    actionable=False,
                )
            has_key = player.has_key(door.key_id) is not None
            return InteractionTarget(
                kind="door",
                sprite=door,
                prompt="Ouvrir la porte" if has_key else "Verrouillee : il te faut la cle",
                actionable=has_key,
            )

        # 3. Parler à un PNJ.
        npc = _nearest(level.npc_list, x, y, radius + 12)
        if npc is not None:
            prompt = "Parler"
            if npc.wants_item and not npc.satisfied:
                item_name = C.ITEM_PHRASES.get(npc.wants_item, npc.wants_item)
                if player.inventory.find(npc.wants_item):
                    prompt = f"Donner {item_name}"
            return InteractionTarget(kind="npc", sprite=npc, prompt=prompt)

        return None

    def interact(self, player, level) -> str:
        """Exécute l'interaction proposée par `find_target` et renvoie un message."""
        target = self.find_target(player, level)
        if target is None:
            return ""
        if not target.actionable:
            return target.prompt

        if target.kind == "item":
            return self._pick_up(player, target.sprite)
        if target.kind == "door":
            return self._open_door(player, level, target.sprite)
            
        npc = target.sprite
        if npc.wants_item and not npc.satisfied:
            item = player.inventory.find(npc.wants_item)
            if item is None:
                return npc.next_line()
            player.inventory.remove(item)
            npc.satisfied = True
            
            # Create the key
            key_id = getattr(npc, "properties", {}).get("key_id")
            key_item = Item(C.ITEM_KEY, {"key_id": key_id} if key_id else {})
            from src.entities.items import ItemSprite
            
            # NPC change de dialogue pour remercier le joueur
            npc.lines = ["Merci pour mon bouclier !", "Tiens, prends cette cle en echange.", "Fais attention a toi..."]
            npc.line_index = 0
            
            if not player.inventory.is_full:
                player.pick_up(key_item)
                self.audio.play("pickup")
                return npc.next_line()
            else:
                sprite = ItemSprite(key_item, npc.center_x, npc.center_y - 20)
                level.item_list.append(sprite)
                return npc.next_line()
                
        return npc.next_line()

    def _pick_up(self, player, item_sprite) -> str:
        item = item_sprite.item
        player.pick_up(item)
        item_sprite.remove_from_sprite_lists()
        self.audio.play("pickup")
        if item.properties.get("dropped"):
            self.score.stats.corpses_looted += 1
            return f"Tu reprends {item.phrase} pres de ton ancien corps."
        self.score.stats.items_picked += 1
        return f"Tu ramasses {item.phrase}."

    def _open_door(self, player, level, door) -> str:
        key = player.has_key(door.key_id)
        if key is None:                      # garde-fou : `find_target` l'a déjà filtré
            return "Verrouillee. Il te faut la cle."
        player.inventory.remove(key)
        level.open_door(door)
        self.score.stats.doors_opened += 1
        self.audio.play("door_open")
        return "La serrure cede."

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
