# Base R track. Run from repository root: Rscript courses/tracks/analysis.R
# Synthetic teaching records only. Read each Markdown lesson before its check.
options(stringsAsFactors = FALSE)
input <- "data/learning/transactions.csv"
if (!file.exists(input)) stop("Run from the Fraud repository root; CSV is missing")
d <- read.csv(input, colClasses = "character", check.names = FALSE)
d$amount_cents <- as.numeric(d$amount_cents)
stopifnot(!anyNA(d$amount_cents), all(d$amount_cents == floor(d$amount_cents)))
# Values fit exactly in R doubles for this dataset; this is not a general 64-bit money parser.
d$amount_usd <- d$amount_cents / 100
d$invoice_date <- as.Date(d$invoice_date)
d$payment_date <- as.Date(d$payment_date)
d$delay_days <- as.integer(d$payment_date - d$invoice_date)
d$month <- format(d$invoice_date, "%Y-%m")

# orientation
stopifnot(nrow(d) == 6000, length(unique(d$transaction_id)) == 6000,
          all(d$synthetic == "True"), !anyNA(d), sum(d$amount_cents) == 1355092995)
# quality: supplier + invoice key, not amount alone
invoice_key <- paste(d$supplier, d$invoice_id, sep = "|")
repeated <- d[duplicated(invoice_key) | duplicated(invoice_key, fromLast = TRUE), ]
stopifnot(nrow(repeated) == 2)
# comparison
stopifnot(max(d$amount_cents) == 27500000)
# timing
late <- d[d$delay_days > 90, ]
stopifnot(nrow(late) == 1, late$delay_days == 181)
# thresholds: five candidates, only one deliberately planted
supplier_day <- split(d, paste(d$supplier, d$invoice_date, sep = "|"))
candidates <- Filter(function(x) nrow(x) >= 3 && all(x$amount_cents < 1000000) &&
                       sum(x$amount_cents) > 1000000, supplier_day)
stopifnot(length(candidates) == 5)
# review, summaries, capacity
monthly <- aggregate(amount_usd ~ month, d, sum)
category <- aggregate(amount_usd ~ category, d, sum)
regional <- aggregate(amount_usd ~ region, d, sum)
regional <- regional[order(-regional$amount_usd), ]
regional$cumulative_share <- cumsum(regional$amount_usd) / sum(regional$amount_usd)
grid <- xtabs(amount_usd ~ department + category, d)
stopifnot(nrow(monthly) == 12, length(grid) == 16,
          abs(sum(monthly$amount_usd) - sum(d$amount_usd)) < 0.01,
          abs(tail(regional$cumulative_share, 1) - 1) < 1e-12)

dir.create("output", showWarnings = FALSE)
pdf("output/course-r.pdf", width = 10, height = 7)
barplot(category$amount_usd, names.arg = category$category, ylab = "Synthetic USD", main = "Category totals")
plot(as.Date(paste0(monthly$month, "-01")), monthly$amount_usd, type = "o",
     xlab = "Invoice month", ylab = "Synthetic USD", main = "Invoice-month trend")
hist(d$amount_usd, breaks = 50, xlab = "Synthetic USD", main = "Amount distribution (equal-width bins)")
plot(d$amount_usd, d$delay_days, pch = 16, col = rgb(0, .4, .3, .25),
     xlab = "Synthetic USD", ylab = "Payment delay (days)", main = "All 6,000 transactions")
boxplot(amount_usd ~ category, d, ylab = "Synthetic USD", main = "Tukey boxplots (R defaults)")
image(seq_len(nrow(grid)), seq_len(ncol(grid)), grid, axes = FALSE,
      xlab = "Department", ylab = "Category", main = "Synthetic USD totals by department/category")
axis(1, at = seq_len(nrow(grid)), labels = rownames(grid))
axis(2, at = seq_len(ncol(grid)), labels = colnames(grid))
for (i in seq_len(nrow(grid))) for (j in seq_len(ncol(grid))) text(i, j, round(grid[i,j]))
centers <- barplot(regional$amount_usd, names.arg = regional$region, ylab = "Synthetic USD", main = "Regional concentration")
par(new = TRUE)
plot(centers, regional$cumulative_share * 100, type = "o", col = "brown",
     axes = FALSE, xlab = "", ylab = "", ylim = c(0, 100), xlim = par("usr")[1:2], xaxs = "i")
axis(4); mtext("Cumulative percent", side = 4, line = 2)
dev.off()
cat("PASS: 6000 rows; 1 repeated invoice group; 5 threshold candidates; 1 delay over 90 days.\n")
cat("Charts: output/course-r.pdf. Whiskers and histogram bins differ from the browser; see the track guide.\n")
