# Smart File Renamer 🎵

Un outil léger et portable pour renommer automatiquement vos fichiers musicaux au format standardisé : `ARTISTE - TITRE.ext` (en majuscules).

## Fonctionnalités

- **Nettoyage automatique** des noms de fichiers :
  - Supprime les tags comme `#FREE DL#`, `[Official]`, `(Free Download)`, etc.
  - Supprime les chiffres aléatoires en fin de nom (ex: `titre567898.mp3` → `TITRE.mp3`)
  - Convertit tout en MAJUSCULES
  
- **Lecture des métadonnées** : Utilise les tags ID3/métadonnées intégrées (artiste, titre) quand disponibles

- **Mode prévisualisation** : Voir les changements avant de les appliquer

- **Interface simple** : Mode interactif ou ligne de commande

## 📥 Installation

### Option 1 : Télécharger l'exécutable (recommandé)

Téléchargez `SmartFileRenamer.exe` depuis la section [Releases](../../releases) et exécutez-le directement.

### Option 2 : Exécuter avec Python

```powershell
# Cloner le projet
git clone https://github.com/votre-user/smart-file-renamer.git
cd smart-file-renamer

# Installer les dépendances
pip install tinytag

# Exécuter
python main.py
```

### Option 3 : Construire l'exécutable vous-même

```powershell
# Exécuter le script de build
.\build.ps1
```

L'exécutable sera créé dans le dossier `dist\`.

## 🚀 Utilisation

### Mode interactif (double-clic sur l'exe)

```
🎵 SMART FILE RENAMER - Renommeur de fichiers musicaux

📂 Entrez le chemin du dossier: C:\Ma Musique
```

### Ligne de commande

```powershell
# Renommer les fichiers d'un dossier
SmartFileRenamer.exe "C:\Ma Musique"

# Prévisualiser sans modifier (dry-run)
SmartFileRenamer.exe "C:\Ma Musique" --dry-run

# Inclure les sous-dossiers
SmartFileRenamer.exe "C:\Ma Musique" --recursive

# Afficher l'aide
SmartFileRenamer.exe --help
```

## 📋 Exemples de renommage

| Avant | Après |
|-------|-------|
| `artiste - titre567898.mp3` | `ARTISTE - TITRE.MP3` |
| `artiste - titre #FREE DL#.mp3` | `ARTISTE - TITRE.MP3` |
| `Artist_Name - Song Title [Official].flac` | `ARTIST NAME - SONG TITLE.FLAC` |
| `dj_name - track (Free Download).m4a` | `DJ NAME - TRACK.M4A` |

## 🎵 Formats supportés

- MP3
- FLAC
- M4A / AAC
- OGG / Opus
- WAV
- WMA

## ⚙️ Options

| Option | Description |
|--------|-------------|
| `-d, --dry-run` | Prévisualiser les changements sans les appliquer |
| `-r, --recursive` | Traiter également les sous-dossiers |
| `-h, --help` | Afficher l'aide |

## 🛡️ Sécurité

- **Mode prévisualisation** : Toujours voir les changements avant de les appliquer
- **Gestion des conflits** : Si un fichier avec le même nom existe déjà, un numéro est ajouté automatiquement
- **Aucune suppression** : L'outil renomme uniquement, il ne supprime jamais de fichiers

## 📝 License

MIT License - Libre d'utilisation et de modification.

