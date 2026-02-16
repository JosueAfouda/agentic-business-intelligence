import pandas as pd
import plotly.express as px

def main():
    # File paths based on the provided context
    csv_path = "outputs/staff_performance/staff_performance.csv"
    output_html_path = "outputs/staff_performance/staff_performance.html"

    # 1. Load the CSV file using pandas
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        # Stop execution if data is missing or unreadable
        return

    # 2. Data Preparation
    # Convert 'mois_paiement' to datetime to ensure correct chronological sorting on the X-axis
    df['mois_paiement'] = pd.to_datetime(df['mois_paiement'])
    
    # Sort data by date and then by sales amount for consistent rendering
    df = df.sort_values(by=['mois_paiement', 'montant_total_ventes'], ascending=[True, False])

    # 3. Chart Selection & Creation
    # The goal is to show performance (sales and transaction volume) over time for each staff member.
    # A Line Chart with markers is the most effective way to compare individual trends and monthly fluctuations.
    
    fig = px.line(
        df,
        x="mois_paiement",
        y="montant_total_ventes",
        color="membre_staff",
        markers=True,
        title="Performance Mensuelle du Staff : Chiffre d'Affaires et Transactions",
        labels={
            "mois_paiement": "Mois de l'année",
            "montant_total_ventes": "Montant des Ventes ($)",
            "membre_staff": "Membre du Personnel",
            "nombre_transactions": "Volume de Transactions"
        },
        hover_data={
            "nombre_transactions": True,
            "montant_total_ventes": ":.2f$"
        },
        template="plotly_white",
        line_shape="linear"
    )

    # 4. Interactivity & Visual Quality (UX)
    # Use 'x unified' hovermode for easier comparison of all staff members at a specific point in time
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Chronologie (2007)",
        yaxis_title="Total des Ventes ($)",
        legend_title="Personnel",
        font=dict(family="Arial, sans-serif", size=14),
        title_font=dict(size=22),
        margin=dict(l=40, r=40, t=80, b=40)
    )

    # Format the X-axis to show clear month names
    fig.update_xaxes(
        dtick="M1",
        tickformat="%b %Y",
        showgrid=True,
        gridwidth=1,
        gridcolor='whitesmoke'
    )

    # Ensure Y-axis starts at zero for honest comparison
    fig.update_yaxes(rangemode="tozero")

    # Add a subtitle/annotation to clarify the business insight
    fig.add_annotation(
        text="Analyse : Évolution du chiffre d'affaires et du nombre de transactions par employé.",
        xref="paper", yref="paper",
        x=0, y=1.07, showarrow=False,
        font=dict(size=12, color="gray"),
        align="left"
    )

    # 5. Output
    # Save the visualization as a self-contained interactive HTML file
    fig.write_html(output_html_path)

if __name__ == "__main__":
    main()