import os
import sys
import pandas as pd

filename = sys.argv[1]
category = os.path.basename(filename).replace("amazon_reviews_us_", "").replace(".tsv", "")

df = pd.read_csv(
    filename,
    sep="\t",
    usecols=["star_rating"],
    low_memory=False
)

df["star_rating"] = pd.to_numeric(df["star_rating"], errors="coerce")
df = df.dropna(subset=["star_rating"])

mean_rating = df["star_rating"].mean()
count = len(df)

outfile = f"{category}_summary.csv"
with open(outfile, "w") as f:
    f.write("category,mean_star_rating,n_reviews\n")
    f.write(f"{category},{mean_rating},{count}\n")

print(f"Wrote {outfile}")
