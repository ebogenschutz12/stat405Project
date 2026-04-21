import sys
sys.path.insert(0, '/home/clavier/pylibs')

import pandas as pd

df = pd.read_csv(
    "/home/clavier/.cache/kagglehub/datasets/cynthiarempel/amazon-us-customer-reviews-dataset/versions/9/amazon_reviews_multilingual_US_v1_00.tsv",
    sep="\t",
    on_bad_lines='skip',
    engine='python'
)

print("Shape:", df.shape)
print("Columns:", df.columns.tolist())

avg = df['star_rating'].mean()
print(f"Average star rating: {round(avg, 2)}")
