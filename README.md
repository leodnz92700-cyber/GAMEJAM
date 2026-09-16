# Configuration de l'environnement

Choisis la section correspondant à ton système d'exploitation.

---

# Windows

Toutes les étapes se font dans un terminal **PowerShell**.

## 1. Cloner le repo

```powershell
git clone https://github.com/leodnz92700-cyber/GAMEJAM.git
cd GAMEJAM
```

---

## 2. Installer pyenv-win

Lance cette commande pour télécharger et exécuter l'installateur :

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
Remove-Item ./install-pyenv-win.ps1
```

**Important :** Ferme complètement PowerShell et rouvre-le dans le dossier `GAMEJAM` pour prendre en compte les variables d'environnement.

Vérifie que pyenv répond :

```powershell
pyenv --version
```

---

## 3. Installer Python 3.12.9 via pyenv

Le repo contient déjà le fichier `.python-version` qui demande la `3.12.9`. Lance simplement :

```powershell
pyenv install 3.12.9
```

Vérifie que la bonne version est active :

```powershell
python --version
```

Sortie attendue : `Python 3.12.9`

---

## 4. Créer et activer l'environnement virtuel (.venv)

Autorise d'abord l'exécution des scripts locaux (à faire une seule fois) :

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Crée le venv local et active-le :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Le préfixe `(.venv)` doit apparaître au début de la ligne de commande.

---

## 5. Installer les bibliothèques du projet

Avec le `(.venv)` activé :

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 6. Lier l'interpréteur dans PyCharm

1. Ouvre le dossier du projet dans PyCharm.
2. Ouvre les paramètres : `Ctrl + Alt + S` > Project: GAMEJAM > Python Interpreter.
3. Clique sur **Add Interpreter** > **Add Local Interpreter...**.
4. Sélectionne **Existing** et va chercher : `chemin\vers\GAMEJAM\.venv\Scripts\python.exe`
5. Valide avec **OK**.

---

## 7. Lancer le jeu

```powershell
python main.py
```

---

# macOS

Toutes les étapes se font dans un terminal (**Terminal.app** ou **iTerm**).

## 1. Cloner le repo

```bash
git clone https://github.com/leodnz92700-cyber/GAMEJAM.git
cd GAMEJAM
```

---

## 2. Installer pyenv

Le plus simple est de passer par **Homebrew** (installe Homebrew d'abord si besoin, via [brew.sh](https://brew.sh)) :

```bash
brew update
brew install pyenv
```

Ajoute ensuite pyenv à ton shell. Si tu utilises **zsh** (par défaut sur macOS récent) :

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
```

**Important :** Ferme complètement le terminal et rouvre-le dans le dossier `GAMEJAM` pour prendre en compte les variables d'environnement.

Vérifie que pyenv répond :

```bash
pyenv --version
```

---

## 3. Installer Python 3.12.9 via pyenv

Le repo contient déjà le fichier `.python-version` qui demande la `3.12.9`. Lance simplement :

```bash
pyenv install 3.12.9
```

Vérifie que la bonne version est active :

```bash
python --version
```

Sortie attendue : `Python 3.12.9`

---

## 4. Créer et activer l'environnement virtuel (.venv)

```bash
python -m venv .venv
source .venv/bin/activate
```

Le préfixe `(.venv)` doit apparaître au début de la ligne de commande.

---

## 5. Installer les bibliothèques du projet

Avec le `(.venv)` activé :

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 6. Lier l'interpréteur dans PyCharm

1. Ouvre le dossier du projet dans PyCharm.
2. Ouvre les paramètres : `Cmd + ,` > Project: GAMEJAM > Python Interpreter.
3. Clique sur **Add Interpreter** > **Add Local Interpreter...**.
4. Sélectionne **Existing** et va chercher : `chemin/vers/GAMEJAM/.venv/bin/python`
5. Valide avec **OK**.

---

## 7. Lancer le jeu

```bash
python main.py
```

---

# Linux

Toutes les étapes se font dans un terminal (**bash**).

## 1. Cloner le repo

```bash
git clone https://github.com/leodnz92700-cyber/GAMEJAM.git
cd GAMEJAM
```

---

## 2. Installer pyenv

Installe d'abord les dépendances de build (exemple pour Debian/Ubuntu) :

