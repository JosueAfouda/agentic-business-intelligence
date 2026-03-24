import pandas as pd
import plotly.express as px

def main():
    # 1. Configuration & Paths
    csv_path = "outputs/winter_events/winter_events.csv"
    output_html_path = "outputs/winter_events/winter_events.html"
    
    # 2. Data Loading
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        # Fallback to absolute path or relative to project root
        df = pd.read_csv("outputs/winter_events/winter_events.csv")

    if df.empty:
        fig = px.scatter(title="No data found for the query: Winter events with athletes over 40")
        fig.write_html(output_html_path)
        return

    # 3. Visualization Design
    # The objective is to identify specific events. A horizontal bar chart 
    # provides a clean, readable list of event names grouped by sport.
    
    df['Presence'] = 1  # Constant value to ensure equal bar lengths
    df = df.sort_values(by=["Sport", "Événement"], ascending=[True, True])

    fig = px.bar(
        df,
        y="Événement",
        x="Presence",
        color="Sport",
        orientation='h',
        title="Winter Olympic Events Featuring Athletes Over 40",
        labels={
            "Événement": "Olympic Event",
            "Sport": "Sport Category"
        },
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # 4. UI/UX Enhancements
    fig.update_layout(
        title_font_size=22,
        title_x=0.5,
        xaxis_visible=False,  # Quantitative axis is irrelevant for a boolean list
        yaxis_title=None,
        margin=dict(l=20, r=20, t=100, b=50),
        template="plotly_white",
        hovermode="closest",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        height=max(400, 50 * len(df)) # Adaptive height
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Sport: %{fullData.name}<extra></extra>"
    )

    # 5. Export
    fig.write_html(output_html_path)

if __name__ == "__main__":
    main()