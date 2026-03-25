import textwrap
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


INPUT_CSV = Path("outputs/events_winter/events_winter.csv")
OUTPUT_HTML = Path("outputs/events_winter/events_winter.html")


def wrap_label(value: str, width: int = 34) -> str:
    return "<br>".join(textwrap.wrap(str(value), width=width, break_long_words=False))


def build_empty_figure() -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text="No winter events with athletes over age 40 were found in the CSV.",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=18, color="#1F2937"),
    )
    fig.update_layout(
        title="Winter Events That Include Athletes Over Age 40",
        template="plotly_white",
        height=420,
        margin=dict(l=40, r=40, t=90, b=40),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def main():
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_CSV)

    if "winter_event" not in df.columns:
        raise ValueError("Expected a 'winter_event' column in the input CSV.")

    df = df[["winter_event"]].dropna()
    df["winter_event"] = df["winter_event"].astype(str).str.strip()
    df = df[df["winter_event"] != ""].drop_duplicates().sort_values("winter_event").reset_index(drop=True)

    if df.empty:
        fig = build_empty_figure()
        fig.write_html(OUTPUT_HTML, full_html=True, include_plotlyjs=True)
        return

    df["included"] = 1
    df["display_event"] = df["winter_event"].apply(wrap_label)

    fig = px.bar(
        df,
        x="included",
        y="display_event",
        orientation="h",
        custom_data=["winter_event"],
        color_discrete_sequence=["#2F6B8A"],
    )

    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>Status: Includes athletes over age 40<extra></extra>",
        marker_line_color="#1D4E67",
        marker_line_width=1,
        opacity=0.9,
    )

    fig.update_layout(
        title=(
            "Winter Events That Include Athletes Over Age 40"
            f"<br><sup>{len(df)} distinct winter events appear in the result set</sup>"
        ),
        template="plotly_white",
        height=max(430, 120 + len(df) * 70),
        margin=dict(l=220, r=80, t=95, b=60),
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=14, color="#1F2937"),
    )

    fig.update_xaxes(
        title="Query Result Status",
        range=[0, 1.12],
        tickmode="array",
        tickvals=[1],
        ticktext=["Included"],
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        title="Winter Event",
        autorange="reversed",
        showgrid=False,
    )

    fig.add_annotation(
        x=1.01,
        y=1.08,
        xref="paper",
        yref="paper",
        text=f"Total events: <b>{len(df)}</b>",
        showarrow=False,
        font=dict(size=13, color="#374151"),
        align="right",
    )

    fig.write_html(OUTPUT_HTML, full_html=True, include_plotlyjs=True)


if __name__ == "__main__":
    main()