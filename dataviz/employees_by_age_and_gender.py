import pandas as pd
import plotly.express as px

def main():
    # Define file paths based on the context
    csv_path = "outputs/employees_by_age_and_gender/employees_by_age_and_gender.csv"
    output_html_path = "outputs/employees_by_age_and_gender/employees_by_age_and_gender.html"

    # Load the resulting dataset
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return

    # Logical ordering for the age groups to ensure a readable distribution
    age_order = ["<20", "20-29", "30-39", "40-49", "50+"]

    # Create a grouped bar chart which is the most appropriate for comparing 
    # counts across categories (Age Groups) subdivided by another category (Gender)
    fig = px.bar(
        df,
        x="groupe_age",
        y="nombre_total_employes",
        color="genre",
        barmode="group",
        category_orders={"groupe_age": age_order},
        title="<b>Répartition des Employés par Tranche d'Âge et Genre</b><br><sup>Nombre total d'employés par groupe d'âge et sexe</sup>",
        labels={
            "groupe_age": "Tranche d'âge",
            "nombre_total_employes": "Nombre d'employés",
            "genre": "Genre"
        },
        text_auto='.0f',
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Prism
    )

    # Improve visual quality and interactivity
    fig.update_layout(
        hovermode="x unified",
        xaxis={'categoryorder': 'array', 'categoryarray': age_order},
        yaxis_title="Nombre d'Employés",
        xaxis_title="Tranche d'Âge",
        legend_title_text="Genre",
        margin=dict(l=40, r=40, t=80, b=40)
    )

    # Enhance hover tooltips
    fig.update_traces(
        hovertemplate="<b>Genre:</b> %{fullData.name}<br><b>Tranche:</b> %{x}<br><b>Nombre:</b> %{y}<extra></extra>"
    )

    # Save the interactive visualization as HTML
    fig.write_html(output_html_path)

if __name__ == "__main__":
    main()