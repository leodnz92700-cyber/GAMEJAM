# Dossier `src/ui/`

Contient tous les éléments d'interface utilisateur (HUD, boutons, fenêtres de
dialogue) qui seront affichés par les vues (`src/views/`).

- **dialog_box.py** : affichage du lore et des textes PNJ.
- **hud.py** : bandeau du bas (étage, inventaire, morts, contraintes du mode).
  Règle à respecter : le HUD n'affiche JAMAIS le temps restant avant l'arrivée
  de la créature.
- **menu_components.py** : boutons et listes navigables pour les menus.
- **text_cache.py** : `draw_text_cached`, à utiliser partout à la place de
  `arcade.draw_text` (qu'Arcade signale comme très lent). Même signature.
