import pandas as pd

# Lecture du fichier CSV
df = pd.read_csv("data/data.csv")

# Aperçu rapide
print(df.shape)
print(df.columns.tolist())
df.head(5)
