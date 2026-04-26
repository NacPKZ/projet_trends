# Import de Path pour gérer les chemins de fichiers de manière propre et portable
from pathlib import Path

# Pandas sert à lire, nettoyer, transformer et agréger les données tabulaires
import pandas as pd

# NumPy est importé pour les calculs numériques.
# Dans ce script, il n’est pas utilisé directement.
import numpy as np

# Plotly Express permet de créer rapidement des graphiques interactifs ou exportables
import plotly.express as px

# Plotly Graph Objects permet de créer des figures plus personnalisées
import plotly.graph_objects as go

# Matplotlib est utilisé ici uniquement pour sauvegarder/fermer d’éventuelles figures académiques
import matplotlib.pyplot as plt


# =========================================================
# PATHS
# =========================================================

# Définit le dossier racine du projet.
# __file__ correspond au chemin du script actuel.
# .resolve() transforme ce chemin en chemin absolu.
# .parents[1] remonte de deux niveaux dans l’arborescence.
BASE_DIR = Path(__file__).resolve().parents[1]

# Dossier contenant les fichiers de données déjà nettoyés ou préparés
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Dossier principal où seront stockées les sorties du script
OUTPUT_DIR = BASE_DIR / "outputs"

# Dossier spécifique pour les figures Plotly avec style sombre premium
PLOTLY_DIR = OUTPUT_DIR / "figures_premium_dark"

# Dossier prévu pour des figures Matplotlib au style académique
MPL_DIR = OUTPUT_DIR / "figures_academic"

# Crée les dossiers de sortie s’ils n’existent pas déjà.
# parents=True permet de créer aussi les dossiers parents manquants.
# exist_ok=True évite une erreur si le dossier existe déjà.
PLOTLY_DIR.mkdir(parents=True, exist_ok=True)
MPL_DIR.mkdir(parents=True, exist_ok=True)

# Chemin vers le fichier contenant les tendances temporelles au format long
TIME_FILE = PROCESSED_DIR / "trends_time_long.csv"

# Chemin vers le fichier contenant les scores par pays enrichis avec continent et code ISO
COUNTRY_FILE = PROCESSED_DIR / "trends_country_enriched.csv"

# Chemin vers le fichier contenant les insights par pays :
# mot-clé dominant, score maximum, deuxième score, écart, etc.
INSIGHTS_FILE = PROCESSED_DIR / "country_insights.csv"


# =========================================================
# LOAD
# =========================================================

# Charge les données temporelles dans un DataFrame pandas
df_time = pd.read_csv(TIME_FILE)

# Charge les données pays enrichies dans un DataFrame pandas
df_country = pd.read_csv(COUNTRY_FILE)

# Charge les données d’insights pays dans un DataFrame pandas
df_insights = pd.read_csv(INSIGHTS_FILE)


# =========================================================
# CLEAN
# =========================================================

# Convertit la colonne date en vrai type datetime.
# errors="coerce" transforme les dates invalides en NaT.
df_time["date"] = pd.to_datetime(df_time["date"], errors="coerce")

# Convertit les scores en valeurs numériques.
# Les valeurs invalides deviennent NaN, puis sont remplacées par 0.
df_time["score"] = pd.to_numeric(df_time["score"], errors="coerce").fillna(0)

# Nettoyage équivalent pour les scores par pays
df_country["score"] = pd.to_numeric(df_country["score"], errors="coerce").fillna(0)

# Remplace les continents manquants par "Inconnu"
df_country["continent"] = df_country["continent"].fillna("Inconnu")

# Remplace les codes ISO manquants par une chaîne vide
df_country["iso3"] = df_country["iso3"].fillna("")

# Nettoie les colonnes numériques du fichier d’insights
df_insights["score_max"] = pd.to_numeric(df_insights["score_max"], errors="coerce").fillna(0)
df_insights["score_2eme"] = pd.to_numeric(df_insights["score_2eme"], errors="coerce").fillna(0)
df_insights["ecart_top2"] = pd.to_numeric(df_insights["ecart_top2"], errors="coerce").fillna(0)

# Nettoie les colonnes catégorielles du fichier d’insights
df_insights["continent"] = df_insights["continent"].fillna("Inconnu")
df_insights["iso3"] = df_insights["iso3"].fillna("")
df_insights["country"] = df_insights["country"].fillna("Unknown")


# =========================================================
# STYLE
# =========================================================

# Dictionnaire associant chaque mot-clé à une couleur fixe.
# Cela permet de garder une identité visuelle cohérente entre les graphiques.
COLORS = {
    "ChatGPT": "#60A5FA",
    "crypto": "#F87171",
    "Netflix": "#34D399",
    "Tesla": "#A78BFA",
    "intelligence artificielle": "#FB923C"
}

