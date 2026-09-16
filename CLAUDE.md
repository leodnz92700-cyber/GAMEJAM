# CLAUDE.md — contexte du projet pour une session Claude

Ce fichier est lu automatiquement au démarrage de chaque session Claude Code
dans ce dépôt. Il existe pour qu'un membre de l'équipe puisse ouvrir une session
sur **n'importe quel sujet du projet** sans avoir à réexpliquer quoi que ce soit.

Le `README.md` s'adresse aux humains (installation, structure, répartition des
fichiers par personne). Ce fichier-ci s'adresse à Claude : conventions,
invariants, pièges, commandes de vérification. **Les deux doivent rester
cohérents** : si une modification rend une phrase du README fausse, corrigez-la.

---

## 1. Le jeu en une page

**Labyrinth of Shadow** — jeu de survie 2D vue de dessus, Python + Arcade,
réalisé en 3 jours de game jam sur le thème **« MOURIR POUR MIEUX AVANCER »**.

Le joueur se réveille dans une tour labyrinthique plongée dans le noir absolu.
Il ne voit qu'un petit halo autour de lui. Pour avancer, il doit **mourir
volontairement** : boire une fiole ou se jeter dans un piège. Chaque mort choisie
laisse **son cadavre** sur place, et ce cadavre sert les vies suivantes :

- il **émet une lueur** froide et pulsante : c'est un repère dans le noir ;
- il **maintient une plaque de pression** enfoncée, donc une porte ouverte ;
- il **bloque les flèches** du squelette archer ;
- on peut **marcher dessus** : un cadavre ne condamne jamais un couloir.

En face, une **créature invisible** est lâchée après un délai fixe. Se faire
dévorer ne laisse **rien** : pas de cadavre, tous les objets perdus. C'est toute
la tension du jeu : **choisir sa mort est une ressource, la subir est une
punition.**

Le jeu ne contient **qu'un seul niveau** : atteindre sa sortie gagne la partie.
Il n'y a ni ascension d'etages, ni ecran de selection — c'est une decision de
l'equipe, ne la rouvrez pas sans qu'on vous le demande.

Une partie doit tenir en **moins de 5 minutes**.

### Les trois règles de game design à ne jamais casser

1. **Aucun compte à rebours affiché** pour la créature. Le joueur ne dispose que
   du son (grondement lointain → griffes → pas qui courent → battements de
   coeur) et du **vacillement des torches**. Le seul chronomètre autorisé à
   l'écran est celui du mode « Contre-la-montre », qui est une règle de mode et
   non la créature.
2. **Mourir doit toujours rester possible.** La fiole est unique mais réapparaît
   systématiquement près du départ après chaque mort. Sans elle, le joueur est
   bloqué.
3. **Le niveau doit toujours rester finissable.** Les objets uniques (fiole,
   clés) reviennent à leur emplacement de level design s'ils disparaissent du
   monde ; un piège à pointes ne doit jamais être mortel en permanence.

---

## 2. Environnement et commandes

Python **3.12.9** (via pyenv, `.python-version`), venv local **`.venv`**,
Arcade **3.3.3**.

> **Le venv n'est pas activé par défaut dans un shell d'agent.** Préfixez
> systématiquement par `.venv/bin/python`, sinon vous obtiendrez
> `ModuleNotFoundError: No module named 'arcade'`. C'est l'erreur la plus
> fréquente de ce dépôt.

```bash
.venv/bin/python main.py                                       # jouer
.venv/bin/python main.py --map level_test.tmx --skip-menu      # debug rapide
.venv/bin/python main.py --mode timed --skip-menu              # contre-la-montre, sans menu
```

### Vérifications — à lancer après toute modification

```bash
.venv/bin/python -m compileall -q src tools main.py   # syntaxe
.venv/bin/python tools/check_levels.py                # coherence logique des cartes
.venv/bin/python tools/walk_test.py                   # praticabilite reelle (collisions)
.venv/bin/python tools/smoke_test.py /tmp/shots       # partie complete scriptee + captures
```

