# Import de Path pour construire des chemins de fichiers propres et compatibles Windows/macOS/Linux
from pathlib import Path

# Import de time pour ajouter des pauses entre les requêtes Google Trends
import time

# Import de pandas pour manipuler et exporter les données tabulaires
import pandas as pd

# Import de TrendReq, l’objet principal de pytrends pour interroger Google Trends
from pytrends.request import TrendReq


# Liste des mots-clés à analyser dans Google Trends
KEYWORDS = [
    "intelligence artificielle",
    "crypto",
    "Netflix",
    "Tesla",
    "ChatGPT"
]

# Période utilisée pour récupérer l’évolution temporelle globale des recherches
TIMEFRAME = "2023-01-01 2026-01-01"

# Période utilisée pour récupérer les scores par pays.
# Elle est plus courte afin d’obtenir une image récente de la répartition géographique.
TIMEFRAME_COUNTRY = "2025-01-01 2026-01-01"

# Zone géographique.
# Une chaîne vide signifie que la recherche est effectuée au niveau mondial.
GEO = ""

# Langue et région utilisées pour les requêtes Google Trends
HL = "fr-FR"


# Définit le dossier racine du projet.
# __file__ représente le chemin du script actuel.
# .resolve() transforme ce chemin en chemin absolu.
# .parents[1] remonte de deux niveaux dans l’arborescence.
BASE_DIR = Path(__file__).resolve().parents[1]

# Dossier dans lequel les données brutes seront enregistrées
RAW_DIR = BASE_DIR / "data" / "raw"

# Crée le dossier raw s’il n’existe pas encore
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Chemin du fichier CSV qui contiendra les tendances temporelles
TIME_OUTPUT = RAW_DIR / "trends_time.csv"

# Chemin du fichier CSV qui contiendra les tendances par pays
COUNTRY_OUTPUT = RAW_DIR / "trends_country.csv"


def connect_trends():
    """
    Crée une connexion à Google Trends via pytrends.

    Paramètres utilisés :
    - hl=HL : langue/région de l’interface Google Trends
    - tz=360 : fuseau horaire exprimé en minutes.
      360 correspond à UTC+6.

    Retour :
    - un objet TrendReq prêt à envoyer des requêtes.
    """

    return TrendReq(hl=HL, tz=360)


def fetch_interest_over_time(pytrends, keywords):
    """
    Récupère l’évolution temporelle de l’intérêt de recherche
    pour une liste de mots-clés.

    Paramètres :
    - pytrends : connexion TrendReq déjà initialisée
    - keywords : liste de mots-clés à comparer

    Retour :
    - DataFrame contenant une colonne date et une colonne par mot-clé.
    """

    # Prépare la requête Google Trends avec plusieurs mots-clés.
    # cat=0 signifie toutes catégories.
    # timeframe définit la période étudiée.
    # geo="" signifie monde entier.
    # gprop="" signifie recherche Google classique.
    pytrends.build_payload(
        kw_list=keywords,
        cat=0,
        timeframe=TIMEFRAME,
        geo=GEO,
        gprop=""
    )

    # Récupère les séries temporelles d’intérêt de recherche.
    # Les valeurs sont normalisées par Google Trends entre 0 et 100.
    df_time = pytrends.interest_over_time()

    # Si Google Trends ne renvoie aucune donnée, on arrête clairement la fonction.
    if df_time.empty:
        raise ValueError("Aucune donnée temporelle récupérée.")

    # Google Trends ajoute parfois une colonne isPartial indiquant
    # si la dernière période est incomplète.
    # Elle n’est pas nécessaire pour l’analyse finale.
    if "isPartial" in df_time.columns:
        df_time = df_time.drop(columns=["isPartial"])

    # Transforme l’index temporel en colonne classique appelée généralement "date"
    df_time = df_time.reset_index()

    return df_time


