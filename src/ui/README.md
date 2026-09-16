# Dossier `src/ui/`

Contient tous les éléments d'interface utilisateur (HUD, boutons, fenêtres de
dialogue) qui seront affichés par les vues (`src/views/`).

- **dialog_box.py** : affichage du lore et des textes PNJ.
- **hud.py** : l'ATH, dessiné intégralement en transparence par-dessus le jeu —
  il n'y a aucun bandeau. Étage et zone en haut à gauche, temps et morts en haut
  à droite, inventaire et rappels de touches en bas à droite, invite
  d'interaction en bas au centre. Deux règles à respecter : l'ATH n'affiche
  JAMAIS le temps restant avant l'arrivée de la créature, et l'invite « E » ne
  s'affiche que lorsqu'une interaction est réellement à portée.
- **key_icons.py** : touches de clavier dessinées (lettre ou flèche) pour les
  rappels de commandes. Tracées à la main, elles ne dépendent d'aucun asset.
- **menu_components.py** : boutons et listes navigables pour les menus.
- **screamer.py** : le jumpscare joué quand la créature dévore le joueur. Sans
  lui, la mort la plus punitive du jeu passait inaperçue.
- **text_cache.py** : `draw_text_cached`, à utiliser partout à la place de
  `arcade.draw_text` (qu'Arcade signale comme très lent). Même signature.