```bash
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

Installe ensuite pyenv :

```bash
curl https://pyenv.run | bash
```

Ajoute pyenv à ton shell (exemple pour **bash**, remplace `~/.bashrc` par `~/.zshrc` si tu utilises zsh) :

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
```

**Important :** Ferme complètement le terminal et rouvre-le dans le dossier `GAMEJAM` pour prendre en compte les variables d'environnement.

Vérifie que pyenv répond :

```bash
pyenv --version
```

---

## 3. Installer Python 3.12.9 via pyenv

Le repo contient déjà le fichier `.python-version` qui demande la `3.12.9`. Lance simplement :

```bash
pyenv install 3.12.9
```

Vérifie que la bonne version est active :

```bash
python --version
```

Sortie attendue : `Python 3.12.9`

---

## 4. Créer et activer l'environnement virtuel (.venv)

```bash
python -m venv .venv
source .venv/bin/activate
```

Le préfixe `(.venv)` doit apparaître au début de la ligne de commande.

---

## 5. Installer les bibliothèques du projet

Avec le `(.venv)` activé :

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 6. Lier l'interpréteur dans PyCharm

1. Ouvre le dossier du projet dans PyCharm.
2. Ouvre les paramètres : `Ctrl + Alt + S` > Project: GAMEJAM > Python Interpreter.
3. Clique sur **Add Interpreter** > **Add Local Interpreter...**.
4. Sélectionne **Existing** et va chercher : `chemin/vers/GAMEJAM/.venv/bin/python`
5. Valide avec **OK**.

---

## 7. Lancer le jeu

```bash
python main.py
```


## Structure du projet

Le nom entre crochets indique qui est responsable du fichier. Chaque paquet de
`src/` contient aussi un `__init__.py` vide et un `README.md` qui détaille son
rôle.

