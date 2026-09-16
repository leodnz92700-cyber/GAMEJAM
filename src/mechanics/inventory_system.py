"""
Fichier : inventory_system.py
Auteur : base technique (game jam)

Description :
Inventaire du joueur, volontairement minuscule (2 emplacements par défaut).

La contrainte est un choix de game design : comme rien n'est conservé après la
mort, le joueur doit décider à chaque vie de ce qu'il emporte et de ce qu'il
laisse sur une dépouille pour plus tard.
"""
from __future__ import annotations

from src import constants as C
from src.entities.items import Item


class Inventory:
    """Sac à dos limité : premier arrivé, premier rangé."""

    def __init__(self, capacity: int = C.INVENTORY_CAPACITY):
        self.capacity = capacity
        self.items: list[Item] = []

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    @property
    def is_full(self) -> bool:
        return len(self.items) >= self.capacity

    def add(self, item: Item) -> bool:
        """Range un objet. Renvoie False si le sac est plein."""
        if self.is_full:
            return False
        self.items.append(item)
        return True

    def find(self, item_type: str) -> Item | None:
        for item in self.items:
            if item.type == item_type:
                return item
        return None

    def find_key(self, key_id: str | None) -> Item | None:
        """
        Cherche une clé compatible avec une serrure.

        Une clé sans `key_id` est considérée comme passe-partout : pratique
        pendant la jam pour tester une porte sans configurer les identifiants.
        """
        for item in self.items:
            if item.type != C.ITEM_KEY:
                continue
            if key_id is None or item.key_id is None or item.key_id == key_id:
                return item
        return None

    def remove(self, item: Item) -> None:
        if item in self.items:
            self.items.remove(item)

    def clear(self) -> list[Item]:
        """Vide le sac et renvoie son contenu (utilisé au moment de la mort)."""
        dropped = self.items
        self.items = []
        return dropped
