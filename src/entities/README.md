# Dossier `src/entities/`

Contient les acteurs dynamiques du jeu.

- **corpse.py** : Très important. Gère les cadavres laissés après une mort par fiole ou piège. Les cadavres gardent l'inventaire, ont une présence physique (pour les plaques de pression), et émettent de la lumière.
- **items.py** : Les objets ramassables (fioles de poison pour se sacrifier, clés, objets de quête).
- **monster.py** : La créature invisible qui traque le joueur et mange les cadavres.
- **npc.py** : Les personnages non-joueurs mentionnés dans le pitch pour interagir et résoudre certains obstacles.
- **player.py** : Le joueur, avec son inventaire limité et ses actions (mourir volontairement, marcher, interagir).
