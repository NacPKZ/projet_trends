# Import de pandas pour lire, transformer et sauvegarder des fichiers CSV
import pandas as pd

# Import de Path pour gérer proprement les chemins de fichiers
from pathlib import Path

# Import du module unicodedata pour supprimer les accents et normaliser les textes
import unicodedata


# Définit le dossier racine du projet
BASE_DIR = Path(__file__).resolve().parents[1]

# Dossier contenant les données brutes issues de la collecte pytrends
RAW_DIR = BASE_DIR / "data" / "raw"

# Dossier contenant les fichiers nettoyés et transformés
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Dossier contenant les fichiers externes, ici les métadonnées pays issues de Kaggle
KAGGLE_DIR = BASE_DIR / "data" / "kaggle"

# Crée le dossier processed s’il n’existe pas déjà
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# FONCTION DE NORMALISATION
# =========================

def normalize_text(text):
    """
    Normalise une chaîne de caractères pour faciliter les jointures.

    Étapes :
    - conversion en chaîne de caractères
    - suppression des espaces au début et à la fin
    - passage en minuscules
    - suppression des accents
    - remplacement des espaces multiples par un seul espace

    Exemple :
    "  États-Unis  " devient "etats-unis".
    """

    text = str(text).strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = " ".join(text.split())

    return text


# =========================
# 1. TIME SERIES
# =========================

# Chemin du fichier brut contenant les tendances temporelles.
# Ce fichier est généralement au format large :
# une colonne date + une colonne par mot-clé.
time_input = RAW_DIR / "trends_time.csv"

# Chemin du fichier transformé au format long.
# Le format long est plus pratique pour Plotly, seaborn ou les groupby pandas.
time_output = PROCESSED_DIR / "trends_time_long.csv"

# Lecture du fichier brut des tendances temporelles
df_time = pd.read_csv(time_input)

# Transformation du format large vers le format long.
# id_vars=["date"] signifie que la colonne date reste inchangée.
# Toutes les autres colonnes deviennent des lignes dans "mot_cle" et "score".
df_time_long = df_time.melt(
    id_vars=["date"],
    var_name="mot_cle",
    value_name="score"
)

# Sauvegarde des tendances temporelles transformées
df_time_long.to_csv(time_output, index=False)

# Message de confirmation
print("trends_time_long.csv créé")


# =========================
# 2. COUNTRY DATA
# =========================

# Chemin du fichier brut contenant les scores par pays et par mot-clé
country_input = RAW_DIR / "trends_country.csv"

# Chemin du fichier intermédiaire nettoyé au format long
country_output = PROCESSED_DIR / "trends_country_long.csv"

# Lecture du fichier pays brut
df_country_long = pd.read_csv(country_input)

# Standardise les noms de colonnes :
# suppression des espaces et passage en minuscules.
df_country_long.columns = [c.strip().lower() for c in df_country_long.columns]

# Nettoie la colonne country en supprimant les espaces inutiles
df_country_long["country"] = df_country_long["country"].astype(str).str.strip()

# Nettoie la colonne mot_cle en supprimant les espaces inutiles
df_country_long["mot_cle"] = df_country_long["mot_cle"].astype(str).str.strip()

# Convertit le score en numérique.
# Les valeurs invalides deviennent NaN puis sont remplacées par 0.
df_country_long["score"] = pd.to_numeric(
    df_country_long["score"],
    errors="coerce"
).fillna(0)


