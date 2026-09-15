# Configuration de l'environnement (Windows)

Toutes les étapes se font dans un terminal **PowerShell**.

---

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