import glob
import pandas as pd

files = glob.glob("*_summary.csv")

dfs = [pd.read_csv(f) for f in files]
result = pd.concat(dfs, ignore_index=True)

result = result.sort_values("mean_star_rating", ascending=False)

print(result)

result.to_csv("all_category_avg_ratings.csv", index=False)
