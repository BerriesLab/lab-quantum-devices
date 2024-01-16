import pandas as pd

# import database
df = pd.read_csv("/Users/berri/Medical Imaging/mri/database.csv", sep=";", index_col=False)
# filter df: drop all rows where "series description" == NaN
df = df.dropna(subset="series description")
# filter df: drop all rows where "series description" does not include "tra T1"
df = df[df["series description"].str.contains("tra t1", case=False,)]

# group database
grpd = df.groupby(["patient species",
                   "patient id",
                   ])

for key, grp in grpd:
    if key[0] != "dog" or grp["series description"].count() != 3:
        continue
    print(key)
    print(grp[["series description", "series datetime", "image direction patient"]].sort_values("series datetime"))
    print("\n")