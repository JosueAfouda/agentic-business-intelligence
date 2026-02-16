import pandas as pd
import plotly.express as px

def main():
    csv_path = "outputs/top_five_customers/top_five_customers.csv"
    output_html_path = "outputs/top_five_customers/top_five_customers.html"

    # Chargement des données issues de l'analyse SQL
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return

    # Tri des données par rentabilité pour un meilleur rendu visuel (classement)
    df = df.sort_values(by="total_paiements_valides", ascending=True)

    # Création d'un graphique à barres horizontales interactif
    fig = px.bar(
        df,
        x="total_paiements_valides",
        y="client",
        orientation="h",
        text="total_paiements_valides",
        title="Top 5 des Clients les plus Rentables (Dernière Année)",
        labels={
            "client": "Nom du Client",
            "total_paiements_valides": "Chiffre d'Affaires ($)",
            "nombre_locations_qualifiees": "Locations Effectuées"
        },
        hover_data={
            "nombre_locations_qualifiees": True, 
            "total_paiements_valides": ":.2f$"
        },
        template="plotly_white",
        color="total_paiements_valides",
        color_continuous_scale="Viridis"
    )

    # Amélioration de la lisibilité et de l'esthétique
    fig.update_traces(
        texttemplate='%{text:.2f}$',
        textposition='outside',
        cliponaxis=False
    )

    fig.update_layout(
        xaxis_title="Montant Total des Paiements ($)",
        yaxis_title=None,
        coloraxis_showscale=False,
        margin=dict(l=150, r=50, t=100, b=50),
        font=dict(family="Arial, sans-serif", size=14),
        title_font=dict(size=22)
    )

    # Ajout d'une annotation expliquant le contexte métier (filtres appliqués)
    fig.add_annotation(
        text="Critères : Catégories les plus louées, taux de retard < moyenne globale, transactions sur les 12 derniers mois.",
        xref="paper", yref="paper",
        x=0, y=1.06, showarrow=False,
        font=dict(size=12, color="gray"),
        align="left"
    )

    # Sauvegarde du graphique interactif au format HTML
    fig.write_html(output_html_path)

if __name__ == "__main__":
    main()