# Dictionnaire de correspondance entre les noms de pays français normalisés
# et les noms de pays anglais utilisés dans le fichier de métadonnées Kaggle.
mapping_fr_to_en = {
    "afghanistan": "afghanistan",
    "afrique du sud": "south africa",
    "albanie": "albania",
    "algerie": "algeria",
    "allemagne": "germany",
    "arabie saoudite": "saudi arabia",
    "argentine": "argentina",
    "armenie": "armenia",
    "australie": "australia",
    "autriche": "austria",
    "belgique": "belgium",
    "bielorussie": "belarus",
    "bolivie": "bolivia",
    "bresil": "brazil",
    "bulgarie": "bulgaria",
    "cambodge": "cambodia",
    "cameroun": "cameroon",
    "canada": "canada",
    "chili": "chile",
    "chine": "china",
    "colombie": "colombia",
    "coree du sud": "south korea",
    "croatie": "croatia",
    "danemark": "denmark",
    "egypte": "egypt",
    "emirats arabes unis": "united arab emirates",
    "espagne": "spain",
    "estonie": "estonia",
    "etats-unis": "united states",
    "finlande": "finland",
    "france": "france",
    "grece": "greece",
    "hongrie": "hungary",
    "inde": "india",
    "indonesie": "indonesia",
    "irlande": "ireland",
    "islande": "iceland",
    "israel": "israel",
    "italie": "italy",
    "japon": "japan",
    "kazakhstan": "kazakhstan",
    "kenya": "kenya",
    "luxembourg": "luxembourg",
    "malaisie": "malaysia",
    "maroc": "morocco",
    "mexique": "mexico",
    "nigeria": "nigeria",
    "norvege": "norway",
    "nouvelle-zelande": "new zealand",
    "pakistan": "pakistan",
    "pays-bas": "netherlands",
    "perou": "peru",
    "philippines": "philippines",
    "pologne": "poland",
    "portugal": "portugal",
    "qatar": "qatar",
    "roumanie": "romania",
    "royaume-uni": "united kingdom",
    "russie": "russia",
    "singapour": "singapore",
    "slovaquie": "slovakia",
    "slovenie": "slovenia",
    "suede": "sweden",
    "suisse": "switzerland",
    "taiwan": "taiwan",
    "tchequie": "czechia",
    "thailande": "thailand",
    "tunisie": "tunisia",
    "turquie": "turkey",
    "ukraine": "ukraine",
    "vietnam": "vietnam"
}

# Crée une version normalisée du nom de pays provenant de Google Trends.
# Cette colonne sert de clé de jointure.
df_country_long["country_clean"] = df_country_long["country"].apply(normalize_text)

# Remplace les noms français normalisés par leur équivalent anglais.
# Objectif : les faire correspondre aux noms présents dans country_metadata.csv.
df_country_long["country_clean"] = df_country_long["country_clean"].replace(mapping_fr_to_en)

# Sauvegarde le fichier pays nettoyé avant enrichissement
df_country_long.to_csv(country_output, index=False)

# Message de confirmation
print("trends_country_long.csv créé")


# =========================
# 3. METADATA
# =========================

# Chemin du fichier contenant les métadonnées pays :
# pays, code ISO3, continent, etc.
metadata_input = KAGGLE_DIR / "country_metadata.csv"

# Chemin du fichier final enrichi avec iso3 et continent
output_enriched = PROCESSED_DIR / "trends_country_enriched.csv"

# Lecture du fichier de métadonnées
df_meta = pd.read_csv(metadata_input)

# Standardise les noms de colonnes du fichier de métadonnées
df_meta.columns = [c.strip().lower() for c in df_meta.columns]

# Nettoie la colonne country du fichier de métadonnées
df_meta["country"] = df_meta["country"].astype(str).str.strip()

# Crée une clé normalisée côté métadonnées
df_meta["country_clean"] = df_meta["country"].apply(normalize_text)


# =========================
# 4. MERGE SUR country_clean
# =========================

# Joint les données Google Trends nettoyées avec les métadonnées pays.
# La jointure se fait sur country_clean, la version normalisée du nom de pays.
# how="left" conserve toutes les lignes Google Trends, même si aucun pays
# correspondant n’est trouvé dans les métadonnées.
df_enriched = df_country_long.merge(
    df_meta[["country_clean", "iso3", "continent"]],
    on="country_clean",
    how="left"
)

# Sauvegarde du fichier final enrichi
df_enriched.to_csv(output_enriched, index=False)


# Affiche un aperçu du fichier enrichi
print("\ntrends_country_enriched.csv créé")
print(df_enriched.head(20))

# Affiche le nombre de valeurs manquantes sur les colonnes d’enrichissement
print("\nValeurs manquantes :")
print(df_enriched[["iso3", "continent"]].isna().sum())


# =========================
# 5. PAYS NON MATCHÉS
# =========================

# Identifie les pays pour lesquels la jointure avec les métadonnées a échoué.
# Un pays est considéré comme non matché si iso3 est manquant.
unmatched = (
    df_enriched[df_enriched["iso3"].isna()]["country"]
    .drop_duplicates()
    .sort_values()
)

# Affiche les 50 premiers pays non matchés pour faciliter le diagnostic
print("\nPays non matchés (aperçu) :")
print(unmatched.head(50).to_list())

# Affiche le nombre total de pays non matchés
print(f"\nNombre de pays non matchés : {unmatched.shape[0]}")