def fetch_interest_by_country(pytrends, keywords):
    """
    Récupère l’intérêt de recherche par pays pour chaque mot-clé.

    Contrairement à interest_over_time, chaque mot-clé est interrogé séparément.
    Cela permet d’obtenir un tableau harmonisé avec trois colonnes principales :
    country, mot_cle, score.

    Paramètres :
    - pytrends : connexion TrendReq déjà initialisée
    - keywords : liste de mots-clés à traiter

    Retour :
    - DataFrame concaténé contenant les scores par pays et par mot-clé.
    """

    # Liste temporaire qui stockera les résultats de chaque mot-clé
    all_country_data = []

    # Boucle sur chaque mot-clé pour récupérer sa distribution géographique
    for keyword in keywords:
        print(f"Récupération des données pays pour : {keyword}")

        # Prépare une requête Google Trends pour un seul mot-clé.
        # L’usage d’un seul mot-clé évite de mélanger les échelles entre mots-clés.
        pytrends.build_payload(
            kw_list=[keyword],
            cat=0,
            timeframe=TIMEFRAME_COUNTRY,
            geo=GEO,
            gprop=""
        )

        # Récupère l’intérêt de recherche par région.
        # resolution="COUNTRY" impose une agrégation au niveau pays.
        # inc_low_vol=True inclut aussi les pays à faible volume de recherche.
        # inc_geo_code=False évite d’ajouter les codes géographiques Google.
        df_country = pytrends.interest_by_region(
            resolution="COUNTRY",
            inc_low_vol=True,
            inc_geo_code=False
        )

        # Si aucune donnée n’est renvoyée pour ce mot-clé,
        # on affiche un message et on passe au mot-clé suivant.
        if df_country.empty:
            print(f"Aucune donnée pour {keyword}")
            continue

        # Transforme l’index, qui contient généralement les pays,
        # en colonne standard du DataFrame.
        df_country = df_country.reset_index()

        # Récupère le nom de la première colonne.
        # Elle peut varier selon la réponse pytrends.
        first_col = df_country.columns[0]

        # Renomme cette première colonne en "country" pour standardiser le résultat
        df_country = df_country.rename(columns={first_col: "country"})

        # Vérifie que la colonne du mot-clé existe bien.
        # Si elle est absente, cela signifie que la réponse n’a pas le format attendu.
        if keyword not in df_country.columns:
            print(f"Colonne introuvable pour {keyword}")
            continue

        # Renomme la colonne du mot-clé en "score"
        # afin d’obtenir une structure commune pour tous les mots-clés.
        df_country = df_country.rename(columns={keyword: "score"})

        # Ajoute une colonne indiquant à quel mot-clé appartient chaque score
        df_country["mot_cle"] = keyword

        # Garde uniquement les colonnes utiles dans un ordre clair
        df_country = df_country[["country", "mot_cle", "score"]]

        # Ajoute le résultat de ce mot-clé à la liste globale
        all_country_data.append(df_country)

        # Pause de 3 secondes pour limiter le risque de blocage ou de rate limit
        time.sleep(3)

    # Si aucun mot-clé n’a produit de données exploitables, on lève une erreur explicite.
    if not all_country_data:
        raise ValueError("Aucune donnée géographique récupérée.")

    # Concatène tous les DataFrames pays/mot-clé en un seul tableau long
    final_df = pd.concat(all_country_data, ignore_index=True)

    return final_df


def save_csv(df, output_path):
    """
    Sauvegarde un DataFrame au format CSV.

    Paramètres :
    - df : DataFrame pandas à enregistrer
    - output_path : chemin complet du fichier de sortie
    """

    # index=False évite d’écrire l’index pandas dans le fichier.
    # encoding="utf-8" garantit une bonne gestion des accents.
    df.to_csv(output_path, index=False, encoding="utf-8")

    # Message de confirmation avec le chemin exact du fichier créé
    print(f"Fichier enregistré : {output_path}")


def main():
    """
    Fonction principale du script.

    Elle exécute toute la chaîne de collecte :
    1. connexion à Google Trends
    2. récupération des tendances temporelles
    3. sauvegarde du fichier trends_time.csv
    4. récupération des tendances par pays
    5. sauvegarde du fichier trends_country.csv
    6. affichage de contrôles rapides
    """

    try:
        # Initialise la connexion pytrends
        pytrends = connect_trends()

        # Récupère puis sauvegarde les données temporelles
        print("Récupération des données temporelles...")
        df_time = fetch_interest_over_time(pytrends, KEYWORDS)
        save_csv(df_time, TIME_OUTPUT)

        # Pause avant la collecte géographique pour réduire le risque de blocage
        time.sleep(3)

        # Récupère puis sauvegarde les données par pays
        print("Récupération des données par pays...")
        df_country = fetch_interest_by_country(pytrends, KEYWORDS)
        save_csv(df_country, COUNTRY_OUTPUT)

        # Messages de fin et aperçus rapides des données collectées
        print("\nCollecte terminée.")

        print("\nAperçu trends_time :")
        print(df_time.head())

        print("\nAperçu trends_country :")
        print(df_country.head())

    except Exception as e:
        # Capture toute erreur pendant la collecte.
        # Cela évite un crash non lisible et affiche un message simple.
        print("Erreur pendant la collecte :", e)


# Point d’entrée standard d’un script Python.
# Le main() ne s’exécute que si ce fichier est lancé directement,
# et non s’il est importé comme module dans un autre script.
if __name__ == "__main__":
    main()