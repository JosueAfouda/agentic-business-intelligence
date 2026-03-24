import pandas as pd
import plotly.express as px

def main():
    # File paths
    csv_path = "outputs/performance_olympique/performance_olympique.csv"
    output_html_path = "outputs/performance_olympique/performance_olympique.html"
    
    # 1. Load the CSV file using pandas
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return

    # 2. Data Preparation
    # Clean whitespace and ensure correct sorting for the visualization
    df['Pays'] = df['Pays'].str.strip()
    df = df.sort_values(by="Médailles par Million d'Habitants", ascending=True)

    # 3. Create the MOST APPROPRIATE interactive Plotly visualization
    # A horizontal bar chart is ideal for ranking 25 categories (countries) 
    # as it keeps labels readable and allows for clear comparison of the ratio.
    fig = px.bar(
        df,
        x="Médailles par Million d'Habitants",
        y="Pays",
        orientation='h',
        title="<b>Top 25 des pays par performance olympique (Jeux d'été)</b><br><sup>Médailles totales rapportées à la population (par million d'habitants)</sup>",
        labels={
            "Médailles par Million d'Habitants": "Médailles / Million hab.",
            "Pays": "Pays",
            "Total Médailles Été": "Total médailles",
            "Population (Millions)": "Population (M)"
        },
        hover_data={
            "Médailles par Million d'Habitants": ":.4f",
            "Total Médailles Été": True,
            "Population (Millions)": ":.2f",
            "Pays": True
        },
        color="Médailles par Million d'Habitants",
        color_continuous_scale="Viridis",
        template="plotly_white"
    )

    # 4. UX & Visual Quality improvements
    fig.update_layout(
        xaxis_title="Nombre de médailles par million d'habitants",
        yaxis_title=None,
        coloraxis_showscale=False,
        margin=dict(l=20, r=40, t=80, b=60),
        height=850,
        hoverlabel=dict(bgcolor="white", font_size=12),
        title_font_size=20
    )

    # Add a note about the data context
    fig.add_annotation(
        text="Note: Les pays à faible population (ex: Bahamas, Jamaïque) dominent ce classement relatif.",
        xref="paper", yref="paper",
        x=1, y=-0.08,
        showarrow=False,
        font=dict(size=10, color="gray")
    )

    # 5. Save the visualization as an HTML file
    fig.write_html(output_html_path)

if __name__ == "__main__":
    main()