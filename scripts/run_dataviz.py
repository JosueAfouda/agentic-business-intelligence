import subprocess
import sys
import argparse
from pathlib import Path

OUTPUTS_DIR = Path("outputs")

def run_dataviz_script(dataviz_file: Path):
    question_name = dataviz_file.stem
    out_dir = OUTPUTS_DIR / question_name
    html_path = out_dir / f"{question_name}.html"

    if not out_dir.exists():
        print(f"[WARN] Dossier de sortie manquant pour {question_name}, création.")
        out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[RUN] Génération du graphique pour {question_name}...")

    try:
        subprocess.run(
            [sys.executable, str(dataviz_file)],
            check=True,
            capture_output=True,
            text=True
        )
        if html_path.exists():
            print(f"[OK] Graphique généré : {html_path}")
        else:
            print(f"[ERREUR] Script exécuté mais HTML non trouvé : {html_path}")

    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Échec de génération pour {question_name}")
        print(e.stderr)

def main():
    parser = argparse.ArgumentParser(description="Exécute un script de visualisation de données.")
    parser.add_argument("--dataviz", required=True, help="Chemin vers le script Python de visualisation")
    args = parser.parse_args()

    dataviz_file = Path(args.dataviz)
    if not dataviz_file.exists():
        print(f"Erreur : Le fichier {dataviz_file} n'existe pas.")
        sys.exit(1)

    run_dataviz_script(dataviz_file)

if __name__ == "__main__":
    main()
