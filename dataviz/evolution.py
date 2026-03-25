from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


INPUT_CSV = Path("outputs/evolution/evolution.csv")
OUTPUT_HTML = Path("outputs/evolution/evolution.html")


def fmt_int(value):
    return f"{int(value):,}".replace(",", " ")


def load_data():
    df = pd.read_csv(INPUT_CSV)
    df["nom_athlete"] = df["nom_athlete"].fillna("Athlète inconnu")
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype("Int64")
    df["total_medailles_bronze_ete"] = pd.to_numeric(
        df["total_medailles_bronze_ete"], errors="coerce"
    ).fillna(0)
    return df


def create_empty_figure(message):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=18),
        align="center",
    )
    fig.update_layout(
        template="plotly_white",
        title="Évolution des médailles de bronze (jeux d'été) par athlète",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=40, r=40, t=80, b=40),
        height=500,
    )
    return fig


def build_single_year_chart(df):
    positive_df = (
        df.loc[df["total_medailles_bronze_ete"] > 0, ["nom_athlete", "annee", "total_medailles_bronze_ete"]]
        .sort_values(["total_medailles_bronze_ete", "nom_athlete"], ascending=[False, True])
        .reset_index(drop=True)
    )

    if positive_df.empty:
        return create_empty_figure("Aucune médaille de bronze n'est présente dans le fichier.")

    total_athletes = len(df)
    zero_athletes = int((df["total_medailles_bronze_ete"] <= 0).sum())
    year_value = int(df["annee"].dropna().iloc[0])

    view_sizes = []
    for n in (10, 25, 50, len(positive_df)):
        if n <= len(positive_df) and n not in view_sizes:
            view_sizes.append(n)
    default_n = 25 if len(positive_df) >= 25 else len(positive_df)

    def subset_for(n):
        subset = positive_df.head(n).copy()
        return subset

    def chart_height(n):
        return min(max(520, 130 + 26 * n), 1600)

    def make_title(n):
        return (
            "Médailles de bronze par athlète (jeux d'été)"
            f"<br><sup>Le fichier ne contient que {year_value} : aucune évolution temporelle n'est observable ici. "
            f"Affichage des {fmt_int(n)} meilleurs athlètes sur {fmt_int(len(positive_df))} ayant au moins un bronze.</sup>"
        )

    initial = subset_for(default_n)
    max_bronze = max(1.0, float(positive_df["total_medailles_bronze_ete"].max()))

    fig = go.Figure(
        data=[
            go.Bar(
                x=initial["total_medailles_bronze_ete"].tolist(),
                y=initial["nom_athlete"].tolist(),
                orientation="h",
                customdata=initial[["annee"]].astype(int).values.tolist(),
                marker=dict(
                    color=initial["total_medailles_bronze_ete"].tolist(),
                    colorscale=[
                        [0.0, "#f5e6d7"],
                        [0.5, "#c98245"],
                        [1.0, "#7a4b2b"],
                    ],
                    cmin=0,
                    cmax=max_bronze,
                    colorbar=dict(title="Bronze"),
                    line=dict(color="white", width=0.7),
                ),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Année: %{customdata[0]}<br>"
                    "Médailles de bronze: %{x:.0f}<extra></extra>"
                ),
            )
        ]
    )

    buttons = []
    for n in view_sizes:
        subset = subset_for(n)
        buttons.append(
            dict(
                label=f"Top {n}" if n < len(positive_df) else "Tous",
                method="update",
                args=[
                    {
                        "x": [subset["total_medailles_bronze_ete"].tolist()],
                        "y": [subset["nom_athlete"].tolist()],
                        "customdata": [subset[["annee"]].astype(int).values.tolist()],
                        "marker.color": [subset["total_medailles_bronze_ete"].tolist()],
                    },
                    {
                        "title.text": make_title(n),
                        "height": chart_height(n),
                    },
                ],
            )
        )

    fig.update_layout(
        template="plotly_white",
        title=make_title(default_n),
        height=chart_height(default_n),
        margin=dict(l=80, r=80, t=120, b=90),
        xaxis=dict(
            title="Total de médailles de bronze",
            rangemode="tozero",
            tickmode="linear",
            dtick=1,
            gridcolor="#e6e6e6",
        ),
        yaxis=dict(
            title="Athlète",
            autorange="reversed",
            tickfont=dict(size=11),
        ),
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                x=1.0,
                y=1.16,
                xanchor="right",
                yanchor="top",
                showactive=True,
                buttons=buttons,
            )
        ],
        annotations=[
            dict(
                text=(
                    f"{fmt_int(len(positive_df))} athlètes ont au moins un bronze en {year_value}. "
                    f"{fmt_int(zero_athletes)} athlètes sur {fmt_int(total_athletes)} sont à 0."
                ),
                x=0,
                y=-0.16,
                xref="paper",
                yref="paper",
                showarrow=False,
                align="left",
                font=dict(size=12, color="#555555"),
            )
        ],
    )

    return fig


