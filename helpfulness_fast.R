############################################################
# Amazon Helpfulness vs Rating (CHTC-safe version)
############################################################

library(data.table)

# ----------------------------
# File location (CHTC-safe: relative path)
# ----------------------------
args <- commandArgs(trailingOnly = TRUE)

if (length(args) == 0) {
  stop("No input file provided. Use: Rscript helpfulness_fast.R <file.tsv>")
}

file <- args[1]

cat("Processing file:", file, "\n")


# ----------------------------
# Read ONLY needed columns (critical for memory)
# ----------------------------
df <- fread(file,
            select = c("star_rating",
                       "helpful_votes",
                       "total_votes"))

cat("File loaded\n")

# ----------------------------
# Clean data
# ----------------------------
df <- df[!is.na(star_rating) &
         !is.na(helpful_votes) &
         !is.na(total_votes) &
         total_votes > 0]

# ----------------------------
# Compute helpfulness ratio
# ----------------------------
df[, helpful_ratio := helpful_votes / total_votes]

# ----------------------------
# Create sentiment groups
# ----------------------------
df[, sentiment := fifelse(star_rating <= 2, "negative",
                   fifelse(star_rating >= 4, "positive", "neutral"))]

# ----------------------------
# Summary statistics
# ----------------------------
result <- df[, .(
  mean_helpful = mean(helpful_ratio),
  median_helpful = median(helpful_ratio),
  n = .N
), by = sentiment]

# ----------------------------
# Output results
# ----------------------------



clean_name <- gsub(".*/", "", file)
output_file <- paste0("helpfulness_", clean_name, ".csv")

fwrite(result, output_file)

cat("Done!\n")
############################################################
