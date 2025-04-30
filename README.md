# lecteur-metadata-comfyui

**⚠️ Ce script est conçu uniquement pour les images issues de ComfyUI.**

## Description

`comfyui_metadata_gui.py` est une application en **Tkinter** qui permet :

- D’afficher la miniature d’une image générée par **ComfyUI**
- D’extraire et d’afficher ses métadonnées (prompt, sampler, steps, etc.)
- D’utiliser soit le bouton **Ouvrir image**, soit le **glisser-déposer** directement sur la zone de prévisualisation


## Fonctionnalités clés

- **Drag & Drop** : déposez un fichier `.png` ou `.jpg` sur la zone centrale
- **Extraction avancée** : récupère metadata stockées dans l’image (info tEXt, EXIF, commentaire JPEG, XMP, voire JSON du workflow ComfyUI)
- **Affichage interactif** :
  - Miniature redimensionnée (100×100)
  - Métadonnées dans une zone scindée avec menu contextuel (copier / sélectionner tout)


## Prérequis

- **Python 3.8+**
- Modules Python :
  - **Pillow** (PIL)
  - **tkinterdnd2** (support drag & drop)


## Installation

1. Clonez ou copiez ce dépôt dans un dossier local.
2. Ouvrez une console dans ce dossier.
3. Installez les dépendances :
   ```bash
   pip install Pillow tkinterdnd2
   ```


## Utilisation

1. Lancez l’application :
   ```bash
   python comfyui_metadata_gui.py
   ```
2. **Ouvrir une image** : cliquez sur le bouton "Ouvrir image" et sélectionnez votre fichier.
3. **Glisser-déposer** : faites glisser un fichier image (.png, .jpg, .jpeg) sur la zone "Déposez une image ici".
4. La miniature et les métadonnées apparaissent automatiquement.


## Structure du script

- **extraire_metadata(path)** : lit l’image, cherche metadata dans
  - `img.info['parameters']`, comment tEXt, comment JPEG, EXIF
  - contenu brut pour JSON de workflow ComfyUI
- **MetaViewerApp** (TkinterDnD) :
  - `create_widgets()` : construction de l’UI (label, bouton, text)
  - `choose_image()` & `on_drop()` : chargement et extraction
  - `show_preview()` : miniature 100×100
  - `show_metadata()` : affichage du dictionnaire


## Personnalisation

- **Ajuster la taille de la vignette** : modifiez `img.thumbnail((W,H))` dans `show_preview()`
- **Filtres de fichiers** : changez l’extension dans `askopenfilename`
- **Ajouter des champs** : modifiez la fonction `extraire_metadata`

- # Lecteur de Métadonnées ComfyUI - Executable Windows (EXE)

Ce README accompagne le fichier **`comfyui_metadata_gui.exe`**, votre application autonome pour afficher les métadonnées d’images issues de ComfyUI.

---

## 💾 Contenu du paquet

- `comfyui_metadata_gui.exe` : exécutable Windows (tout-en-un).
- `icon.ico` *(optionnel)* : icône de l’application.
- *(pas de dépendances externes à installer)*

---

## 🚀 Lancement

1. **Double-cliquez** sur `comfyui_metadata_gui.exe`.  
2. L’interface graphique s’ouvre sans console.

---

## 🎯 Fonctionnalités

- **Ouvrir une image** : cliquez sur **Ouvrir image**, sélectionnez un PNG/JPG.
- **Glisser-déposer** : déposez directement un fichier image sur la zone de prévisualisation.
- **Miniature** : aperçu 100×100 px.
- **Métadonnées** : prompt, sampler, étapes, modèle, VAE, seed, Lora, CFG Scale.

---

## 📂 Structure de l’UI

```
+---------------------------------------------+
| [Ouvrir image]                              |
+---------------------------------------------+
| [Zone Prévisualisation] | [Zone Métadonnées]|
| (Glisser-déposer ici)   | (Copier / Tout sel.)|
+---------------------------------------------+
```

---

## 🔄 Mise à jour

Pour générer une nouvelle version EXE à partir du code source :

1. Installez **PyInstaller** (si nécessaire) :
   ```bash
   pip install pyinstaller
   ```
2. Dans le dossier du script Python (`comfyui_metadata_gui.py`), lancez :
   ```bash
   pyinstaller --onefile --windowed --icon=icon.ico comfyui_metadata_gui.py
   ```
3. Récupérez le nouvel EXE dans `dist/comfyui_metadata_gui.exe`.

---

## ❓ Problèmes & Support

- Si l’appli ne se lance pas, vérifiez votre antivirus ou vos permissions Windows.  
- Pour toute question, ouvrez une issue sur le dépôt GitHub associé.

---

*Ce programme est fourni "en l’état" sans garantie. Utilisation libre.*




## Licence

Libre d’utilisation, modification et distribution.  
(Ce projet n’est pas affilié à Automattic / ComfyUI.)

