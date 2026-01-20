#!/usr/bin/env python3
"""
Smart File Renamer - Outil de renommage de fichiers musicaux
Renomme les fichiers au format: ARTISTE - TITRE.ext (uppercase)
"""

import os
import re
import argparse
import sys
from pathlib import Path

# Extensions audio supportées
AUDIO_EXTENSIONS = {'.mp3', '.flac', '.m4a', '.ogg', '.wav', '.wma', '.aac', '.opus'}

# Patterns à nettoyer dans les noms de fichiers
CLEANUP_PATTERNS = [
    r'#[^#]+#',           # #FREE DL#, #PREMIERE#, etc.
    r'\[.*?\]',           # [Free Download], [Official], etc.
    r'\(.*?free.*?\)',    # (free download), (FREE), etc. (insensible à la casse)
    r'\(.*?download.*?\)',# (download), (Free Download), etc.
    r'\(.*?premiere.*?\)',# (premiere), (PREMIERE), etc.
    r'\(.*?original\s*mix.*?\)',  # (Original Mix)
    r'\(.*?extended\s*mix.*?\)',  # (Extended Mix)
    r'\(.*?radio\s*edit.*?\)',    # (Radio Edit)
    r'\(.*?club\s*mix.*?\)',      # (Club Mix)
    r'\d{5,}',            # Chiffres aléatoires (5+ chiffres) n'importe où
    r'_+',                # Underscores multiples -> espace
    r'\s+',               # Espaces multiples -> espace unique
]


def try_import_tinytag():
    """Tente d'importer tinytag pour les métadonnées audio."""
    try:
        from tinytag import TinyTag
        return TinyTag
    except ImportError:
        return None


def get_metadata(filepath: Path):
    """Récupère les métadonnées artist et title d'un fichier audio."""
    TinyTag = try_import_tinytag()
    if TinyTag is None:
        return None, None

    try:
        tag = TinyTag.get(str(filepath))
        artist = tag.artist.strip() if tag.artist else None
        title = tag.title.strip() if tag.title else None
        return artist, title
    except Exception:
        return None, None


def clean_filename(name: str) -> str:
    """Nettoie un nom de fichier des éléments indésirables."""
    cleaned = name

    # Supprimer les patterns indésirables
    cleaned = re.sub(r'#[^#]+#', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\[.*?\]', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(.*?free.*?\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(.*?download.*?\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(.*?premiere.*?\)', '', cleaned, flags=re.IGNORECASE)

    # Supprimer les patterns de type mix/version
    cleaned = re.sub(r'\(.*?original\s*mix.*?\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(.*?extended\s*mix.*?\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(.*?radio\s*edit.*?\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(.*?club\s*mix.*?\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(.*?remix.*?\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(.*?bootleg.*?\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(.*?edit.*?\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(.*?version.*?\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(.*?mix.*?\)', '', cleaned, flags=re.IGNORECASE)

    # Supprimer les chiffres aléatoires (5+ chiffres) n'importe où dans le nom
    cleaned = re.sub(r'\d{5,}', '', cleaned)

    # Remplacer underscores par espaces
    cleaned = re.sub(r'_+', ' ', cleaned)

    # Nettoyer les espaces multiples
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Supprimer espaces autour du tiret séparateur
    cleaned = re.sub(r'\s*-\s*', ' - ', cleaned)

    # Supprimer espaces en début/fin
    cleaned = cleaned.strip()

    # Supprimer tiret orphelin en fin
    cleaned = re.sub(r'\s*-\s*$', '', cleaned)

    return cleaned


def parse_filename(filename: str) -> tuple:
    """
    Parse un nom de fichier pour extraire artiste et titre.
    Attend le format: "artiste - titre" ou variantes.
    """
    # Supprimer l'extension
    name = Path(filename).stem

    # Nettoyer le nom
    name = clean_filename(name)

    # Chercher le séparateur artiste - titre
    if ' - ' in name:
        parts = name.split(' - ', 1)
        artist = parts[0].strip()
        title = parts[1].strip() if len(parts) > 1 else ''
        return artist, title

    # Si pas de séparateur, retourner le nom nettoyé comme titre
    return None, name


def generate_new_name(artist: str, title: str, extension: str) -> str:
    """Génère le nouveau nom de fichier en uppercase."""
    if artist and title:
        new_name = f"{artist} - {title}".upper()
    elif title:
        new_name = title.upper()
    else:
        return None

    # Nettoyer les caractères interdits dans les noms de fichiers Windows
    forbidden_chars = '<>:"/\\|?*'
    for char in forbidden_chars:
        new_name = new_name.replace(char, '')

    return f"{new_name}{extension.lower()}"


