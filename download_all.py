import sys
sys.path.insert(0, '/home/clavier/pylibs')
import kagglehub
import pandas as pd
import numpy as np
import os
import shutil
from scipy import stats
import csv

files = [
    "amazon_reviews_multilingual_US_v1_00.tsv",
    "amazon_reviews_us_Apparel_v1_00.tsv",
    "amazon_reviews_us_Automotive_v1_00.tsv",
    "amazon_reviews_us_Baby_v1_00.tsv",
    "amazon_reviews_us_Beauty_v1_00.tsv",
    "amazon_reviews_us_Books_v1_02.tsv",
    "amazon_reviews_us_Camera_v1_00.tsv",
    "amazon_reviews_us_Digital_Ebook_Purchase_v1_01.tsv",
    "amazon_reviews_us_Digital_Music_Purchase_v1_00.tsv",
    "amazon_reviews_us_Digital_Software_v1_00.tsv",
    "amazon_reviews_us_Digital_Video_Download_v1_00.tsv",
    "amazon_reviews_us_Digital_Video_Games_v1_00.tsv",
    "amazon_reviews_us_Electronics_v1_00.tsv",
    "amazon_reviews_us_Furniture_v1_00.tsv",
    "amazon_reviews_us_Gift_Card_v1_00.tsv",
    "amazon_reviews_us_Grocery_v1_00.tsv",
    "amazon_reviews_us_Health_Personal_Care_v1_00.tsv",
    "amazon_reviews_us_Major_Appliances_v1_00.tsv",
    "amazon_reviews_us_Mobile_Apps_v1_00.tsv",
    "amazon_reviews_us_Mobile_Electronics_v1_00.tsv",
    "amazon_reviews_us_Music_v1_00.tsv",
    "amazon_reviews_us_Musical_Instruments_v1_00.tsv",
    "amazon_reviews_us_Office_Products_v1_00.tsv",
    "amazon_reviews_us_Outdoors_v1_00.tsv",
    "amazon_reviews_us_PC_v1_00.tsv",
    "amazon_reviews_us_Personal_Care_Appliances_v1_00.tsv",
    "amazon_reviews_us_Pet_Products_v1_00.tsv",
    "amazon_reviews_us_Shoes_v1_00.tsv",
    "amazon_reviews_us_Software_v1_00.tsv",
    "amazon_reviews_us_Sports_v1_00.tsv",
    "amazon_reviews_us_Tools_v1_00.tsv",
    "amazon_reviews_us_Toys_v1_00.tsv",
    "amazon_reviews_us_Video_DVD_v1_00.tsv",
    "amazon_reviews_us_Video_Games_v1_00.tsv",
    "amazon_reviews_us_Video_v1_00.tsv",
    "amazon_reviews_us_Watches_v1_00.tsv",
    "amazon_reviews_us_Wireless_v1_00.tsv",
]

SAMPLE_SIZE = 100000

summary_results = []
sentiment_results = []
all_category_ratings = {}

