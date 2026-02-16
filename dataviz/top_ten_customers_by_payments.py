import pandas as pd
import plotly.express as px

def main():
    csv_path = "outputs/top_ten_customers_by_payments/top_ten_customers_by_payments.csv"
    output_html_path = "outputs/top_ten_customers_by_payments/top_ten_customers_by_payments.html"

    # Chargement des données issues de l'analyse SQL
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        # Sortie silencieuse en cas d'erreur de lecture (ex: fichier manquant)
        return

    # Préparation des données : combinaison des noms et tri pour le classement
    df['client'] = df['prenom'] + ' ' + df['nom']
    # Tri ascendant pour que les plus gros payeurs soient en haut dans un graphique à barres horizontales
    df = df.sort_values(by="montant_total_paye", ascending=True)

    # Création du graphique à barres horizontales interactif
    fig = px.bar(
        df,
        x="montant_total_paye",
        y="client",
        orientation="h",
        text="montant_total_paye",
        title="Top 10 des Clients par Montant Total des Paiements",
        labels={
            "montant_total_paye": "Total des Paiements ($)",
            "client": "Nom du Client"
        },
        template="plotly_white",
        color="montant_total_paye",
        color_continuous_scale="Viridis"
    )

    # Amélioration de l'esthétique et du formatage des données
    fig.update_traces(
        texttemplate='%{text:.2f}$',
        textposition='outside',
        cliponaxis=False
    )

    fig.update_layout(
        xaxis_title="Montant Cumulé ($)",
        yaxis_title=None,
        coloraxis_showscale=False,
        margin=dict(l=150, r=50, t=100, b=50),
        font=dict(family="Arial, sans-serif", size=13),
        title_font=dict(size=22),
        hovermode="y unified"
    )

    # Ajout du contexte métier (question d'origine)
    fig.add_annotation(
        text="Question : Quels sont les 10 clients ayant effectué les paiements totaux les plus élevés sur toute la période ?",
        xref="paper", yref="paper",
        x=0, y=1.08, showarrow=False,
        font=dict(size=12, color="gray"),
        align="left"
    )

    # Sauvegarde du graphique interactif au format HTML
    fig.write_html(output_html_path)

if __name__ == "__main__":
    main()