def get_unique_filepath(filepath: Path) -> Path:
    """Génère un chemin unique si le fichier existe déjà."""
    if not filepath.exists():
        return filepath

    base = filepath.stem
    ext = filepath.suffix
    parent = filepath.parent
    counter = 1

    while True:
        new_name = f"{base} ({counter}){ext}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def process_file(filepath: Path, dry_run: bool = False) -> tuple:
    """
    Traite un fichier audio et le renomme.
    Retourne (success, old_name, new_name, message)
    """
    old_name = filepath.name
    extension = filepath.suffix.lower()

    # Vérifier si c'est un fichier audio
    if extension not in AUDIO_EXTENSIONS:
        return False, old_name, None, "Extension non supportée"

    # Essayer d'abord les métadonnées
    artist, title = get_metadata(filepath)

    # Si pas de métadonnées, parser le nom de fichier
    if not artist or not title:
        parsed_artist, parsed_title = parse_filename(old_name)
        artist = artist or parsed_artist
        title = title or parsed_title
    else:
        # Nettoyer aussi les métadonnées
        artist = clean_filename(artist) if artist else None
        title = clean_filename(title) if title else None

    # Générer le nouveau nom
    new_name = generate_new_name(artist, title, extension)

    if not new_name:
        return False, old_name, None, "Impossible de déterminer le nouveau nom"

    # Si le nom est identique, ne rien faire
    if old_name == new_name:
        return True, old_name, new_name, "Déjà correct"

    # Chemin du nouveau fichier
    new_filepath = get_unique_filepath(filepath.parent / new_name)
    final_new_name = new_filepath.name

    if not dry_run:
        try:
            filepath.rename(new_filepath)
            return True, old_name, final_new_name, "Renommé"
        except Exception as e:
            return False, old_name, final_new_name, f"Erreur: {e}"
    else:
        return True, old_name, final_new_name, "À renommer (dry-run)"


def scan_folder(folder_path: Path, recursive: bool = False, dry_run: bool = False):
    """Scanne un dossier et renomme les fichiers audio."""
    if not folder_path.exists():
        print(f"❌ Erreur: Le dossier '{folder_path}' n'existe pas.")
        return

    if not folder_path.is_dir():
        print(f"❌ Erreur: '{folder_path}' n'est pas un dossier.")
        return

    # Collecter les fichiers
    if recursive:
        files = list(folder_path.rglob('*'))
    else:
        files = list(folder_path.glob('*'))

    audio_files = [f for f in files if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS]

    if not audio_files:
        print("ℹ️  Aucun fichier audio trouvé dans le dossier.")
        return

    print(f"\n📁 Dossier: {folder_path}")
    print(f"🎵 {len(audio_files)} fichier(s) audio trouvé(s)")
    if dry_run:
        print("🔍 Mode prévisualisation (dry-run) - aucune modification ne sera effectuée\n")
    else:
        print()

    success_count = 0
    skip_count = 0
    error_count = 0

    for filepath in sorted(audio_files):
        success, old_name, new_name, message = process_file(filepath, dry_run)

        if success:
            if message == "Déjà correct":
                skip_count += 1
                print(f"  ⏭️  {old_name} (déjà correct)")
            else:
                success_count += 1
                print(f"  ✅ {old_name}")
                print(f"      → {new_name}")
        else:
            error_count += 1
            print(f"  ❌ {old_name} - {message}")

    # Résumé
    print(f"\n📊 Résumé:")
    print(f"   ✅ Renommés: {success_count}")
    print(f"   ⏭️  Ignorés: {skip_count}")
    print(f"   ❌ Erreurs: {error_count}")


def interactive_mode():
    """Mode interactif pour sélectionner un dossier."""
    print("\n" + "="*60)
    print("   🎵 SMART FILE RENAMER - Renommeur de fichiers musicaux")
    print("="*60)
    print("\nCet outil renomme vos fichiers audio au format:")
    print("   ARTISTE - TITRE.ext (en majuscules)")
    print("\nIl nettoie automatiquement:")
    print("   • Les tags comme #FREE DL#, [Official], etc.")
    print("   • Les chiffres aléatoires en fin de nom")
    print("   • Les espaces et caractères superflus")
    print()

    while True:
        folder_input = input("📂 Entrez le chemin du dossier (ou 'q' pour quitter): ").strip()

        if folder_input.lower() in ('q', 'quit', 'exit'):
            print("\n👋 Au revoir!")
            break

        # Supprimer les guillemets si présents
        folder_input = folder_input.strip('"\'')

        if not folder_input:
            print("⚠️  Veuillez entrer un chemin valide.\n")
            continue

        folder_path = Path(folder_input)

        if not folder_path.exists():
            print(f"❌ Le dossier '{folder_path}' n'existe pas.\n")
            continue

        if not folder_path.is_dir():
            print(f"❌ '{folder_path}' n'est pas un dossier.\n")
            continue

        # Demander confirmation
        print(f"\n📁 Dossier sélectionné: {folder_path}")

        # Prévisualisation d'abord
        preview = input("\n🔍 Prévisualiser les changements d'abord? (O/n): ").strip().lower()

        if preview != 'n':
            scan_folder(folder_path, recursive=False, dry_run=True)

            confirm = input("\n✏️  Appliquer les changements? (o/N): ").strip().lower()
            if confirm != 'o':
                print("❌ Opération annulée.\n")
                continue

        # Appliquer les changements
        scan_folder(folder_path, recursive=False, dry_run=False)
        print()


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="🎵 Smart File Renamer - Renomme les fichiers audio au format ARTISTE - TITRE.ext",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s "C:\\Ma Musique"                    Renommer les fichiers du dossier
  %(prog)s "C:\\Ma Musique" --dry-run          Prévisualiser sans modifier
  %(prog)s "C:\\Ma Musique" --recursive        Inclure les sous-dossiers
  %(prog)s                                     Mode interactif
        """
    )

    parser.add_argument(
        'folder',
        nargs='?',
        help="Chemin du dossier contenant les fichiers audio"
    )

    parser.add_argument(
        '-d', '--dry-run',
        action='store_true',
        help="Prévisualiser les changements sans les appliquer"
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help="Traiter aussi les sous-dossiers"
    )

    args = parser.parse_args()

    if args.folder:
        folder_path = Path(args.folder)
        scan_folder(folder_path, recursive=args.recursive, dry_run=args.dry_run)
    else:
        # Mode interactif
        interactive_mode()


if __name__ == '__main__':
    main()