for f in files:
    print("Processing: " + f)
    try:
        tsv_path = kagglehub.dataset_download(
            "cynthiarempel/amazon-us-customer-reviews-dataset",
            path=f
        )
        if os.path.isdir(tsv_path):
            tsv_path = os.path.join(tsv_path, f)

        total_rows = sum(1 for _ in open(tsv_path, errors='ignore')) - 1
        skip = max(0, total_rows - SAMPLE_SIZE)

        df = pd.read_csv(
            tsv_path,
            sep="\t",
            on_bad_lines='skip',
            engine='python',
            quoting=csv.QUOTE_NONE,
            encoding_errors='ignore',
            skiprows=range(1, skip + 1)
        )

        df['star_rating'] = pd.to_numeric(df['star_rating'], errors='coerce')
        df['helpful_votes'] = pd.to_numeric(df['helpful_votes'], errors='coerce')
        df['total_votes'] = pd.to_numeric(df['total_votes'], errors='coerce')
        df = df.dropna(subset=['star_rating', 'product_category'])
        df['review_length'] = df['review_body'].astype(str).apply(len)

        category = df['product_category'].iloc[0]
        ratings = df['star_rating']

        avg_rating = round(ratings.mean(), 4)
        var_rating = round(ratings.var(), 4)
        std_rating = round(ratings.std(), 4)
        review_count = len(df)

        corr, corr_pval = stats.pearsonr(
            df['review_length'].fillna(0),
            df['star_rating'].fillna(0)
        )

        df_reg = df[['star_rating', 'review_length']].dropna()
        slope, intercept, r_val, p_val, std_err = stats.linregress(
            df_reg['review_length'], df_reg['star_rating']
        )

        summary_results.append({
            'category': category,
            'review_count': review_count,
            'avg_rating': avg_rating,
            'variance': var_rating,
            'std_dev': std_rating,
            'corr_length_rating': round(corr, 4),
            'corr_pvalue': round(corr_pval, 4),
            'regression_slope': round(slope, 6),
            'regression_intercept': round(intercept, 4),
            'regression_r2': round(r_val**2, 4),
            'regression_pvalue': round(p_val, 4),
        })

        all_category_ratings[category] = ratings.values

        df['sentiment'] = 'Neutral'
        df.loc[df['star_rating'] >= 4, 'sentiment'] = 'Positive'
        df.loc[df['star_rating'] <= 2, 'sentiment'] = 'Negative'

        df_votes = df[df['total_votes'] > 0].copy()
        df_votes['pct_helpful'] = df_votes['helpful_votes'] / df_votes['total_votes'] * 100

        for sentiment in ['Positive', 'Neutral', 'Negative']:
            subset = df_votes[df_votes['sentiment'] == sentiment]
            count_s = len(df[df['sentiment'] == sentiment])
            pct_of_total = round(count_s / review_count * 100, 1)
            avg_pct_helpful = round(subset['pct_helpful'].mean(), 1) if len(subset) > 0 else None
            median_helpful = round(subset['helpful_votes'].median(), 1) if len(subset) > 0 else None

            sentiment_results.append({
                'category': category,
                'sentiment': sentiment,
                'count': count_s,
                'pct_of_reviews': pct_of_total,
                'avg_pct_helpful': avg_pct_helpful,
                'median_helpful_votes': median_helpful,
            })

        print("  Done: " + category + " | avg=" + str(avg_rating) + " | rows=" + str(review_count))
        cache_dir = os.path.dirname(tsv_path)
        shutil.rmtree(cache_dir, ignore_errors=True)

    except Exception as e:
        print("  ERROR on " + f + ": " + str(e))

summary_df = pd.DataFrame(summary_results).sort_values('avg_rating', ascending=False)

if len(summary_df) >= 2:
    top_cat = summary_df.iloc[0]['category']
    bot_cat = summary_df.iloc[-1]['category']
    if top_cat in all_category_ratings and bot_cat in all_category_ratings:
        t_stat, t_pval = stats.ttest_ind(
            all_category_ratings[top_cat],
            all_category_ratings[bot_cat],
            equal_var=False
        )
        print("\n=== T-Test: " + top_cat + " vs " + bot_cat + " ===")
        print("t-statistic: " + str(round(t_stat, 4)))
        print("p-value: " + str(round(t_pval, 6)))

sentiment_df = pd.DataFrame(sentiment_results)
chi_data = sentiment_df[sentiment_df['sentiment'].isin(['Positive', 'Negative'])]
chi_pivot = chi_data.pivot_table(index='category', columns='sentiment', values='count', aggfunc='sum').dropna()
if chi_pivot.shape[0] > 1:
    chi2, chi_pval, dof, expected = stats.chi2_contingency(chi_pivot)
    print("\n=== Chi-Square Test ===")
    print("chi2: " + str(round(chi2, 2)))
    print("p-value: " + str(round(chi_pval, 6)))
    print("degrees of freedom: " + str(dof))

print("\n=== Summary Statistics ===")
print(summary_df.to_string(index=False))
summary_df.to_csv("category_summary_stats.csv", index=False)
sentiment_df.to_csv("category_sentiment_analysis.csv", index=False)
print("\nSaved category_summary_stats.csv and category_sentiment_analysis.csv")