```
GAMEJAM/
│
├── README.md                        # [Théo] Documentation, pitch, structure
├── requirements.txt                 # [Théo] Dépendances (arcade 3.3.3)
├── .python-version                  # [Théo] Python 3.12.9 via pyenv
├── .gitignore                       # [Théo] .venv, caches, scores locaux
├── main.py                          # [Melvin] Point d'entrée + options de debug (--map, --skip-menu)
│
├── map/                             # NOUVEAU
│   └── dungeonsAndPixels/           # [Tom] Pack pixel art source 32x32. JAMAIS lu par le jeu.
│
├── tools/                           # NOUVEAU — scripts hors-jeu, jamais importés par le jeu
│   ├── import_pack_assets.py        # [Tom] Importe le pack vers assets/. Seul fichier à changer pour un autre pack.
│   ├── gen_placeholder_maps.py      # [Tom] Génère les .tmx placeholder. ÉCRASE les cartes existantes !
│   ├── check_levels.py              # [Tom] Valide une carte : sortie atteignable, clé pas enfermée, fiole unique, torches
│   ├── walk_test.py                 # [Tom] Traverse la carte avec le vrai moteur de collisions (couloirs étroits, pièges)
│   ├── gen_placeholder_assets.py    # [Léo] Génère les sons de synthèse et le dégradé de lumière
│   ├── check_audio_levels.py        # [Léo] NOUVEAU — vérifie que tous les sons sortent au même niveau
│   └── smoke_test.py                # [Melvin] Rejoue une partie complète et capture des écrans
│
├── assets/
│   ├── audio/                       # [Léo] TOUS les sons du jeu. Inventaire complet : assets/audio/README.md
│   │   ├── player/                  # [Léo] footstep, breathing, pain
│   │   ├── items/                   # [Léo] potion, key, torch : un get.wav et un use.wav chacun
│   │   ├── misc/doors/              # [Léo] open_wooden_door, door_locked
│   │   ├── misc/plate/              # [Léo] plaque enfoncée / relâchée
│   │   ├── misc/trap/               # [Léo] spiketrap_open + arrow_shot (encore un placeholder)
│   │   ├── monster/                 # [Léo] 4 alertes (une par palier), final_timer, chase, kill
│   │   ├── ambiance/                # [Léo] water_drop, squeak, et la musique du menu
│   │   └── menu/                    # [Léo] hover_button, button_click
│   ├── fonts/                       # [Erwan] Police pixel de l'interface
│   │   ├── PixelifySans.ttf         # [Erwan] Pixelify Sans, licence SIL OFL
│   │   └── OFL.txt                  # [Erwan] La licence, à conserver en cas de redistribution
│   ├── ui/                          # [Erwan] Images d'interface (pas du décor)
│   │   └── logo.png                 # [Erwan] Logo du jeu, affiché sur l'écran d'accueil
│   ├── maps/                        # [Tom]
│   │   ├── level_01.tmx             # [Tom] LE niveau du jeu (le seul)
│   │   ├── level_test.tmx           # [Tom] Carte de test, pour itérer vite
│   │   ├── Tileset_Dungeon.png/.tsx # [Tom] Tileset du pack, importé
│   │   └── README.md                # [Tom] Convention Tiled : calques, classes, propriétés, règles de contenu
│   └── sprites/                     # [Tom] Importés du pack, à plat (voir assets/sprites/README.md)
│       ├── player_idle_*.png        # [Tom] Héros au repos, 3 directions
│       ├── player_run_*.png         # [Tom] Héros en course, 3 directions
│       ├── monster_idle/move.png    # [Tom] Le fantôme
│       ├── corpse.png               # [Tom] Ossements
│       ├── item_key/vial/torch.png  # [Tom] Objets ramassables
│       ├── torch_strip.png          # [Tom] Torche plantée, animée
│       ├── trap_spike_strip.png     # [Tom] Pointes, 7 images (cycle)
│       ├── plate_strip.png          # [Tom] Plaque relevée / enfoncée
│       ├── door_front/side_*.png    # [Tom] Portes de face et de profil
│       ├── exit.png                 # [Tom] La sortie : l'atteindre gagne la partie
│       ├── archer_idle/shoot_*.png  # [Tom] Squelette archer, repos et tir
│       ├── arrow.png                # [Tom] Sa flèche
│       └── light_gradient.png       # [Léo] Dégradé radial du moteur de lumière
│
├── data/
│   └── leaderboard.json             # [Léo] Scores locaux. Créé au 1er lancement, NON versionné.
│
└── src/
    ├── constants.py                 # [NA] TOUT l'équilibrage : vitesses, timers, lumière, modes de jeu
    │
    ├── entities/
    │   ├── corpse.py                # [Inès] Cadavres : le corps du héros, lueur, présence physique
    │   ├── items.py                 # [Théo] Objets ramassables (donnée + sprite au sol)
    │   ├── monster.py               # [Inès] Le fantôme : suit son chemin, visible de très près seulement
    │   ├── npc.py                   # [NA] PNJ (classe prête, aucun posé dans les cartes)
    │   ├── player.py                # [Théo] Déplacement, animation 4 directions, inventaire
    │   └── textures.py              # [Tom] NOUVEAU — découpe les bandes du pack, définit les boîtes de collision
    │
    ├── environment/
    │   ├── door.py                  # [Melvin] Portes à clé et à plaque, de face ou de profil
    │   ├── pressure_plate.py        # [Melvin] Plaques tenues par le joueur ou par un cadavre
    │   ├── torch.py                 # [Erwan] Torches plantées, flamme animée, vacille selon la tension
    │   └── trap.py                  # [Inès] Pointes cycliques visibles + squelette archer
    │
    ├── mechanics/
    │   ├── audio_manager.py         # [Léo] NOUVEAU — point d'entrée unique du son, paliers de tension
    │   ├── death_manager.py         # [Inès] Mort choisie (cadavre + objets) vs subie (rien)
    │   ├── interaction_manager.py   # [Melvin] Touches J/K/L/M : ramasser, ouvrir, planter, jeter, boire
    │   ├── inventory_system.py      # [Théo] Sac de 2 places
    │   ├── level_manager.py         # [Melvin] Construit le niveau, simule l'environnement, gère les zones
    │   ├── lighting_engine.py       # [Léo] Shader d'obscurité + passe de lueur additive
    │   ├── map_loader.py            # [Melvin] NOUVEAU — lit le .tmx et le traduit en données neutres
    │   ├── monster_manager.py       # [Inès] Sursis, signaux d'ambiance, traque
    │   └── score_manager.py         # [Léo] Statistiques de run + classement local
    │
    ├── ui/
    │   ├── dialog_box.py            # [Erwan] Lore et répliques PNJ
    │   ├── hud.py                   # [Erwan] ATH transparent : coins de l'écran, invite d'interaction
    │   ├── key_icons.py             # [Erwan] NOUVEAU — touches de clavier dessinées (lettres, flèches)
    │   ├── screamer.py              # [Inès] NOUVEAU — jumpscare plein écran quand la créature dévore
    │   ├── fonts.py                 # [Erwan] NOUVEAU — charge la police pixel (police système en secours)
    │   ├── logo.py                  # [Erwan] NOUVEAU — charge, rogne et dessine le logo (titre en texte si absent)
    │   ├── menu_components.py       # [Erwan] Panneaux, tableaux alignés, boutons, titres
    │   └── text_cache.py            # [Erwan] NOUVEAU — draw_text_cached : cache + police pixel, à utiliser au lieu de arcade.draw_text
    │
    └── views/
        ├── end_screen.py            # [Inès] NOUVEAU — mise en page commune aux deux écrans de fin
        ├── game_over_view.py        # [Inès] Défaite + statistiques
        ├── game_view.py             # [Melvin] Boucle principale : orchestre tous les modules
        ├── main_menu.py             # [Erwan] Accueil (logo, lore, mode de jeu, tableau des scores)
        └── victory_view.py          # [Inès] Victoire + statistiques
```

