from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


INPUT_CSV = Path("outputs/top_ten_clients/top_ten_clients.csv")
OUTPUT_HTML = Path("outputs/top_ten_clients/top_ten_clients.html")


def main():
    df = pd.read_csv(INPUT_CSV)

    expected_columns = [
        "rang_client_rentabilite",
        "client_id",
        "client_nom_complet",
        "chiffre_affaires_client",
        "categorie_film_principale",
        "chiffre_affaires_categorie",
    ]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Colonnes manquantes dans le CSV : {missing_columns}")

    numeric_columns = [
        "rang_client_rentabilite",
        "client_id",
        "chiffre_affaires_client",
        "chiffre_affaires_categorie",
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[numeric_columns].isna().any().any():
        raise ValueError("Le fichier CSV contient des valeurs numeriques invalides.")

    df["client_nom_complet"] = df["client_nom_complet"].astype(str).str.strip()
    df["categorie_film_principale"] = (
        df["categorie_film_principale"].astype(str).str.strip().replace({"": "Non renseignee"})
    )
    df["part_categorie_principale"] = (
        df["chiffre_affaires_categorie"] / df["chiffre_affaires_client"]
    )
    df = df.sort_values(
        ["rang_client_rentabilite", "chiffre_affaires_client"],
        ascending=[True, False],
        kind="mergesort",
    ).copy()
    df["client_label"] = df["rang_client_rentabilite"].astype(int).astype(str) + ". " + df["client_nom_complet"]

    categories = list(dict.fromkeys(df["categorie_film_principale"].tolist()))
    palette = [
        "#0F766E",
        "#2563EB",
        "#D97706",
        "#DC2626",
        "#7C3AED",
        "#059669",
        "#B45309",
        "#BE185D",
        "#1D4ED8",
        "#4F46E5",
    ]
    color_map = {category: palette[i % len(palette)] for i, category in enumerate(categories)}

    fig = go.Figure()

    total_customdata = df[
        ["categorie_film_principale", "chiffre_affaires_categorie", "part_categorie_principale"]
    ].to_numpy()

    fig.add_trace(
        go.Bar(
            x=df["chiffre_affaires_client"],
            y=df["client_label"],
            orientation="h",
            name="CA total du client",
            marker=dict(
                color="rgba(100, 116, 139, 0.28)",
                line=dict(color="rgba(71, 85, 105, 0.55)", width=1),
            ),
            customdata=total_customdata,
            text=df["chiffre_affaires_client"].map(lambda v: f"{v:.2f}"),
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Chiffre d'affaires total : %{x:.2f}<br>"
                "Categorie principale : %{customdata[0]}<br>"
                "CA de la categorie principale : %{customdata[1]:.2f}<br>"
                "Part de la categorie principale : %{customdata[2]:.1%}"
                "<extra></extra>"
            ),
        )
    )

    for category in categories:
        subset = df[df["categorie_film_principale"] == category].copy()
        subset_customdata = subset[
            ["categorie_film_principale", "chiffre_affaires_client", "part_categorie_principale"]
        ].to_numpy()

        fig.add_trace(
            go.Bar(
                x=subset["chiffre_affaires_categorie"],
                y=subset["client_label"],
                orientation="h",
                name=category,
                marker=dict(color=color_map[category]),
                customdata=subset_customdata,
                text=subset["part_categorie_principale"].map(lambda v: f"{v:.0%}"),
                textposition="inside",
                insidetextanchor="middle",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Categorie principale : %{customdata[0]}<br>"
                    "CA de la categorie : %{x:.2f}<br>"
                    "Chiffre d'affaires total : %{customdata[1]:.2f}<br>"
                    "Part de la categorie principale : %{customdata[2]:.1%}"
                    "<extra></extra>"
                ),
            )
        )

    max_total = df["chiffre_affaires_client"].max()
    top_client = df.iloc[0]

    fig.update_layout(
        title=dict(
            text=(
                "Top 10 des clients les plus rentables et contribution de leur categorie principale"
                "<br><sup>Barre grisee : chiffre d'affaires total du client | "
                "Barre coloree : chiffre d'affaires genere par la categorie de films la plus contributrice</sup>"
            ),
            x=0.5,
        ),
        template="plotly_white",
        barmode="overlay",
        hovermode="y unified",
        height=720,
        margin=dict(l=230, r=50, t=120, b=70),
        bargap=0.34,
        legend=dict(
            title="Categorie principale",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        uniformtext_minsize=10,
        uniformtext_mode="hide",
    )

    fig.update_xaxes(
        title="Chiffre d'affaires",
        range=[0, max_total * 1.18],
        gridcolor="rgba(15, 23, 42, 0.08)",
        zeroline=False,
    )
    fig.update_yaxes(title="", autorange="reversed")

    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0,
        y=1.12,
        showarrow=False,
        align="left",
        text=(
            f"Client le plus rentable : <b>{top_client['client_nom_complet']}</b> "
            f"({top_client['chiffre_affaires_client']:.2f} de CA) | "
            f"Categorie principale : <b>{top_client['categorie_film_principale']}</b> "
            f"({top_client['chiffre_affaires_categorie']:.2f}, "
            f"{top_client['part_categorie_principale']:.1%} du total)"
        ),
        font=dict(size=12, color="#334155"),
    )

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(OUTPUT_HTML), include_plotlyjs=True, full_html=True)


if __name__ == "__main__":
    main()