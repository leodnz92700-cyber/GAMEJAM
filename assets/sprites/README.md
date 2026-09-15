# assets/sprites/

Toutes les images utilisées par les entités et le décor.

- Joueur : feuilles de sprites pour les déplacements (idle, marche
  dans chaque direction), éventuellement une pose "mort".
- Tuiles de décor : murs, sol, variantes pour casser la répétition
  visuelle sur de longs couloirs.
- Cadavre : sprite statique + éventuellement un halo de lueur séparé
  si vous préférez le gérer comme une image plutôt qu'un effet de
  lumière calculé.
- Torche : deux visuels distincts, portée (icône inventaire ou vue à
  la main) et plantée (sur pied, avec flamme animée si possible).
- Clés et portes : une variante par état (porte fermée / ouverte,
  éventuellement une variante "porte spéciale" pour celle liée au
  timer caché, visuellement différenciable).
- Ennemi invisible : la silhouette elle-même (semi-transparente ou en
  contour), en plusieurs frames si vous l'animez.

Convention : préfixer par le nom de l'entité plutôt que par un numéro
générique (`torch_placed.png`, `door_special_open.png`), pour que le
code qui charge les textures reste lisible.
