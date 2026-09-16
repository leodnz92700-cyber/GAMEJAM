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
from src.entities.items import Item, ItemSprite


@dataclass
class InteractionTarget:
    """
    Ce que le joueur peut faire, ici et maintenant.

    Cet objet est la source de vérité UNIQUE partagée par l'ATH et par l'action :
    l'invite « J » ne s'affiche que si `find_target` renvoie quelque chose, et
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
        l'invite « J » qu'au moment où une interaction est réellement à portée,
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

        # 3. Parler à un PNJ. L'invite annonce le troc dès qu'il est possible :
        #    sans l'objet, le PNJ se contente de le réclamer.
        npc = _nearest(level.npc_list, x, y, radius + 12)
        if npc is not None:
            prompt = "Parler"
            if npc.wants_item and player.inventory.find(npc.wants_item):
                item_name = C.ITEM_PHRASES.get(npc.wants_item, npc.wants_item)
                prompt = f"Donner {item_name}"
            return InteractionTarget(kind="npc", sprite=npc, prompt=prompt)

        return None

    def interact(self, player, level) -> str:
        """Exécute l'interaction proposée par `find_target` et renvoie un message."""
        target = self.find_target(player, level)
        if target is None:
            return ""
        if not target.actionable:
            # La serrure resiste : le bruit dit au joueur que l'action a bien ete
            # tentee et qu'elle a echoue, la ou un simple texte gris passe
            # inapercu dans le noir.
            if target.kind == "door":
                self.audio.play("door_locked")
            return target.prompt

        if target.kind == "item":
            return self._pick_up(player, target.sprite)
        if target.kind == "door":
            return self._open_door(player, level, target.sprite)
            
        return self._talk(player, level, target.sprite)

    # ------------------------------------------------------------------ #
    # PNJ : le troc en deux temps
    # ------------------------------------------------------------------ #
    def _talk(self, player, level, npc) -> str:
        """
        Dialogue et échange, REJOUABLE autant de fois que le joueur le veut.

        Ce que dit le PNJ ne dépend que de ce que le joueur porte à cet instant :
          - sans l'objet réclamé, il le RÉCLAME (ses répliques de la carte) ;
          - avec l'objet, il le prend et rend une CLÉ en disant d'aller s'en
            servir.

        Rien n'est mémorisé : revenir avec un second bouclier redonne une seconde
        clé. C'est cohérent avec la duplication des objets à la mort — les clés
        se multiplient comme le reste, et le joueur peut s'en faire un stock au
        prix d'un aller-retour. C'est aussi ce qui garantit qu'une clé dévorée
        par la créature est toujours récupérable.

        La clé est remise même le sac plein : elle tombe alors aux pieds du PNJ,
        plutôt que de disparaître parce que le joueur avait deux torches sur lui.
        """
        if not npc.wants_item:
            return npc.next_line()

        item = player.inventory.find(npc.wants_item)
        if item is None:
            # Il réclame. Si la carte n'a pas écrit de réplique, on en fabrique
            # une : le joueur doit toujours comprendre ce qu'on attend de lui.
            if npc.lines == ["..."]:
                wanted = C.ITEM_PHRASES.get(npc.wants_item, npc.wants_item)
                return f"Va me chercher {wanted}, et je te donnerai une cle."
            return npc.next_line()

        player.inventory.remove(item)
        key_id = getattr(npc, "properties", {}).get("key_id")
        key_item = Item(C.ITEM_KEY, {"key_id": key_id} if key_id else {})
        if player.inventory.is_full:
            # Garde-fou : l'objet est retire AVANT que la cle soit rendue, donc
            # avec un seul objet echange contre un seul il reste toujours une
            # place. Ce cas ne sert que si un PNJ rend un jour plus d'un objet.
            level.item_list.append(ItemSprite(key_item, npc.center_x, npc.center_y - 20))
            return "Ton sac est plein : il pose la cle a tes pieds. Va t'en servir."
        player.pick_up(key_item)
        self.audio.play_item_pickup(C.ITEM_KEY)
        return "Voila ta cle. Va t'en servir sur la porte."

    def _pick_up(self, player, item_sprite) -> str:
        item = item_sprite.item
        player.pick_up(item)
        item_sprite.remove_from_sprite_lists()
        self.audio.play_item_pickup(item.type)
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
        # Deux sons superposes, comme demande : le tour de cle et le battant.
        self.audio.play("key_use")
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
        self.audio.play("torch_use")
        return "Torche plantee. Cette zone restera eclairee."

    # ------------------------------------------------------------------ #
    # Lacher un objet
    # ------------------------------------------------------------------ #
    def drop_item(self, player, level) -> str:
        """
        Lache le PREMIER objet du sac, aux pieds du joueur.

        Il n'y a volontairement aucune selection d'objet : l'inventaire est
        minuscule et une case a choisir, dans le noir, coute plus au joueur
        qu'elle ne lui rend. L'objet redevient un objet au sol ordinaire, donc
        ramassable — rien n'est jamais detruit, le niveau reste finissable.
        """
        if not player.inventory.items:
            return "Ton sac est vide."
        item = player.inventory.items[0]
        player.inventory.remove(item)
        level.place_item_near(player.center_x, player.center_y, item)
        self.audio.play_item_pickup(item.type)
        return f"Tu laisses {item.phrase} au sol."

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
        # Le son part ICI et pas dans `death_manager` : la mort n'y est traitee
        # qu'une fois le personnage effondre, presque une seconde plus tard, et
        # le joueur n'entendrait sa gorgee qu'apres etre tombe.
        self.audio.play("potion_use")
        return True