def build_multi_year_chart(df):
    positive_df = (
        df.loc[df["total_medailles_bronze_ete"] > 0, ["nom_athlete", "annee", "total_medailles_bronze_ete"]]
        .dropna(subset=["annee"])
        .copy()
    )

    if positive_df.empty:
        return create_empty_figure("Aucune médaille de bronze n'est présente dans le fichier.")

    athlete_totals = (
        positive_df.groupby("nom_athlete", as_index=False)["total_medailles_bronze_ete"]
        .sum()
        .sort_values(["total_medailles_bronze_ete", "nom_athlete"], ascending=[False, True])
    )

    top_n = min(15, athlete_totals["nom_athlete"].nunique())
    top_athletes = athlete_totals.head(top_n)["nom_athlete"].tolist()
    plot_df = positive_df.loc[positive_df["nom_athlete"].isin(top_athletes)].sort_values(
        ["nom_athlete", "annee"]
    )

    fig = go.Figure()
    palette = [
        "#7a4b2b",
        "#c98245",
        "#a35d2f",
        "#d9a066",
        "#8f6b4f",
        "#6f4e37",
        "#b87333",
        "#9c6a4a",
        "#c4915b",
        "#8c5a3c",
        "#c66b3d",
        "#a8795a",
        "#6e5844",
        "#b98662",
        "#8a4f30",
    ]

    for i, athlete in enumerate(top_athletes):
        athlete_df = plot_df.loc[plot_df["nom_athlete"] == athlete]
        fig.add_trace(
            go.Scatter(
                x=athlete_df["annee"].astype(int).tolist(),
                y=athlete_df["total_medailles_bronze_ete"].tolist(),
                mode="lines+markers",
                name=athlete,
                line=dict(width=2.5, color=palette[i % len(palette)]),
                marker=dict(size=7),
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Année: %{x}<br>"
                    "Médailles de bronze: %{y:.0f}<extra></extra>"
                ),
            )
        )

    year_min = int(plot_df["annee"].min())
    year_max = int(plot_df["annee"].max())

    fig.update_layout(
        template="plotly_white",
        title=(
            "Évolution des médailles de bronze (jeux d'été) par athlète"
            f"<br><sup>Affichage des {fmt_int(top_n)} athlètes ayant cumulé le plus de bronze entre {year_min} et {year_max}. "
            "Utilisez la légende pour isoler des athlètes.</sup>"
        ),
        height=800,
        margin=dict(l=80, r=40, t=120, b=80),
        xaxis=dict(
            title="Année",
            tickmode="linear",
            gridcolor="#e6e6e6",
        ),
        yaxis=dict(
            title="Total de médailles de bronze",
            rangemode="tozero",
            tickmode="linear",
            dtick=1,
            gridcolor="#e6e6e6",
        ),
        legend=dict(
            title="Athlète",
            orientation="v",
            x=1.02,
            y=1,
            xanchor="left",
            yanchor="top",
        ),
    )

    return fig


def main():
    df = load_data()
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)

    unique_years = sorted(df["annee"].dropna().astype(int).unique().tolist())

    if df.empty:
        fig = create_empty_figure("Le fichier CSV est vide.")
    elif len(unique_years) <= 1:
        fig = build_single_year_chart(df)
    else:
        fig = build_multi_year_chart(df)

    fig.write_html(
        str(OUTPUT_HTML),
        include_plotlyjs=True,
        full_html=True,
        config={"displaylogo": False, "responsive": True},
    )


if __name__ == "__main__":
    main()