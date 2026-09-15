# Dossier `src/environment/`

Contient les éléments statiques ou interactifs du labyrinthe.

- **door.py** : Portes nécessitant des clés ou des plaques de pression.
- **pressure_plate.py** : Plaques de pression. Le joueur peut mourir dessus pour laisser son cadavre maintenir la porte ouverte.
- **torch.py** : Les torches que le joueur peut planter pour éclairer durablement une zone.
- **trap.py** : Les pièges. Un danger à éviter mais aussi une opportunité
  stratégique pour laisser son corps au bon endroit. Le piège à pointes est
  invisible jusqu'à sa première victime, puis bat en continu : c'est ce qui le
  rend franchissable, puisqu'il barre toute la largeur du couloir.