# Dimensions des images exportées, adaptées à un format de slide 16:9
SLIDE_W = 1600
SLIDE_H = 900

# Couleurs principales du thème sombre
DARK_BG = "#0B1020"
CARD_BG = "#121A2B"
GRID = "#263042"
FONT = "#E5E7EB"


def apply_plotly_dark(fig, title, x_title="", y_title=""):
    """
    Applique un style sombre cohérent à une figure Plotly.

    Paramètres :
    - fig : figure Plotly à modifier
    - title : titre du graphique
    - x_title : titre de l’axe X
    - y_title : titre de l’axe Y

    Retour :
    - la figure Plotly modifiée
    """

    fig.update_layout(
        title=title,
        title_font_size=26,
        font=dict(size=15, color=FONT, family="Arial"),
        paper_bgcolor=DARK_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=70, r=70, t=90, b=70),
        xaxis_title=x_title,
        yaxis_title=y_title,
        hoverlabel=dict(
            bgcolor="#111827",
            font_size=13,
            font_color="white"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=FONT)
        )
    )

    # Active une grille discrète sur les axes et supprime la ligne zéro
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)

    return fig


def safe_save_plotly(fig, filename):
    """
    Sauvegarde une figure Plotly en image PNG.

    La fonction est protégée par try/except afin que le script continue
    même si une exportation échoue.

    Attention :
    fig.write_image nécessite généralement le package kaleido.
    """

    out = PLOTLY_DIR / filename

    try:
        fig.write_image(str(out), width=SLIDE_W, height=SLIDE_H, scale=2)
        print(f"[OK] {filename}")
    except Exception as e:
        print(f"[ERREUR] {filename} -> {e}")


def safe_save_mpl(fig, filename):
    """
    Sauvegarde une figure Matplotlib.

    Cette fonction n’est pas utilisée dans les figures actuelles,
    mais elle est prête pour de futures visualisations académiques.
    """

    out = MPL_DIR / filename

    try:
        fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
        print(f"[OK] {filename}")
    except Exception as e:
        print(f"[ERREUR] {filename} -> {e}")
    finally:
        # Ferme systématiquement la figure pour libérer la mémoire
        plt.close(fig)


# =========================================================
# PREP TIME
# =========================================================

# Trie les données par mot-clé puis par date.
# Cela garantit que le calcul de moyenne mobile se fait dans le bon ordre temporel.
df_line = df_time.sort_values(["mot_cle", "date"]).copy()

# Calcule un score lissé avec une moyenne mobile de 6 périodes.
# groupby("mot_cle") applique le calcul séparément pour chaque mot-clé.
# min_periods=1 permet de calculer une moyenne même au début de la série.
df_line["score_lisse"] = (
    df_line.groupby("mot_cle")["score"]
    .transform(lambda s: s.rolling(window=6, min_periods=1).mean())
)


# =========================================================
# FIGURE 1 - LINE
# =========================================================

try:
    # Crée un graphique en lignes montrant l’évolution du score lissé dans le temps
    fig1 = px.line(
        df_line,
        x="date",
        y="score_lisse",
        color="mot_cle",
        color_discrete_map=COLORS
    )

    # Épaissit les lignes pour un rendu plus lisible
    fig1.update_traces(line=dict(width=4))

    # Applique le thème sombre défini plus haut
    fig1 = apply_plotly_dark(fig1, "Search Momentum", "Date", "Smoothed score")

    # Affiche un tooltip commun à toutes les séries au même point temporel
    fig1.update_layout(hovermode="x unified")

    # Récupère le dernier point disponible pour chaque mot-clé.
    # Ces points serviront à placer des labels directement à droite des courbes.
    last_points = (
        df_line.sort_values("date")
        .groupby("mot_cle", as_index=False)
        .tail(1)
    )

    # Ajoute une annotation à la fin de chaque courbe
    for _, row in last_points.iterrows():
        fig1.add_annotation(
            x=row["date"],
            y=row["score_lisse"],
            text=row["mot_cle"],
            showarrow=False,
            xshift=10,
            font=dict(size=12, color=COLORS.get(row["mot_cle"], FONT))
        )

    # Sauvegarde la figure
    safe_save_plotly(fig1, "01_search_momentum_dark.png")

except Exception as e:
    print(f"[ERREUR FIG1] {e}")


# =========================================================
# FIGURE 2 - HEATMAP
# =========================================================

