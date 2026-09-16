# Dossier `src/entities/`

Contient les acteurs dynamiques du jeu.

- **corpse.py** : Très important. Gère les cadavres laissés après une mort par
  fiole ou piège. Le sprite du cadavre est la DERNIÈRE image de l'animation de
  mort du héros : c'est donc bien son corps qui reste sur place, ce qui rend
  cohérent le fait qu'il arrête les fléchettes et maintienne une plaque de
  pression. Il émet une lueur, et ne contient aucun objet : les affaires du
  joueur tombent au sol autour de lui (`Level.drop_items`).
- **items.py** : Les objets ramassables (fiole de poison pour se sacrifier,
  clés, torches).
- **monster.py** : La créature qui traque le joueur, un fantôme invisible tant
  qu'il n'est pas à quelques pas.
- **npc.py** : Les personnages non-joueurs mentionnés dans le pitch. Squelette
  prêt à l'emploi, aucun PNJ n'est encore posé dans les cartes.
- **player.py** : Le joueur, son animation dans quatre directions, son
  inventaire limité et ses actions.
- **textures.py** : Découpage des bandes d'animation du pack graphique et
  définition des boîtes de collision. À lire avant de changer un sprite : la
  boîte de collision d'un personnage doit rester plus petite qu'une tuile, sinon
  les couloirs d'une seule tuile deviennent infranchissables.
