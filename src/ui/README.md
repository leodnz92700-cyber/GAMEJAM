# Dossier `src/ui/`

Contient tous les éléments d'interface utilisateur (HUD, boutons, fenêtres de
dialogue) qui seront affichés par les vues (`src/views/`).

- **dialog_box.py** : affichage du lore et des textes PNJ.
- **hud.py** : l'ATH, dessiné intégralement en transparence par-dessus le jeu —
  il n'y a aucun bandeau. Zone courante en haut à gauche, temps et morts en haut
  à droite, inventaire et rappels de touches en bas à droite, invite
  d'interaction en bas au centre. Deux règles à respecter : l'ATH n'affiche
  JAMAIS le temps restant avant l'arrivée de la créature, et l'invite « E » ne
  s'affiche que lorsqu'une interaction est réellement à portée.
- **fonts.py** : charge la police pixel du jeu (*Pixelify Sans*, `assets/fonts/`).
  Choisie parce qu'elle a de vraies bas-de-casse ET un vrai gras, ce que la
  plupart des polices pixel n'ont pas. Police système en secours si le
  fichier manque.
- **key_icons.py** : touches de clavier dessinées (lettre ou flèche) pour les
  rappels de commandes. Tracées à la main, elles ne dépendent d'aucun asset.
- **logo.py** : charge `assets/ui/logo.png`, rogne sa marge transparente et le
  dessine sans le déformer. Si le fichier manque, le titre s'affiche en texte :
  l'écran d'accueil reste utilisable sur un dépôt fraîchement cloné.
- **menu_components.py** : les briques des écrans hors-jeu — panneau
  (`draw_panel`), tableau à colonnes alignées (`draw_table`), tableau
  « libellé … valeur » (`draw_stat_rows`), boutons et listes navigables,
  titres. **Les colonnes sont posées à l'abscisse**, jamais alignées avec des
  espaces : la police n'est pas à chasse fixe.
- **screamer.py** : le jumpscare joué quand la créature dévore le joueur. Sans
  lui, la mort la plus punitive du jeu passait inaperçue.
- **text_cache.py** : `draw_text_cached`, à utiliser partout à la place de
  `arcade.draw_text` (qu'Arcade signale comme très lent). Même signature, et
  c'est lui qui applique la police pixel à tout le jeu : un `arcade.Text`
  écrit à la main sortirait dans la police du système.
