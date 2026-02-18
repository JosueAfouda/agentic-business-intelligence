import pandas as pd
import plotly.express as px

def main():
    csv_path = "outputs/top_movies_by_revenue/top_movies_by_revenue.csv"
    output_html_path = "outputs/top_movies_by_revenue/top_movies_by_revenue.html"

    # Chargement des données issues de l'analyse SQL
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        # Arrêt silencieux si le fichier de données n'est pas encore généré
        return

    # Tri des données par revenu pour un affichage optimal en barres horizontales (du plus élevé au moins élevé)
    df = df.sort_values(by="revenu_total", ascending=True)

    # Création d'un graphique à barres horizontales interactif
    # Ce format est idéal pour comparer des titres de films potentiellement longs
    fig = px.bar(
        df,
        x="revenu_total",
        y="titre_du_film",
        orientation="h",
        text="revenu_total",
        title="Top 10 des Films ayant Généré le Plus de Revenu",
        labels={
            "titre_du_film": "Titre du Film",
            "revenu_total": "Revenu Total ($)"
        },
        hover_data={
            "revenu_total": ":.2f$"
        },
        template="plotly_white",
        color="revenu_total",
        color_continuous_scale="Viridis"
    )

    # Amélioration de la lisibilité des étiquettes de données
    fig.update_traces(
        texttemplate='%{text:.2f}$',
        textposition='outside',
        cliponaxis=False
    )

    # Configuration de la mise en page (UX et style)
    fig.update_layout(
        xaxis_title="Chiffre d'Affaires Cumulé ($)",
        yaxis_title=None,
        coloraxis_showscale=False,
        margin=dict(l=200, r=60, t=100, b=50),
        font=dict(family="Arial, sans-serif", size=14),
        title_font=dict(size=24, color="#2c3e50"),
        hovermode="y unified"
    )

    # Ajout d'une annotation contextuelle
    fig.add_annotation(
        text="Analyse basée sur le montant total des paiements encaissés pour les locations de chaque titre.",
        xref="paper", yref="paper",
        x=0, y=1.07, showarrow=False,
        font=dict(size=12, color="gray"),
        align="left"
    )

    # Sauvegarde du graphique interactif au format HTML pour intégration au rapport
    fig.write_html(output_html_path)

if __name__ == "__main__":
    main()