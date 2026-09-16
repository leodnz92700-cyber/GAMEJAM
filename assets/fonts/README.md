# Dossier `assets/fonts/`

La police d'interface du jeu.

- **PixelifySans.ttf** — *Pixelify Sans*, police pixel sous licence SIL Open Font
  License 1.1 (le texte complet est dans `OFL.txt`, a conserver si vous
  redistribuez le jeu).
- **OFL.txt** — la licence.

Elle a ete choisie sur trois criteres, dans cet ordre :

1. **De vraies bas-de-casse.** Beaucoup de polices pixel (Silkscreen, Press
   Start 2P) sont en capitales uniquement : le paragraphe de lore de l'ecran
   d'accueil y devenait un mur de majuscules illisible.
2. **Un vrai gras.** Toute la hierarchie de l'interface repose dessus — titres
   de panneaux, valeurs des tableaux, libelles de boutons. Un gras synthetique
   sur du pixel art donne un pate.
3. **Lisible a petite taille**, parce que l'ATH est pose en transparence sur un
   jeu tres sombre.

Elle est chargee par `src/ui/fonts.py` et appliquee **automatiquement** par
`src/ui/text_cache.py` : tout texte passant par `draw_text_cached` l'utilise,
il n'y a rien a preciser a l'appel.