---

# Labyrinth of Shadow — base technique

Première version jouable : labyrinthe dans le noir, mort volontaire, cadavres
persistants, créature qui traque. Tout est en place pour travailler à plusieurs
en parallèle.

## Lancer le jeu

```bash
python main.py
```

Options utiles pendant le développement :

```bash
python main.py --skip-menu                       # demarrer la partie sans passer par l'accueil
python main.py --map level_test.tmx --skip-menu  # charger une carte precise, sans menu
```

## Contrôles

| Touche | Action |
|--------|--------|
| `Z` `Q` `S` `D` ou les flèches | se déplacer |
| `J` | interagir : ramasser un objet, ouvrir une porte, parler — l'invite n'apparaît que si quelque chose est à portée |
| `L` | planter une torche (éclaire la zone définitivement) |
| `M` | jeter le premier objet du sac aux pieds du joueur (il reste ramassable) |
| `K` | boire la fiole : mort volontaire |
| `N` | couper / rétablir le son (utile pour montrer le jeu dans une salle bruyante) |
| `Échap` | retour au menu |

## Ce qui fonctionne déjà

- Vue de dessus, déplacement animé dans quatre directions, collisions avec les murs.
- **Caméra fixe par zone** : un écran = une zone de 40x22 tuiles, la caméra
  saute à la zone adjacente quand le joueur franchit une frontière (petit fondu).
  Le niveau fait 4 zones. Les frontières de zone sont des murs pleins, percés
  d'un seul passage : là où l'on ne peut pas changer d'écran, il y a un mur.
- **Couloirs étroits** (1 ou 2 tuiles) et quatre salles par zone, où trouver les
  objets.
- **Obscurité** : voile noir percé par un shader, halo autour du joueur, torches
  plantées (lumière permanente qui vacille), cadavres (lueur froide qui pulse).
  Seules ces trois sources éclairent : un objet posé au sol reste invisible tant
  qu'on n'apporte pas de lumière.
- **Mort volontaire** (fiole, touche `R`) : le héros s'effondre à l'écran, et le
  corps qui reste est littéralement la dernière image de cette animation. C'est
  donc bien son cadavre qui éclaire la zone, maintient les plaques de pression
  et arrête les flèches.
- **Les affaires tombent au sol autour du corps** : il n'y a rien à fouiller, on
  les ramasse comme n'importe quel objet. Elles n'émettent aucune lumière — ce
  sont la lueur du cadavre et les torches plantées qui les rendent visibles.
- **... et une copie de chacune retourne à sa place d'origine.** Une mort qui
  laisse un cadavre **duplique** donc tout ce que le joueur portait : un
  exemplaire près du corps, un autre là où le level design l'avait posé. C'est
  assumé — mourir enrichit réellement le labyrinthe, les objets se retrouvent à
  des endroits de plus en plus variés, et on n'est jamais obligé de retraverser
  tout l'étage pour récupérer une clé tombée près d'un ancien corps. Le retour à
  la place d'origine a lieu **quelle que soit la cause de la mort**, créature
  comprise : seul un objet donné par un PNJ, qui n'a pas d'emplacement dans la
  carte, peut être définitivement perdu.
