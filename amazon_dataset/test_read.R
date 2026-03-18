library(readr)

# Read a small chunk of one file
data <- read_tsv("amazon_reviews_us_Electronics_v1_00.tsv", n_max = 100000)

# Print first few rows
print(head(data))

# Compute average rating
avg_rating <- mean(data$star_rating, na.rm = TRUE)

# Print result
print(paste("Average rating:", avg_rating))
