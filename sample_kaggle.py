import os
import glob
import pandas as pd
import kagglehub

scratch = os.getcwd()
os.environ["KAGGLEHUB_CACHE"] = os.path.join(scratch, "kaggle_cache")

dataset = "cynthiarempel/amazon-us-customer-reviews-dataset"
path = kagglehub.dataset_download(dataset)

print("Downloaded to:", path)

files = sorted(glob.glob(os.path.join(path, "*.tsv")) + glob.glob(os.path.join(path, "*.csv")))
print("Available files:")
for f in files:
    print(os.path.basename(f))

# choose one file explicitly
target_name = "amazon_reviews_us_Books_v1_02.tsv"
matches = [f for f in files if os.path.basename(f) == target_name]

if not matches:
    raise FileNotFoundError(f"Could not find {target_name}")

data_file = matches[0]
print("Using file:", data_file)

df = pd.read_csv(data_file, sep="\t", nrows=100_000)
df.to_csv("sample_100k.csv", index=False)
print("Saved sample_100k.csv")
