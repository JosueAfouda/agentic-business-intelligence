import subprocess
import sys
from pathlib import Path

DATAVIZ_DIR = Path("dataviz")
OUTPUTS_DIR = Path("outputs")

def run():
    # Parcours tous les scripts de dataviz
    for dataviz_file in DATAVIZ_DIR.glob("*.py"):
        question_name = dataviz_file.stem
        out_dir = OUTPUTS_DIR / question_name
        html_path = out_dir / f"{question_name}.html"

        # Skip si le HTML existe déjà
        if html_path.exists():
            print(f"[SKIP] {html_path} existe déjà, pas d'exécution")
            continue

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

if __name__ == "__main__":
    run()
