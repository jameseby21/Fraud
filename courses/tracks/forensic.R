# Run from repository root: Rscript courses/tracks/forensic.R
d <- read.csv("data/forensic/v2/payments.csv", stringsAsFactors = FALSE)
entities <- read.csv("data/forensic/v2/entities.csv", stringsAsFactors = FALSE)
invoices <- read.csv("data/forensic/v2/invoices.csv", stringsAsFactors = FALSE)
bank <- read.csv("data/forensic/v2/bank_entries.csv", stringsAsFactors = FALSE)
stopifnot(nrow(d) == 12000, nrow(entities) == 120, nrow(invoices) == 11999,
          nrow(bank) == 12000, length(unique(d$transaction_id)) == 12000,
          all(d$supplier_id %in% entities$supplier_id), all(d$invoice_id %in% invoices$invoice_id))
# evidence-brief: match bank to ledger without multiplying invoice rows
positions <- match(bank$transaction_id, d$transaction_id)
stopifnot(!anyNA(positions))
differences <- -bank$signed_amount_cents - d$amount_cents[positions]
stopifnot(sum(differences != 0) == 1, sum(abs(differences)) == 500)
# round-sums: integer-valued doubles are exact within this fixture's range
groups <- split(d, paste(d$supplier_id, d$payment_date, sep = "|"))
candidates <- Filter(function(x) nrow(x) >= 3 && sum(x$amount_cents) %% 1000000 == 0, groups)
stopifnot(length(candidates) >= 12)
# distribution-shift: descriptive CDF distance, not a calibrated test
before <- subset(d, supplier_id == "VEN-0088" & payment_date < "2025-10-01")$amount_cents
after <- subset(d, supplier_id == "VEN-0088" & payment_date >= "2025-10-01")$amount_cents
domain <- sort(unique(c(before, after)))
distance <- max(abs(ecdf(before)(domain) - ecdf(after)(domain)))
stopifnot(length(before) > 0, length(after) > 0, distance > 0.15)
dir.create("output", showWarnings = FALSE)
pdf("output/forensic-r.pdf", width = 10, height = 7)
hist(d$amount_cents / 100, breaks = 50, xlab = "Synthetic USD", main = "All fictional payments; actual source values reassigned")
plot(ecdf(before / 100), col = "darkgreen", xlab = "Synthetic USD", ylab = "Empirical cumulative fraction", main = "Supplier VEN-0088: before/after 2025-10-01")
lines(ecdf(after / 100), col = "brown")
legend("bottomright", c("Before", "After"), col = c("darkgreen", "brown"), lty = 1)
first_digit <- function(x) as.integer(substr(as.character(as.integer(x)), 1, 1))
profiles <- rbind(tabulate(first_digit(before), nbins = 9) / length(before),
                  tabulate(first_digit(after), nbins = 9) / length(after))
barplot(profiles, beside = TRUE, names.arg = 1:9, legend.text = c("Before", "After"),
        xlab = "Leading digit of cents", ylab = "Fraction", main = "Descriptive digits; Benford assumptions not established")
dev.off()
cat(sprintf("PASS: 12000 payments; 120 entities; %d round-total candidates; one 500-cent bank difference; CDF distance %.4f.\n", length(candidates), distance))
