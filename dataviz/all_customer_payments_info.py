import pandas as pd
import plotly.express as px

def main():
    # 1. Load the CSV file
    csv_path = "outputs/all_customer_payments_info/all_customer_payments_info.csv"
    output_html_path = "outputs/all_customer_payments_info/all_customer_payments_info.html"
    
    df = pd.read_csv(csv_path)

    # 2. Data Preparation
    # Convert date_paiement to datetime objects
    df['date_paiement'] = pd.to_datetime(df['date_paiement'])
    
    # Sort by date (as per business request)
    df = df.sort_values('date_paiement')

    # Since there are >14,000 rows, a raw scatter plot would be unreadable.
    # We aggregate by day and staff member to show the business trend and staff performance.
    df_daily = df.groupby([df['date_paiement'].dt.date, 'membre_personnel']).agg(
        total_montant=('montant', 'sum'),
        nombre_paiements=('montant', 'count')
    ).reset_index()
    
    df_daily.rename(columns={'date_paiement': 'date'}, inplace=True)

    # 3. Create the Visualization
    # A line chart is most appropriate for time-based payment trends.
    fig = px.line(
        df_daily,
        x="date",
        y="total_montant",
        color="membre_personnel",
        title="Évolution Quotidienne des Paiements par Membre du Personnel",
        labels={
            "date": "Date de Paiement",
            "total_montant": "Montant Total ($)",
            "membre_personnel": "Personnel",
            "nombre_paiements": "Nombre de transactions"
        },
        hover_data={"nombre_paiements": True},
        template="plotly_white",
        category_orders={"membre_personnel": sorted(df['membre_personnel'].unique())}
    )

    # Enhance visual quality
    fig.update_traces(mode="lines+markers", marker=dict(size=4))
    fig.update_layout(
        hovermode="x unified",
        legend_title_text='Membre du Personnel',
        xaxis_title="Chronologie des paiements",
        yaxis_title="Recettes totales par jour ($)"
    )

    # 4. Save the visualization
    fig.write_html(output_html_path)

if __name__ == "__main__":
    main()
