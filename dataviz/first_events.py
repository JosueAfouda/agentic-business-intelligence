import pandas as pd
import plotly.express as px

def main():
    # File paths
    csv_path = "outputs/first_events/first_events.csv"
    output_html_path = "outputs/first_events/first_events.html"
    
    # 1. Load the CSV file
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        # If running from a different context, try relative to root
        df = pd.read_csv("outputs/first_events/first_events.csv")

    # 2. Create the MOST APPROPRIATE interactive Plotly visualization
    # Ranking of events by athlete count -> Horizontal Bar Chart
    
    # Sort data descending to have the highest values at the top
    df = df.sort_values(by="Nombre d'Athlètes Uniques", ascending=True)

    fig = px.bar(
        df,
        y="Évènement Olympique",
        x="Nombre d'Athlètes Uniques",
        orientation='h',
        title="Top 10 Olympic Events: Athletes from Nobel-Winning Countries",
        labels={
            "Évènement Olympique": "Olympic Event",
            "Nombre d'Athlètes Uniques": "Unique Athletes Count"
        },
        color="Nombre d'Athlètes Uniques",
        color_continuous_scale="Portland",
        text="Nombre d'Athlètes Uniques"
    )

    # 3. Adjust layout for readability and UX
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Number of Unique Athletes",
        yaxis_title=None, # Clear enough from context
        margin=dict(l=20, r=40, t=80, b=40),
        template="plotly_white",
        hovermode="y unified",
        showlegend=False
    )
    
    fig.update_traces(
        textposition='outside',
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Athletes: %{x}<extra></extra>"
    )

    # 4. Save the visualization as an HTML file
    fig.write_html(output_html_path)

if __name__ == "__main__":
    main()