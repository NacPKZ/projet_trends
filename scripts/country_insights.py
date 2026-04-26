# Import de pandas pour manipuler les données sous forme de DataFrame
import pandas as pd

# Import de Path pour gérer les chemins de fichiers de façon portable
from pathlib import Path


# Définit le dossier racine du projet.
# __file__ correspond au fichier Python en cours d’exécution.
# .resolve() transforme le chemin en chemin absolu.
# .parents[1] remonte de deux niveaux dans l’arborescence.
BASE_DIR = Path(__file__).resolve().parents[1]

# Définit le dossier contenant les fichiers de données préparés
PROCESSED_DIR = BASE_DIR / "data" / "processed"


# Chemin du fichier d’entrée :
# il contient les scores de recherche par pays, enrichis avec iso3 et continent
inp = PROCESSED_DIR / "trends_country_enriched.csv"

# Chemin du fichier de sortie :
# il contiendra, pour chaque pays, le mot-clé dominant et l’écart avec le deuxième
out = PROCESSED_DIR / "country_insights.csv"


# Lecture du fichier CSV source dans un DataFrame pandas
df = pd.read_csv(inp)


# =========================================================
# SÉLECTION DES COLONNES UTILES
# =========================================================

# Liste des colonnes nécessaires pour calculer les insights par pays
cols = ["country", "iso3", "continent", "mot_cle", "score"]

# Garde uniquement ces colonnes.
# .copy() évite les effets de bord ou avertissements pandas lors des modifications suivantes.
df = df[cols].copy()


# =========================================================
# NETTOYAGE DES TYPES
# =========================================================

# Convertit la colonne score en numérique.
# Les valeurs non convertibles deviennent NaN grâce à errors="coerce".
# Les NaN sont ensuite remplacés par 0 afin de garantir des calculs sans erreur.
df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)


# =========================================================
# CLASSEMENT DES MOTS-CLÉS PAR PAYS
# =========================================================

# Trie les lignes par pays puis par score décroissant.
# Pour chaque pays, les mots-clés les plus forts apparaissent donc en premier.
df = df.sort_values(["country", "score"], ascending=[True, False])

# Calcule le rang de chaque mot-clé à l’intérieur de chaque pays.
# Le meilleur score reçoit le rang 1, le deuxième le rang 2, etc.
# method="first" signifie qu’en cas d’égalité, l’ordre actuel du DataFrame est utilisé.
df["rank"] = df.groupby("country")["score"].rank(method="first", ascending=False)


# =========================================================
# EXTRACTION DU TOP 1
# =========================================================

# Sélectionne, pour chaque pays, la ligne correspondant au mot-clé le mieux classé
top1 = df[df["rank"] == 1].copy()

# Renomme les colonnes pour rendre le résultat final plus explicite :
# - mot_cle devient mot_cle_dominant
# - score devient score_max
top1 = top1.rename(columns={
    "mot_cle": "mot_cle_dominant",
    "score": "score_max"
})


# =========================================================
# EXTRACTION DU TOP 2
# =========================================================

# Sélectionne, pour chaque pays, la ligne correspondant au deuxième meilleur score.
# On ne garde que country et score, car les autres informations viennent déjà du top 1.
top2 = df[df["rank"] == 2][["country", "score"]].copy()

# Renomme le score du deuxième mot-clé pour clarifier son rôle
top2 = top2.rename(columns={"score": "score_2eme"})


# =========================================================
# FUSION TOP 1 + TOP 2
# =========================================================

# Fusionne les informations du meilleur mot-clé avec celles du deuxième.
# how="left" garantit que tous les pays présents dans top1 restent dans le résultat,
# même si aucun deuxième mot-clé n’existe pour certains pays.
res = top1.merge(top2, on="country", how="left")


# =========================================================
# CALCUL DE L’ÉCART DE DOMINANCE
# =========================================================

# Si un pays n’a pas de deuxième mot-clé, le score_2eme est manquant.
# Il est remplacé par 0 pour permettre le calcul de l’écart.
res["score_2eme"] = res["score_2eme"].fillna(0)

# Calcule l’écart entre le meilleur score et le deuxième meilleur score.
# Plus cet écart est élevé, plus le mot-clé dominant domine nettement dans le pays.
res["ecart_top2"] = res["score_max"] - res["score_2eme"]


# =========================================================
# ORGANISATION DES COLONNES FINALES
# =========================================================

# Réordonne les colonnes pour produire un fichier clair et directement exploitable.
res = res[
    ["country", "iso3", "continent",
     "mot_cle_dominant", "score_max", "score_2eme", "ecart_top2"]
]


# =========================================================
# EXPORT DU FICHIER
# =========================================================

# Enregistre le résultat final au format CSV.
# index=False évite d’ajouter l’index pandas comme colonne supplémentaire.
res.to_csv(out, index=False)


# =========================================================
# AFFICHAGE DE CONTRÔLE
# =========================================================

# Confirme la création du fichier
print("country_insights.csv créé")

# Affiche les 10 premières lignes pour vérifier rapidement la structure du résultat
print(res.head(10))

# Affiche le nombre de pays uniques traités
print("\nNb pays :", res["country"].nunique())

# Affiche le nombre de pays dominés par chaque mot-clé
print("\nDominance :")
print(res["mot_cle_dominant"].value_counts())