Ces trois outils ont été vérifiés : ils **échouent réellement** quand la
mécanique correspondante est cassée. Ce ne sont pas des tests décoratifs.

| Outil | Ce qu'il attrape |
|-------|------------------|
| `check_levels.py` | sortie inatteignable, clé enfermée derrière sa propre porte, fiole absente ou en double, torches insuffisantes, parcours trop long |
| `walk_test.py` | couloir trop étroit pour la boîte de collision, passage bouché, **piège sans fenêtre sûre assez longue pour être traversé** |
| `smoke_test.py` | régression de mécanique : pièges visibles, animation de mort, cadavre + objets tombés au sol, réapparition de la fiole, **mort par flèche puis cadavre-bouclier (l'archer tire toujours, aucune flèche ne passe le corps)**, lâcher de la créature, jumpscare, clé restituée après dévoration, changement de zone |

`smoke_test.py` écrit des captures PNG : c'est aussi le moyen de **voir** le jeu
sans y jouer. Les captures sont converties en RGB, sans quoi l'alpha < 255 les
fait paraître grises.

**Attention :** `tools/gen_placeholder_maps.py` **écrase** les `.tmx`. Ne le
relancez jamais sans demander, une carte dessinée à la main serait perdue.

---

## 3. Architecture

Le découpage vient de l'équipe et **doit être respecté** : chacun travaille dans
ses fichiers, c'est ce qui évite les conflits Git. Le `README.md` donne le nom du
responsable de chaque fichier ; ne déplacez pas de logique d'un module à l'autre
sans raison forte.

```
main.py              cree la fenetre, choisit la premiere vue. Aucune logique de jeu.
src/constants.py     TOUT l'equilibrage. Aucune valeur magique ailleurs.
src/views/           un ecran = une View arcade. game_view.py = la boucle de jeu.
src/mechanics/       la logique (niveau, lumiere, mort, creature, score, interactions)
src/entities/        ce qui bouge ou se ramasse (joueur, creature, cadavre, objets)
src/environment/     ce qui est pose dans le decor (portes, plaques, torches, pieges)
src/ui/              ATH, boites de dialogue, menus, jumpscare
tools/               scripts hors-jeu. JAMAIS importes par le jeu.
map/dungeonsAndPixels/  pack source. JAMAIS lu par le jeu.
assets/              ce que le jeu lit reellement.
```

**`src/views/game_view.py` est l'orchestrateur** : il ne contient pas de règles,
il appelle les managers dans le bon ordre. Une nouvelle mécanique se branche
dans son manager, puis s'appelle depuis `on_update` / `on_draw`.

**Toute valeur d'équilibrage va dans `src/constants.py`**, avec un commentaire
qui dit ce qu'elle change pour le joueur. C'est le fichier que les coéquipiers
ouvrent pour régler le jeu sans lire le code.

Chaque paquet de `src/` a un `README.md` qui détaille son rôle — mettez-le à
jour quand vous ajoutez un fichier.

---

## 4. Ce qui est déjà en place

- Déplacement animé 4 directions, collisions murs, `PhysicsEngineSimple`.
- **Caméra fixe par zone** : 1 écran = 1 zone de 40 x 22 tuiles, la caméra
  **saute** à la zone voisine (petit fondu), elle ne suit jamais le joueur.
  Le niveau = 4 zones (2x2), soit une carte de 80 x 44 tuiles.
- **Obscurité par shader** : voile noir percé + passe de lueur additive.
- Mort volontaire (fiole `R`) avec animation d'effondrement, mort par piège,
  mort par la créature avec jumpscare.
- Cadavres persistants (lueur, plaques, blocage des flèches, franchissables).
- Objets tombés au sol autour du corps, aucune interaction avec le cadavre.
- Pièges à pointes cycliques **visibles**, **squelette archer** (tireur
  increvable, une flèche toutes les 0,3 s en travers d'une grande salle, arrêtée
  par les cadavres), portes à clé et à plaque, torches plantables, sortie vers
  l'étage suivant.
- Créature : délai fixe, paliers sonores de tension, traque par BFS.
- Écrans d'accueil, de victoire et de défaite, classement local, 3 modes de
  jeu (Exploration / Sursis 8 morts / Contre-la-montre 5 min).
- ATH entièrement transparent (voir §6).

### Pas encore fait (pistes pour un coéquipier)

- Les PNJ existent en tant que classe, **aucun n'est posé dans les cartes**.
- La créature ne dévore pas les cadavres (le pitch l'évoque) → `monster_manager`.
- Pas de mémoire des zones explorées → `lighting_engine`.
- Les sons sont des placeholders de synthèse → remplacer les fichiers dans
  `assets/audio/` **sous les mêmes noms**, sans relancer le générateur.
- Pas d'animation d'attaque de la créature (le pack en fournit pourtant une).

---

## 5. Pièges techniques — déjà rencontrés, ne pas y retomber

### Arcade 3.3.3

- **`arcade.experimental.lights.LightLayer` n'existe pas** dans cette version.
  L'éclairage est un **shader GLSL maison** dans `src/mechanics/lighting_engine.py`.
  Ne proposez pas `LightLayer`, ne l'importez pas.
- Le voile doit être **noir pur**, avec la lueur dans une **passe additive
  séparée**. Un voile teinté éclaircit le bord des halos plus que leur centre :
  le résultat est un anneau visible, très laid.
- Utilisez `arcade.gl.geometry.quad_2d_fs()` / `quad_2d(size, pos)`, qui
  travaillent en NDC. **Ne touchez pas à `ctx.viewport`** : sur écran retina le
  facteur d'échelle casse tout.
- **`Sprite.hit_box` n'a pas de setter.** La seule façon publique de définir une
  boîte de collision est `arcade.Texture(image, hit_box_points=[...])` — c'est ce
  que fait `src/entities/textures.py`.
- **`arcade.draw_text` est très lent** (Arcade émet un `PerformanceWarning`).
  Utilisez `src/ui/text_cache.py` : `draw_text_cached` réutilise des objets
  `arcade.Text`, et `draw_text_shadowed` ajoute l'ombre portée d'1 px
  **obligatoire** pour tout texte posé sur le jeu (sinon illisible dès qu'une
  torche éclaire le fond). C'est aussi `text_cache` qui applique la **police
  pixel** du jeu à tout le monde : n'écrivez jamais un `arcade.Text` à la main,
  il sortirait dans la police du système et jurerait avec le reste.
- **`pixelated=True` sur chaque `draw`** : le pack est du pixel art, le
  filtrage linéaire le rend flou.
- Frame-rate independence : `change_x = vitesse * delta_time`, jamais une
  constante par frame.
- **Ordre de dessin : le décor plat d'abord, puis une passe triée en profondeur**
  (`game_view._draw_world`). Tout ce qui dépasse de sa tuile — portes, archers,
  PNJ, créature, héros — est dessiné du `center_y` le plus grand au plus petit,
  donc du plus lointain au plus proche. Sans ce tri, un personnage debout au NORD
  d'une porte était dessiné par-dessus elle, alors qu'il se trouve derrière.
  N'ajoutez pas un sprite haut dans une simple `SpriteList.draw()` : mettez-le
  dans la liste `tall`.

### Sprites et boîtes de collision

Bandes d'images du pack (`assets/sprites/`), découpées par `load_strip` :

| Bande | Format |
|-------|--------|
| héros repos / course | 4 et 6 images de **32 x 48** |
| **héros mort** | **6 images de 48 x 48** — format différent des autres ! |
| créature | 4 images de 32 x 48 |
| squelette archer repos / tir | 4 et 6 images de 32 x 48 |
| torche plantée | 3 images de 32 x 32 |
| pointes | 7 images de 32 x 32 |
| plaque | 3 images de 32 x 32 |

> La bande de mort a un **format différent**. Une erreur sur ce point produit un
> scintillement à l'écran (les images sont découpées de travers). Vérifiez dans
> le pack source avant de supposer un format.

Deux fonctions de `textures.py` à comprendre avant de toucher aux sprites :

- **`centered_box(w, h)`** pour les personnages : la boîte est un petit rectangle
  **centré**, bien plus petite que l'image. Le héros fait 32 x 48 alors que les
  couloirs les plus étroits font 32 px : avec une boîte à la taille de l'image,
  il ne passe pas. Une boîte décalée vers les pieds avait exactement cet effet.
- **`lift_art(texture, n)`** ajoute des lignes transparentes **en bas** de
  l'image, ce qui fait dessiner le dessin au-dessus de son point de collision.
  C'est ce qui empêche les pieds du personnage de s'enfoncer dans le mur du bas.
  **La valeur n'est pas libre** : `(hauteur de l'image - hauteur de la boîte) / 2`,
  soit `(48 - 16) / 2 = 16` pour un personnage 32x48 — c'est `PLAYER_ART_LIFT`,
  que réutilisent le héros, le cadavre, le PNJ et l'archer. En dessous, le bas du
  dessin passe SOUS la boîte de collision : collé à un mur, le personnage a les
  pieds dessinés par-dessus la tuile d'en bas et semble marcher sur le décor.

**Après tout changement de sprite de personnage, relancez `walk_test.py`** :
c'est lui qui détecte qu'un héros est devenu trop large pour un couloir.

### Tiled

- `tile_map.object_lists[nom_du_calque]` → des `arcade.types.TiledObject`
  (`shape`, `properties`, `name`, `type`). **La classe Tiled est dans `type`.**
- `shape` est **déjà** converti en coordonnées Arcade (Y inversé) : ne le
  refaites pas.
- `src/mechanics/map_loader.py` traduit le `.tmx` en **données neutres** ; le
  reste du jeu ne connaît pas Tiled. Un nouveau type d'objet se déclare là.
- La convention complète (calques, classes, propriétés, règles de contenu) est
  dans **`assets/maps/README.md`** — c'est la référence pour tout ce qui touche
  au level design.

### Soft-locks déjà corrigés (ne pas les réintroduire)

- **Piège à pointes mortel en permanence** dans un couloir d'une tuile = niveau
  infranchissable. D'où le cycle (`SPIKE_SAFE_DURATION` / `SPIKE_STRIKE_DURATION`)
  et l'assertion de `walk_test.py` : chaque piège doit offrir une fenêtre sûre
  d'au moins 3,5 fois le temps de traversée d'une tuile.
- **Clé détruite par la créature** = étage infinissable. D'où
  `RESPAWNING_ITEM_TYPES` et `Level.restore_unique_items()` : les objets uniques
  reviennent à leur emplacement d'origine **seulement s'ils ont disparu du
  monde**. Une clé posée près d'un cadavre est toujours dans le niveau : elle
  n'est pas remise en place, et le joueur doit aller la rechercher. Tout nouvel
  objet de quête unique doit être ajouté à cette liste.
- Tous les pièges pulsent **en phase**, pilotés par `Level.clock` : sinon le
  joueur ne peut pas apprendre le rythme.
- **Flèche sans portée** = mort incompréhensible. Un tir qui sort de la salle
  par une ouverture traversait tout l'étage et tuait le joueur trois salles plus
  loin, sans qu'il ait jamais vu l'archer. D'où `ARROW_RANGE` (9 tuiles) : le
  danger reste dans la pièce du tireur.

---

## 6. L'interface (refaite sur demande du joueur)

**Aucun bandeau.** Tout est dessiné **en transparence par-dessus le jeu**, qui
occupe la fenêtre entière. `HUD_HEIGHT` **n'existe plus** — si vous le voyez
quelque part, c'est un reste à supprimer.

La fenêtre fait **1280 x 704**, soit exactement une zone de 40 x 22 tuiles.
Ces dimensions sont **calculées** dans `constants.py` à partir de `ZONE_COLS`,
`ZONE_ROWS` et `TILE_SIZE`, et `tools/gen_placeholder_maps.py` les **importe** :
le jeu et les cartes ne peuvent plus diverger. Si vous changez la taille d'une
zone, il faut régénérer ou redimensionner les cartes.

Disposition (`src/ui/hud.py`) :

| Coin | Contenu |
|------|---------|
| haut gauche | étage et zone |
| haut droite | temps de la partie et nombre de morts |
| haut centre | murmures : ce que le personnage entend de la créature |
| bas droite | inventaire (titre « INVENTAIRE » **au-dessus** des cases), surmonté des rappels `F` / `R` |
| bas centre | invite d'interaction et messages temporaires |

- Les touches sont **dessinées à la main** (`src/ui/key_icons.py`) : rectangle +
  lettre, ou rectangle + triangle pour les flèches. Elles restent nettes à toute
  taille et ne dépendent d'aucun asset.
- Une touche dont l'action est indisponible est **grisée**, pas masquée : le
  joueur apprend qu'elle existe avant d'avoir l'objet.
- **Le déplacement n'est pas rappelé.** ZQSD est un réflexe acquis, l'afficher
  n'apprend rien. `draw_arrow_cluster` reste disponible dans `key_icons.py` pour
  un futur écran de commandes.
- Pas de nom d'objet sous les cases d'inventaire : le sprite suffit, et le texte
  débordait sur l'objet.

### Les écrans hors-jeu (accueil, victoire, défaite)

Ils partagent la **police pixel** du jeu (*Pixelify Sans*, `assets/fonts/`,
licence OFL, chargée par `src/ui/fonts.py`). Elle a été choisie contre les
classiques du genre pour deux raisons qu'il faut connaître avant d'en changer :
**elle a de vraies bas-de-casse** (Silkscreen et Press Start 2P sont en
capitales seulement, le paragraphe de lore y devenait un mur de majuscules) et
**elle a un vrai gras**, sur lequel repose toute la hiérarchie de l'interface.
Elle est plus large que la police du système à taille égale : après un
changement de taille, **relancez l'écran et regardez**, les retours à la ligne
et les colonnes bougent.

Ils partagent aussi une **palette relevée sur le logo** : l'or de son liseré
(`COLOR_ACCENT`, échantillonné à (255, 244, 149)) sur un noir légèrement rougi,
des gris qui tirent sur le brun, aucun angle arrondi et aucun dégradé — le jeu
est en pixel art, l'interface aussi. L'or ne sert qu'à ce qui est **actif ou
important** ; le rouge, qu'au danger — c'est celui des lettres du logo, remonté
jusqu'à être lisible en texte.

**Les lueurs du JEU ne suivent pas cette palette.** Le cadavre reste d'un cyan
froid (`COLOR_CORPSE_GLOW`) alors que l'interface est chaude, et c'est
volontaire : dans le noir, c'est à sa couleur que le joueur distingue de loin un
cadavre d'une torche plantée (`COLOR_TORCH_GLOW`, orange). Deux lueurs dorées
seraient indiscernables.

Trois règles de mise en page, et elles expliquent tout le code de
`src/ui/menu_components.py` :

0. **L'écran d'accueil ne rappelle aucune touche.** Naviguer aux flèches et
   valider à Entrée est un réflexe acquis : l'écrire n'apprend rien et encombre
   le bas de la page. Seul le choix du mode a un repère visuel (trois traits),
   parce que rien d'autre ne dit qu'il y a trois modes. Les écrans de fin, eux,
   gardent leur ligne « Entrée : retour à l'écran d'accueil ».
1. **Rien n'est posé « à l'oeil ».** Chaque écran déclare sa grille en
   constantes en haut du fichier (`PANELS_TOP`, `LEFT_WIDTH`, `STATS_BOTTOM`…)
   et tout s'en déduit. Deux panneaux côte à côte commencent et finissent aux
   mêmes ordonnées, sinon l'écran part en morceaux.
2. **Une colonne se place à son abscisse, jamais avec des espaces.** La police
   du système n'est pas à chasse fixe : `"VICTOIRE   03:34"` donne des colonnes
   en escalier. `draw_table` reçoit des `Column(titre, largeur, alignement)` et
   aligne chaque cellule lui-même ; les nombres sont **alignés à droite**.
3. **Un panneau ne se dimensionne pas au contenu, c'est le contenu qui doit y
   entrer.** Le lore de l'accueil est calibré sur six lignes : un paragraphe de
   plus déborde par le bas, silencieusement. Vérifiez à l'écran.

Le **logo** (`assets/ui/logo.png`, chargé par `src/ui/logo.py`) est livré sur un
**fond noir opaque**, pas sur du transparent. Posé tel quel, il collerait un
rectangle noir franc sur l'écran ; `logo.py` lui fabrique donc un canal alpha à
partir de sa luminosité — le noir devient transparent, la lueur s'éteint
d'elle-même sur ses bords — puis rogne au plus près du dessin, ce qui permet de
l'aligner. **La version actuelle du logo est, elle, correctement détourée** : le
code détecte son canal alpha et le respecte, il ne se déclenche que sur une
image opaque. Dans les deux cas le rognage a lieu, et c'est lui qui compte pour
la mise en page : le logo est un bandeau très étalé (1160 x 181 une fois rogné),
c'est donc sa HAUTEUR qui limite son échelle — élargir sa boîte ne le grandit
plus. **Si le fichier manque, le
titre s'affiche en texte** : un dépôt tout juste cloné ne doit pas planter sur
son écran d'accueil.

Les deux écrans de fin sont **le même écran** (`src/views/end_screen.py`) : seuls
le titre, sa couleur et la phrase de verdict changent. Les modifier séparément,
c'est garantir qu'ils finiront désalignés l'un par rapport à l'autre.

### `InteractionTarget` — l'invite ne peut pas mentir

`src/mechanics/interaction_manager.find_target(player, level)` répond à « que
puis-je faire ici ? » et est la **source de vérité unique**, partagée par
l'affichage et par l'exécution :

- l'ATH l'appelle chaque frame pour n'afficher `[E]` **que** si quelque chose est
  à portée ;
- `interact()` l'appelle aussi, et exécute exactement ce que l'invite annonçait.

Quand l'action est à portée mais impossible, le texte s'affiche **sans la touche
et en gris** (`Inventaire plein`, `Verrouillee : il te faut la cle`) : le joueur
sait pourquoi ça ne marche pas, sans croire que `E` fera quelque chose.

**Toute nouvelle interaction doit passer par `find_target`**, jamais par un test
ad hoc dans `game_view` — sinon l'invite et le comportement divergeront.

Ordre de priorité, important pour la lisibilité dans le noir :
objet au sol → porte fermée → PNJ.

Commandes : `ZQSD`/flèches déplacer · `E` interagir · `F` planter une torche ·
`R` boire la fiole · `Échap` menu.

---

## 7. Décisions de design déjà tranchées par l'équipe

Ces points ont fait l'objet d'une demande explicite. **Ne les rouvrez pas sans
que le joueur le demande.**

- Les **pièges et projectiles sont visibles** dès le départ. Ils ne sont plus
  cachés jusqu'à leur découverte : le joueur voit le danger et doit l'esquiver.
- **Les objets au sol n'émettent jamais de lumière.** Seules trois sources
  éclairent : le halo du joueur, les **torches plantées** et les **cadavres**
  (plus la sortie). Un objet posé reste invisible tant qu'on n'apporte pas de
  lumière — c'est ce qui donne sa valeur à une torche plantée.
- **Le cadavre est le vrai corps**, la dernière image de l'animation de mort, pas
  des ossements : c'est plus logique quand une flèche vient s'y planter, et la
  transition animation → cadavre est invisible.
- **Aucune interaction avec le cadavre.** Les affaires tombent au sol **autour**
  du corps et se ramassent comme n'importe quel objet. Elles ne sont jamais
  posées pile sur le corps, où elles seraient cachées par le sprite.
- **Une seule fiole par étage**, près du départ, qui réapparaît après **chaque**
  mort — volontaire, par piège ou par la créature.
- **Beaucoup de torches** (une vingtaine) le long du chemin principal, assez pour
  l'éclairer entièrement. Une torche plantée **ne se ramasse plus**. Une torche
  en poche lors d'une mort choisie se retrouve près du cadavre ; dévoré par la
  créature, on la perd.
- **Couloirs de 1 ou 2 tuiles**, quelques salles plus larges pour y poser des
  objets. Aux frontières de zone, **un mur partout où l'on ne peut pas passer** :
  le joueur ne doit jamais avancer vers un bord en espérant qu'il s'ouvre.
- **Les plaques de pression sont posées juste avant leur porte**, pour que le
  joueur voie la porte s'ouvrir et se refermer, et comprenne qu'il doit mourir
  dessus.
- **Le tir vient d'un squelette archer, pas d'un mur.** On le voit, on ne peut
  ni le tuer ni le traverser — il est **solide** (`_rebuild_physics`), sans quoi
  il suffisait de marcher dans son dos pour esquiver ses flèches sans payer le
  passage —, et il est posé dans une **grande salle** pour que la
  flèche traverse plusieurs tuiles avant de se planter. Sa cadence est
  volontairement infernale (`ARCHER_DEFAULT_INTERVAL = 0.30`) : une traversée à
  l'aveugle est mortelle une fois sur deux, aller-retour compris. **Il ne cesse
  jamais de tirer, même après avoir tué le joueur** — c'est le cadavre laissé en
  travers de la ligne qui encaisse les flèches, et c'est la vraie solution du
  passage, pas un contournement. Ne baissez pas la cadence « pour être gentil » :
  c'est l'endroit du jeu qui enseigne le pitch.
- **Un seul niveau, une seule sortie.** Le deuxième étage et l'écran de
  sélection d'étage ont été supprimés : le numéro d'étage n'apparaît plus nulle
  part (ni dans l'ATH, ni dans les statistiques de fin). Si la tour reprend un
  jour plusieurs étages, tout repart de `C.LEVEL_NAME` et de `LevelManager`.
- **L'interface est calée sur le logo**, pas l'inverse : police pixel, or et
  rouge sombre sur noir, panneaux à bords nets, équerres dans les coins. Si le
  logo change de couleur, c'est `constants.py` qu'on rééchantillonne — pas le
  logo qu'on retouche.
- **Aucun rappel de touches sur l'écran d'accueil.** Demandé explicitement : le
  joueur sait déjà naviguer un menu.
- **Le jumpscare** de la créature remplace la mort brutale et instantanée :
  éclair blanc, la gueule qui tremble à l'écran, fondu au noir.

---

## 8. Conventions de code

- **Tout en français** : commentaires, docstrings, textes du jeu, messages de
  commit. Les identifiants restent en anglais.
- Chaque fichier commence par un en-tête `Fichier / Auteur / Description`. La
  description explique **pourquoi** le module existe et quelles règles il porte,
  pas ce que le code fait ligne à ligne.
- Les textes affichés au joueur sont **sans accents** (`Verrouillee`, `Cle`) : la
  police système utilisée les rend mal. Les commentaires, eux, sont accentués.
- Le code est lu par cinq personnes de niveaux différents : privilégiez le
  direct et le commenté au malin.
- Ne créez pas de fichier « au cas où ». Ne laissez pas de code mort sans un
  commentaire disant à quoi il est destiné.

## 9. Travailler avec l'équipe

Six personnes, branche `main`, travail en parallèle. Le `README.md` attribue
chaque fichier à quelqu'un — **restez dans le périmètre demandé** : une
modification opportuniste dans le fichier d'un coéquipier devient un conflit Git
au pire moment d'une jam.

Ne committez et ne poussez **que** si on vous le demande.

Quand vous terminez une modification qui change le comportement du jeu, mettez à
jour la documentation concernée dans le même mouvement : `README.md` pour les
fonctionnalités et les contrôles, `assets/maps/README.md` pour le level design,
le `README.md` du paquet pour un nouveau fichier, et **ce fichier-ci** pour une
décision de design ou un piège technique qui doit survivre à la session.
