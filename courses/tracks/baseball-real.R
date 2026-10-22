# Source: N. D. Pifer (2024), Optical Tracking Data from College Baseball Scrimmages,
# Mendeley Data V3, doi:10.17632/xfnz6mkdzm.3; CC BY 4.0.
# Original CSV unchanged. Derived tables and plots below; no endorsement implied.
path <- "data/library/raw/7b7b8974107be6181dcf1880d609034ef9f7556f9fb13aec021a52d37cd0c190.csv"
pitch <- read.csv(path, stringsAsFactors = FALSE, na.strings = "",
                  colClasses = c(PitcherId = "character", BatterId = "character"))
stopifnot(nrow(pitch) == 3344, ncol(pitch) == 141)
pitch$pitchername <- pitch$PitcherId
pitch$pitchtype <- pitch$TaggedPitchType
pitch$px <- pitch$PlateLocSide
pitch$pz <- pitch$PlateLocHeight
source("courses/tracks/baseball-plots.R")
swings <- pitch$PitchCall %in% c("StrikeSwinging", "FoulBall", "InPlay")
whiffs <- pitch$PitchCall == "StrikeSwinging"
stopifnot(sum(swings) == 1432, sum(whiffs) == 381)
stopifnot(sum(pitch$TaggedPitchType == "Fastball") == 1745)
player <- subset(pitch, PitcherId == "1000036206")
stopifnot(nrow(player) == 193)
mix <- as.data.frame(table(player$TaggedPitchType))
names(mix) <- c("pitch_type", "pitches")
mix$share <- mix$pitches / nrow(player)
contact <- subset(pitch, PitchCall == "InPlay" & is.finite(ExitSpeed))
stopifnot(sum(pitch$PitchCall == "InPlay") == 549)
dir.create("output", showWarnings = FALSE)
write.csv(mix, "output/baseball-real-arsenal.csv", row.names = FALSE)
write.csv(aggregate(ExitSpeed ~ BatterId, contact, mean), "output/baseball-real-contact.csv", row.names = FALSE)
pdf("output/baseball-real-course.pdf", width = 11, height = 7)
par(mfrow = c(1, 2))
plot_pitcher_locations(pitch, "1000036206", "Real college scrimmages")
plot_pitcher_locations(pitch, "1000103199", "Real college scrimmages")
par(mfrow = c(1, 1))
barplot(mix$pitches, names.arg = mix$pitch_type, ylab = "Pitches", main = "Actual anonymous pitcher 1000036206")
outing <- subset(pitch, PitcherId == "1000103199" & TaggedPitchType == "Fastball" & Date == "11/6/2022")
if (nrow(outing)) {
  outing <- outing[order(outing$PitchNo), ]
  plot(outing$PitchNo, outing$RelSpeed, type = "b", xlab = "Pitch number within source outing",
       ylab = "Release speed (mph)", main = "Measured fastballs; source date label is anonymized")
}
hist(contact$ExitSpeed, breaks = "FD", main = "Measured InPlay exit speeds", xlab = "mph")
dev.off()
cat("PASS: real baseball R: 3344 measured pitches; 381/1432 whiffs; actual anonymous pitcher plots.\n")
