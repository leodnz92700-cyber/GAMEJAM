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


GAMEJAM/
├── .gitignore
├── .python-version
├── requirements.txt
├── README.md
├── main.py                  <-- Point d'entrée pour lancer le jeu
├── data/                    <-- Fichiers de sauvegarde
│   └── leaderboard.json     <-- Tableau des scores local
├── assets/                  <-- Toutes les ressources externes
│   ├── sprites/             <-- Personnages, murs, torches, cadavres
│   ├── audio/               <-- Musique flippante, bruitages
│   ├── fonts/               <-- Polices d'écriture pour l'UI
│   └── maps/                <-- Fichiers Tiled (.tmx) ou JSON pour les niveaux
└── src/                     <-- Code source du jeu
    ├── constants.py         <-- Tailles d'écran, timer de mort, couleurs
    ├── views/               <-- Les différents écrans (Arcade Views)
    ├── entities/            <-- Les objets interactifs
    ├── mechanics/           <-- Moteurs logiques
    └── ui/                  <-- Éléments d'interface