try:
    # Copie les données temporelles pour préparer une agrégation mensuelle
    df_heat = df_time.copy()

    # Convertit chaque date en période mensuelle au format YYYY-MM
    df_heat["year_month"] = df_heat["date"].dt.to_period("M").astype(str)

    # Calcule le score moyen par mot-clé et par mois
    df_heat = df_heat.groupby(["mot_cle", "year_month"], as_index=False)["score"].mean()

    # Transforme les données en matrice :
    # lignes = mots-clés
    # colonnes = mois
    # valeurs = score moyen
    heat_pivot = df_heat.pivot(index="mot_cle", columns="year_month", values="score").fillna(0)

    # Crée une heatmap Plotly à partir de la matrice
    fig2 = go.Figure(
        data=go.Heatmap(
            z=heat_pivot.values,
            x=heat_pivot.columns,
            y=heat_pivot.index,
            colorscale="YlOrRd"
        )
    )

    # Applique le style sombre
    fig2 = apply_plotly_dark(fig2, "Monthly Heatmap", "Month", "Keyword")

    # Incline les labels de l’axe X pour éviter les chevauchements
    fig2.update_xaxes(tickangle=-45)

    # Sauvegarde la figure
    safe_save_plotly(fig2, "02_monthly_heatmap_dark.png")

except Exception as e:
    print(f"[ERREUR FIG2] {e}")


# =========================================================
# FIGURE 3 - MAP
# =========================================================

try:
    # Garde uniquement les lignes avec un code ISO3 valide.
    # Les choroplèthes Plotly ont besoin de codes pays à trois lettres.
    df_map = df_insights[df_insights["iso3"].str.len() == 3].copy()

    # Crée une carte mondiale où chaque pays est coloré selon son mot-clé dominant
    fig3 = px.choropleth(
        df_map,
        locations="iso3",
        color="mot_cle_dominant",
        hover_name="country",
        hover_data=["score_max", "score_2eme", "ecart_top2"],
        color_discrete_map=COLORS,
        projection="natural earth"
    )

    # Applique le style sombre global
    fig3 = apply_plotly_dark(fig3, "World Leaders")

    # Personnalise le rendu géographique de la carte
    fig3.update_layout(
        geo=dict(
            bgcolor=DARK_BG,
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#475569",
            showcountries=True,
            countrycolor="#334155"
        )
    )

    # Sauvegarde la carte
    safe_save_plotly(fig3, "03_world_leaders_dark.png")

except Exception as e:
    print(f"[ERREUR FIG3] {e}")


# =========================================================
# FIGURE 4 - SCATTER
# =========================================================

try:
    # Crée un nuage de points comparant :
    # - la popularité absolue du mot-clé dominant
    # - son avance sur le deuxième mot-clé
    fig4 = px.scatter(
        df_insights,
        x="score_max",
        y="ecart_top2",
        color="mot_cle_dominant",
        hover_name="country",
        size="score_max",
        size_max=26,
        color_discrete_map=COLORS
    )

    # Applique le style sombre
    fig4 = apply_plotly_dark(fig4, "Popularity vs Dominance", "Top score", "Gap vs second")

    # Ajoute un contour blanc autour des points et une légère transparence
    fig4.update_traces(marker=dict(line=dict(width=1, color="white"), opacity=0.82))

    # Sauvegarde le graphique
    safe_save_plotly(fig4, "04_popularity_vs_dominance_dark.png")

except Exception as e:
    print(f"[ERREUR FIG4] {e}")


# =========================================================
# FIGURE 5 - CONTINENT LEADERS
# =========================================================

try:
    # Calcule le score moyen de chaque mot-clé dans chaque continent
    df_cont = (
        df_country.groupby(["continent", "mot_cle"], as_index=False)["score"]
        .mean()
    )

    # Pour chaque continent, identifie l’index de la ligne ayant le score le plus élevé
    idx = df_cont.groupby("continent")["score"].idxmax()

    # Extrait les leaders continentaux et trie les résultats pour un graphique horizontal lisible
    df_cont_leaders = df_cont.loc[idx].copy().sort_values("score", ascending=True)

    # Crée un graphique en barres horizontales
    fig5 = px.bar(
        df_cont_leaders,
        x="score",
        y="continent",
        orientation="h",
        text="score",
        color="mot_cle",
        color_discrete_map=COLORS
    )

    # Applique le style sombre
    fig5 = apply_plotly_dark(fig5, "Continental Leaders", "Average score", "Continent")

    # Affiche les scores sur les barres avec une décimale
    fig5.update_traces(texttemplate="%{text:.1f}", textposition="outside")

    # Sauvegarde la figure
    safe_save_plotly(fig5, "05_continental_leaders_dark.png")

except Exception as e:
    print(f"[ERREUR FIG5] {e}")


# Message final indiquant que le script a terminé son exécution
print("\nTerminé.")