- **Une fiole toujours au même endroit, à quelques pas du départ.** Elle y
  revient après chaque mort, quelle qu'en soit la cause : se donner la mort doit
  rester possible à chaque vie. Comme tout se duplique, on peut désormais en
  croiser d'autres exemplaires ailleurs dans l'étage ; c'est la place près du
  départ, et elle seule, qui est garantie pleine.
- **Beaucoup de torches** semées le long du chemin principal, assez pour
  l'éclairer entièrement. Une torche plantée ne se ramasse plus. Une torche
  encore dans le sac au moment d'une mort volontaire se retrouve sur le cadavre
  et se récupère plus tard ; dévoré par la créature, on la perd avec le reste.
- **Mort par piège** : même conséquence qu'une fiole. Le piège à pointes est
  visible dès le départ et **bat en continu** : les pointes sortent puis
  rentrent, et c'est au joueur de lire le rythme pour passer entre deux. Il
  barre toute la largeur du couloir, donc il ne doit jamais rester mortel en
  permanence, sinon le niveau devient infranchissable
  (`tools/walk_test.py` le vérifie).
- **Le squelette archer** : un tireur planté dans une grande salle du chemin,
  qu'on ne peut ni tuer, ni traverser (il bloque comme un mur), ni contourner. Il décoche une flèche toutes les 0,3 s en
  travers de la pièce, entre les deux ouvertures que le joueur doit emprunter :
  la fenêtre de passage existe, mais elle est si courte qu'on ne la trouve pas
  dans le noir — la première traversée se paie d'une mort, et c'est voulu.
  **Il ne s'arrête jamais de tirer, même une fois le joueur tué** : c'est le
  corps laissé en travers de la trajectoire qui arrête les flèches, et qui ouvre
  le passage pour les vies suivantes. Une flèche n'a **pas de portée
  maximale** : elle vole jusqu'à rencontrer un obstacle — un mur, un cadavre ou
  le joueur.
- **Mort par la créature** : sa gueule remplit l'écran (jumpscare) avant la vie
  suivante. **Aucun cadavre et rien au sol** : la vie entière est perdue pour
  rien, et c'est là toute la punition. Les objets qu'on portait retournent, eux,
  là où le level design les avait posés — il faut refaire tout le trajet pour
  aller les rechercher, mais se faire dévorer en portant la clé ne rend jamais
  l'étage infinissable.
- **Physique des cadavres** : ils maintiennent une plaque de pression enfoncée
  (donc une porte ouverte) et bloquent les flèches, mais on marche dessus :
  un cadavre ne condamne jamais un couloir.
