import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def main():
    csv_path = "outputs/employees_salary_ethnicity/employees_salary_ethnicity.csv"
    output_html_path = "outputs/employees_salary_ethnicity/employees_salary_ethnicity.html"

    # Chargement des données issues de l'analyse SQL
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        # En cas d'erreur de lecture, on arrête l'exécution
        return

    # Nettoyage des noms d'ethnies pour supprimer les espaces superflus en début/fin de chaîne
    df["Ethnie"] = df["Ethnie"].str.strip()

    # Tri des données par salaire moyen pour faciliter la lecture du classement (ordre croissant pour un graphique horizontal)
    df = df.sort_values(by="Salaire Moyen", ascending=True)

    # Création d'une figure avec deux graphiques côte à côte partageant l'axe vertical (les ethnies)
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Salaire Moyen (€)", "Nombre d'Employés"),
        shared_yaxes=True,
        horizontal_spacing=0.12
    )

    # Premier graphique : Salaire Moyen par Ethnie (Barres horizontales vertes)
    fig.add_trace(
        go.Bar(
            x=df["Salaire Moyen"],
            y=df["Ethnie"],
            orientation='h',
            name="Salaire Moyen",
            marker=dict(
                color='rgba(50, 171, 96, 0.6)',
                line=dict(color='rgba(50, 171, 96, 1.0)', width=1)
            ),
            hovertemplate="<b>%{y}</b><br>Salaire Moyen: %{x:,.2f} €<extra></extra>"
        ),
        row=1, col=1
    )

    # Second graphique : Nombre d'Employés par Ethnie (Barres horizontales violettes)
    fig.add_trace(
        go.Bar(
            x=df["Nombre d'Employés"],
            y=df["Ethnie"],
            orientation='h',
            name="Nombre d'Employés",
            marker=dict(
                color='rgba(128, 0, 128, 0.6)',
                line=dict(color='rgba(128, 0, 128, 1.0)', width=1)
            ),
            hovertemplate="<b>%{y}</b><br>Nombre d'Employés: %{x}<extra></extra>"
        ),
        row=1, col=2
    )

    # Configuration globale du style et des titres
    fig.update_layout(
        title_text="Répartition des Salaires et Effectifs par Ethnie",
        title_font_size=22,
        title_x=0.5,
        template="plotly_white",
        showlegend=False,
        height=600,
        margin=dict(l=150, r=50, t=100, b=50)
    )

    # Ajout des libellés sur l'axe horizontal pour plus de clarté
    fig.update_xaxes(title_text="Salaire Moyen (€)", row=1, col=1)
    fig.update_xaxes(title_text="Nombre d'Employés", row=1, col=2)

    # Sauvegarde de la visualisation interactive au format HTML
    fig.write_html(output_html_path)

if __name__ == "__main__":
    main()