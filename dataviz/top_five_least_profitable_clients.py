import pandas as pd
import plotly.express as px

def main():
    # File paths as defined by the workflow
    csv_path = "outputs/top_five_least_profitable_clients/top_five_least_profitable_clients.csv"
    output_html_path = "outputs/top_five_least_profitable_clients/top_five_least_profitable_clients.html"
    
    # Loading the dataset
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        # Ensure the script handles missing data gracefully during autonomous execution
        return

    # Business Question: 5 least profitable clients in top categories with low delay rates.
    # We sort by revenue ascending to highlight the "least profitable".
    df = df.sort_values(by="Chiffre d'Affaires (Top Catégories)", ascending=True)

    # Design Choice: Horizontal bar chart for clear ranking and readability of names.
    # Color scale helps visualize the intensity of the low revenue.
    fig = px.bar(
        df,
        x="Chiffre d'Affaires (Top Catégories)",
        y="Client",
        orientation='h',
        title="<b>Top 5 des Clients les Moins Rentables</b><br><sup>Critères : Catégories les plus louées & Taux de retard < moyenne</sup>",
        labels={
            "Chiffre d'Affaires (Top Catégories)": "Revenus ($)",
            "Client": "Nom du Client",
            "Taux de Retard Moyen": "Taux de Retard"
        },
        hover_data=["Taux de Retard Moyen"],
        color="Chiffre d'Affaires (Top Catégories)",
        color_continuous_scale="Reds_r", # Emphasize lower values
        text_auto='.2f'
    )

    # Improve layout and interactivity
    fig.update_layout(
        xaxis_title="Total des paiements ($)",
        yaxis_title=None,
        coloraxis_showscale=False,
        template="plotly_white",
        font=dict(family="Arial", size=12),
        margin=dict(l=20, r=20, t=80, b=20),
        hoverlabel=dict(bgcolor="white", font_size=13)
    )

    # Refine hover tooltip for better storytelling
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>" +
                      "Revenu total : %{x:.2f} $<br>" +
                      "Taux de retard : %{customdata[0]:.2%}<extra></extra>",
        textposition='outside'
    )

    # Save to HTML as requested
    fig.write_html(output_html_path)

if __name__ == "__main__":
    main()