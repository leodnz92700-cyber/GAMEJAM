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
│   └── smoke_test.py                # [Melvin] Rejoue une partie complète et capture des écrans
│
├── assets/
│   ├── audio/                       # [Léo] Sons placeholder générés, à remplacer par les vrais (mêmes noms)
│   │   ├── ambience_drone.wav       # [Léo] Nappe de fond, son volume monte avec la tension
│   │   ├── growl_far.wav            # [Léo] Palier 1 : grondement lointain
│   │   ├── scratch.wav              # [Léo] Palier 2 : griffes sur la pierre
│   │   ├── steps_close.wav          # [Léo] Palier 3 : des pas courent
│   │   ├── heartbeat.wav            # [Léo] Palier 4 : la créature est lâchée
│   │   ├── devoured.wav             # [Léo] Mort subie
│   │   ├── death_vial.wav           # [Léo] Mort choisie
│   │   └── pickup, door_open, torch_place, plate_click, trap_trigger  # [Léo] Interactions
│   ├── fonts/                       # [Erwan] Polices (vide : police système pour l'instant)
│   ├── maps/                        # [Tom]
│   │   ├── level_01.tmx             # [Tom] Étage 1
│   │   ├── level_02.tmx             # [Tom] Étage 2
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
│       ├── exit.png                 # [Tom] Escalier vers l'étage suivant
│       ├── trap_dart.png, dart.png  # [Tom] Piège à fléchettes
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
    │   └── trap.py                  # [Inès] Pointes cycliques visibles + piège à fléchettes
    │
    ├── mechanics/
    │   ├── audio_manager.py         # [Léo] NOUVEAU — point d'entrée unique du son, paliers de tension
    │   ├── death_manager.py         # [Inès] Mort choisie (cadavre + objets) vs subie (rien)
    │   ├── interaction_manager.py   # [Melvin] Touches E/F/R : ramasser, ouvrir, planter, boire
    │   ├── inventory_system.py      # [Théo] Sac de 2 places
    │   ├── level_manager.py         # [Melvin] Construit un étage, simule l'environnement, gère les zones
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
    │   ├── menu_components.py       # [Erwan] Boutons et listes navigables
    │   └── text_cache.py            # [Erwan] NOUVEAU — draw_text_cached, à utiliser au lieu de arcade.draw_text
    │
    └── views/
        ├── game_over_view.py        # [Inès] Défaite + statistiques
        ├── game_view.py             # [Melvin] Boucle principale : orchestre tous les modules
        ├── level_select.py          # [Erwan] Sélection de l'étage
        ├── main_menu.py             # [Erwan] Accueil, lore, mode de jeu, tableau des scores
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
python main.py --level 2                        # demarrer a l'etage 2
python main.py --map level_test.tmx --skip-menu  # charger une carte precise, sans menu
```

## Contrôles

| Touche | Action |
|--------|--------|
| `Z` `Q` `S` `D` ou les flèches | se déplacer |
| `E` | interagir : ramasser un objet, ouvrir une porte, parler — l'invite n'apparaît que si quelque chose est à portée |
| `F` | planter une torche (éclaire la zone définitivement) |
| `R` | boire la fiole : mort volontaire |
| `Échap` | retour au menu |

## Ce qui fonctionne déjà

- Vue de dessus, déplacement animé dans quatre directions, collisions avec les murs.
- **Caméra fixe par zone** : un écran = une zone de 40x22 tuiles, la caméra
  saute à la zone adjacente quand le joueur franchit une frontière (petit fondu).
  Chaque étage fait 4 zones. Les frontières de zone sont des murs pleins, percés
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
  et arrête les fléchettes.
- **Les affaires tombent au sol autour du corps** : il n'y a rien à fouiller, on
  les ramasse comme n'importe quel objet. Elles n'émettent aucune lumière — ce
  sont la lueur du cadavre et les torches plantées qui les rendent visibles.
- **Une seule fiole par étage**, posée à quelques pas du départ. Elle réapparaît
  toujours au même endroit après chaque mort, quelle qu'en soit la cause : on ne
  peut donc jamais en stocker, mais on n'est jamais bloqué non plus.
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
- **Mort par la créature** : sa gueule remplit l'écran (jumpscare) avant la vie
  suivante. Aucun cadavre, tous les objets perdus. Les objets
  UNIQUES (la fiole, les clés) reviennent cependant là où le level design les
  avait posés : sans cela, se faire dévorer en portant la clé détruirait le seul
  exemplaire et rendrait l'étage définitivement infinissable. La punition reste
  entière — il faut refaire tout le trajet pour aller la rechercher.
- **Physique des cadavres** : ils maintiennent une plaque de pression enfoncée
  (donc une porte ouverte) et bloquent les fléchettes, mais on marche dessus :
  un cadavre ne condamne jamais un couloir.
- **Créature** : lâchée après un délai fixe, jamais affiché. Elle s'annonce par
  des sons (grondement lointain, grattements, pas qui courent) et par le
  vacillement des torches, puis traque le joueur par le plus court chemin. Elle
  n'est visible qu'à très courte distance.
- **Objets** : clés, fioles, torches. Inventaire limité à 2 emplacements.
- **Portes** : à clé (ouverture définitive) ou commandées par une plaque.
- **Écrans** : accueil (lore, mode de jeu, tableau des scores local), sélection
  d'étage, victoire et game over avec statistiques.
- **Modes de jeu** : Exploration (libre), Sursis (8 morts max), Contre-la-montre
  (5 minutes).
- **Interface sans bandeau** : tout est dessiné en transparence par-dessus le
  jeu, qui occupe la fenêtre entière. Étage et zone en haut à gauche, temps et
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
| remplacer les sons | déposer vos fichiers dans `assets/audio/` sous les mêmes noms (voir `audio_manager.py`) |
| changer de sprites | `tools/import_pack_assets.py` (le jeu ne lit que `assets/sprites/`) |
| retoucher le HUD ou les menus | `src/ui/` |
| modifier la boucle de jeu | `src/views/game_view.py` |

Règle de game design à ne pas casser : **aucun compte à rebours ne doit être
affiché** pour la créature. Le joueur ne dispose que du son et de la lumière.

## Outils

```bash
python tools/import_pack_assets.py       # importe les sprites du pack Dungeons & Pixels
python tools/gen_placeholder_assets.py   # regenere les sons et le degrade de lumiere
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

Les **sons** sont encore des placeholders de synthèse générés en Python. Déposez
vos vrais fichiers dans `assets/audio/` sous les mêmes noms (voir
`src/mechanics/audio_manager.py`) et ne relancez plus le générateur.

Attention si vous changez les sprites de personnages : leur boîte de collision
est un petit rectangle centré, pas la taille de l'image. Le héros fait 32x48
alors que les couloirs les plus étroits font 32 px de large. Après tout
changement de sprite, relancez `python tools/walk_test.py`.

## Pas encore fait

- Les PNJ existent en tant que classe mais aucun n'est posé dans les cartes.
- La créature ne dévore pas les cadavres (le pitch l'évoque) : à ajouter dans
  `monster_manager` si vous voulez punir l'accumulation de dépouilles.
- Pas de mémoire des zones explorées (la carte ne reste pas partiellement
  visible après la mort) : `lighting_engine` est l'endroit pour l'ajouter.
- Les sons sont encore des placeholders de synthèse.
- Pas d'animation d'attaque (le pack en fournit pourtant une).