- **Créature** : lâchée après un délai fixe, jamais affiché. Elle s'annonce par
  des sons (un grognement different par palier, puis sa propre respiration qui
  s'affole) et par le
  vacillement des torches, puis traque le joueur par le plus court chemin. Elle
  n'est visible qu'à très courte distance.
- **Objets** : clés, fioles, torches. Inventaire limité à 3 emplacements.
- **Portes** : à clé (ouverture définitive) ou commandées par une plaque.
- **Un seul niveau** : atteindre la sortie gagne la partie. Il n'y a ni
  ascension d'étages ni écran de sélection.
- **Police pixel** (*Pixelify Sans*, SIL OFL) sur toute l'interface, jeu compris.
- **Écrans** : accueil (logo, lore, mode de jeu, tableau des scores local),
  victoire et game over. Les deux écrans de fin partagent la même mise en
  page (`views/end_screen.py`) : statistiques alignées, puis la balance des
  morts choisies contre les morts subies.
- **Modes de jeu** : Exploration (libre), Sursis (8 morts max), Contre-la-montre
  (5 minutes).
- **Interface sans bandeau** : tout est dessiné en transparence par-dessus le
  jeu, qui occupe la fenêtre entière. Zone courante en haut à gauche, temps et
  morts en haut à droite, inventaire et rappels de touches (icônes de clavier)
  en bas à droite. L'invite « E » n'apparaît que lorsqu'une interaction est
  réellement possible.

## Où brancher vos ajouts (travail en parallèle)

Chaque module est indépendant : tant que vous ne touchez qu'à vos fichiers, les
conflits Git sont rares.

| Vous voulez... | Fichier à ouvrir |
|----------------|------------------|
| équilibrer (vitesses, délais, rayons de lumière, modes) | `src/constants.py` |
| dessiner les niveaux | `assets/maps/*.tmx` (Tiled) + `assets/maps/README.md` |
| ajouter un type de piège | `src/environment/trap.py` |
| ajouter un objet ramassable | `src/entities/items.py` + `src/mechanics/interaction_manager.py` |
| faire vivre les PNJ | `src/entities/npc.py` (squelette prêt, aucun PNJ posé) |
| changer le comportement de la créature | `src/mechanics/monster_manager.py` |
| remplacer un son | déposer le fichier sous le même nom (inventaire : `assets/audio/README.md`) |
| régler le volume d'un son | `AUDIO_VOLUMES` dans `src/constants.py`, puis `tools/check_audio_levels.py` |
| monter ou baisser tout le jeu | `AUDIO_MASTER_VOLUME` dans `src/constants.py` |
| changer de sprites | `tools/import_pack_assets.py` (le jeu ne lit que `assets/sprites/`) |
| retoucher le HUD ou les menus | `src/ui/` |
| modifier la boucle de jeu | `src/views/game_view.py` |

Règle de game design à ne pas casser : **aucun compte à rebours ne doit être
affiché** pour la créature. Le joueur ne dispose que du son et de la lumière.

## Outils

```bash
python tools/import_pack_assets.py       # importe les sprites du pack Dungeons & Pixels
python tools/gen_placeholder_assets.py   # regenere les sons et le degrade de lumiere
python tools/check_audio_levels.py       # verifie l'equilibre des volumes sonores
python tools/gen_placeholder_maps.py     # regenere les cartes (ECRASE les .tmx !)
python tools/check_levels.py             # verifie que chaque niveau est terminable
python tools/walk_test.py                # traverse chaque niveau avec le vrai moteur de collisions
python tools/smoke_test.py /tmp/shots    # joue un scenario scripte et enregistre des captures
```

Après une modification de carte, lancez `check_levels.py` (cohérence : sortie
atteignable, clé pas enfermée, fiole unique, assez de torches) **et**
`walk_test.py` (praticabilité réelle : couloirs assez larges, passages ouverts).
Avant de pousser, lancez `smoke_test.py` : il rejoue une partie complète et
échoue si une mécanique est cassée.

## Assets

Les **sprites** viennent du pack pixel art *Dungeons & Pixels* (32x32), placé
dans `map/dungeonsAndPixels/`. Le jeu ne lit jamais ce dossier directement :
`tools/import_pack_assets.py` recopie ce dont on a besoin dans `assets/sprites/`
et `assets/maps/` sous les noms attendus par le code. Pour changer de pack ou de
personnage, c'est le seul fichier à modifier.

Les **sons** sont en place et branchés : `assets/audio/README.md` liste, pour
chaque fichier, le moment exact où il joue. Pour en remplacer un, déposez le
vôtre sous le même nom — il n'y a pas une ligne de code à toucher. Trois sons
seulement sont encore des placeholders de synthèse (`misc/trap/arrow_shot.wav`,
`misc/victory.wav`, `misc/game_over.wav`) ; le générateur ne les réécrit jamais
s'ils existent déjà. Les volumes se règlent dans `AUDIO_VOLUMES`
(`src/constants.py`).

Attention si vous changez les sprites de personnages : leur boîte de collision
est un petit rectangle centré, pas la taille de l'image. Le héros fait 32x48
alors que les couloirs les plus étroits font 32 px de large. Après tout
changement de sprite, relancez `python tools/walk_test.py`.

## Pas encore fait

- **Le PNJ troque un bouclier contre une clé, autant de fois qu'on veut** :
  tant qu'on n'a pas de bouclier il en réclame un, dès qu'on en a un il le prend
  et rend une clé en disant d'aller s'en servir. Rien n'est mémorisé : revenir
  avec un second bouclier redonne une seconde clé. Les clés se stockent donc,
  au prix d'un aller-retour — et une clé dévorée par la créature est toujours
  récupérable.
- La créature ne dévore pas les cadavres (le pitch l'évoque) : à ajouter dans
  `monster_manager` si vous voulez punir l'accumulation de dépouilles.
- Pas de mémoire des zones explorées (la carte ne reste pas partiellement
  visible après la mort) : `lighting_engine` est l'endroit pour l'ajouter.
- Trois sons sur trente sont encore des placeholders de synthèse : le tir de
  l'archer, la victoire et la défaite.
- Pas d'animation d'attaque (le pack en fournit pourtant une).
