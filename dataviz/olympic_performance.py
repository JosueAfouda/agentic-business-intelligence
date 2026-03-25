from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


INPUT_CSV = Path("outputs/olympic_performance/olympic_performance.csv")
OUTPUT_HTML = Path("outputs/olympic_performance/olympic_performance.html")


def format_country_name(name: str) -> str:
    small_words = {"and", "of", "the", "de", "du", "la", "le", "des", "et"}

    def format_token(token: str, is_first: bool) -> str:
        if not token:
            return token
        if "-" in token:
            return "-".join(format_token(part, is_first and idx == 0) for idx, part in enumerate(token.split("-")))
        lower = token.lower()
        if not is_first and lower in small_words:
            return lower
        return token[:1].upper() + token[1:].lower()

    parts = name.strip().split()
    return " ".join(format_token(part, i == 0) for i, part in enumerate(parts))


def parse_country(raw_value: str) -> tuple[str, str]:
    text = str(raw_value).strip()
    if " - " in text:
        code, country = text.split(" - ", 1)
        return code.strip().upper(), format_country_name(country.strip())
    return "", format_country_name(text)


def main() -> None:
    df = pd.read_csv(INPUT_CSV)
    df.columns = [col.strip() for col in df.columns]

    expected_columns = {"pays", "medailles_par_million_habitants"}
    missing = expected_columns.difference(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans le CSV : {sorted(missing)}")

    df = df[["pays", "medailles_par_million_habitants"]].copy()
    df["pays"] = df["pays"].astype(str).str.strip()
    df["medailles_par_million_habitants"] = pd.to_numeric(
        df["medailles_par_million_habitants"], errors="coerce"
    )
    df = df.dropna(subset=["medailles_par_million_habitants"])
    df = df.sort_values(
        by=["medailles_par_million_habitants", "pays"],
        ascending=[False, True],
        kind="mergesort",
    ).reset_index(drop=True)

    parsed = df["pays"].apply(parse_country)
    df["code_pays"] = parsed.str[0]
    df["nom_pays"] = parsed.str[1]
    df["rang"] = df.index + 1
    df["libelle"] = df["rang"].map(lambda x: f"{x:02d}") + ". " + df["nom_pays"]
    df["valeur_affichee"] = df["medailles_par_million_habitants"].map(lambda x: f"{x:.2f}")

    customdata = list(
        zip(
            df["rang"],
            df["nom_pays"],
            df["code_pays"].replace("", "N/A"),
            df["medailles_par_million_habitants"],
        )
    )

    fig = go.Figure(
        go.Bar(
            x=df["medailles_par_million_habitants"],
            y=df["libelle"],
            orientation="h",
            customdata=customdata,
            text=df["valeur_affichee"],
            textposition="outside",
            cliponaxis=False,
            marker=dict(
                color=df["medailles_par_million_habitants"],
                colorscale=[
                    [0.0, "#d8e6f3"],
                    [0.45, "#5b8db8"],
                    [1.0, "#0b3954"],
                ],
                colorbar=dict(title="Médailles<br>par million"),
                line=dict(color="#ffffff", width=0.8),
            ),
            hovertemplate=(
                "<b>Rang %{customdata[0]}</b><br>"
                "Pays : %{customdata[1]}<br>"
                "Code : %{customdata[2]}<br>"
                "Médailles par million d'habitants : %{customdata[3]:.4f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=(
            "Top 25 des pays les plus performants aux Jeux d'été"
            "<br><sup>Médailles olympiques rapportées à la population "
            "(médailles par million d'habitants)</sup>"
        ),
        template="plotly_white",
        height=950,
        width=1300,
        margin=dict(l=180, r=70, t=100, b=70),
        xaxis=dict(
            title="Médailles par million d'habitants",
            zeroline=False,
            showgrid=True,
            gridcolor="#d9e2ec",
            tickformat=".2f",
        ),
        yaxis=dict(
            title="Pays",
            autorange="reversed",
            categoryorder="array",
            categoryarray=df["libelle"].tolist(),
        ),
        font=dict(family="Arial, sans-serif", size=13, color="#1f2933"),
        hoverlabel=dict(bgcolor="white"),
    )

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(
        OUTPUT_HTML,
        include_plotlyjs="cdn",
        full_html=True,
        config={
            "responsive": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        },
    )


if __name__ == "__main__":
    main()