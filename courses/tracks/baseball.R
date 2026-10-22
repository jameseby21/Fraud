# Ballpark Estimates adaptation: owner-supplied 2016 project, pitcher filtering,
# px/pz location comparison and pitch-type overlay. See docs/sports/archive-review.md.
# Fresh base-R plotting replaces the incomplete Shiny wiring and deprecated density syntax.
pitch <- read.csv("data/baseball/v1/pitches.csv", stringsAsFactors = FALSE, na.strings = "")
stopifnot(nrow(pitch) == 3600, length(unique(pitch$pitch_id)) == 3600)
pitch$pitchername <- pitch$pitcher
pitch$pitchtype <- pitch$pitch_type
pitch$px <- pitch$plate_x_ft
pitch$pz <- pitch$plate_z_ft
pitch_colors <- c(FF = "#1768ac", SL = "#b64517", CH = "#6b4e96")

source("courses/tracks/baseball-plots.R")

mix <- as.data.frame(with(pitch, table(pitcher, period, pitch_type)))
names(mix) <- c("pitcher", "period", "pitch_type", "count")
mix$share <- with(mix, count / ave(count, pitcher, period, FUN = sum))
stopifnot(subset(mix, pitcher == "Rowan Ellis" & period == "early" & pitch_type == "FF")$share == .6,
          subset(mix, pitcher == "Rowan Ellis" & period == "late" & pitch_type == "FF")$share == .4)
ff <- subset(pitch, pitcher == "Mateo Brooks" & pitch_type == "FF")
velocity_gap <- mean(subset(ff, inning <= 2)$speed_mph) - mean(subset(ff, inning >= 6)$speed_mph)
stopifnot(velocity_gap > 1.5)
whiffs <- aggregate(cbind(whiff, swing) ~ pitch_type + in_zone, data = pitch, FUN = sum)
whiffs$whiff_rate <- ifelse(whiffs$swing > 0, whiffs$whiff / whiffs$swing, NA_real_)
contact <- subset(pitch, in_play == 1)
contact_means <- aggregate(exit_speed_mph ~ batter + period, data = contact, FUN = mean)
casey <- subset(contact_means, batter == "Casey Morgan")
stopifnot(casey$exit_speed_mph[casey$period == "late"] - casey$exit_speed_mph[casey$period == "early"] > 3)

dir.create("output", showWarnings = FALSE)
write.csv(mix, "output/baseball-pitch-mix.csv", row.names = FALSE)
write.csv(whiffs, "output/baseball-whiffs.csv", row.names = FALSE)
write.csv(contact_means, "output/baseball-contact.csv", row.names = FALSE)
pdf("output/baseball-course.pdf", width = 11, height = 7)
par(mfrow = c(1, 2))
plot_pitcher_locations(pitch, "Rowan Ellis")
plot_pitcher_locations(pitch, "Mateo Brooks")
par(mfrow = c(1, 1))
arsenal <- subset(mix, pitcher == "Rowan Ellis")
barplot(xtabs(share ~ pitch_type + period, arsenal), beside = TRUE,
        col = pitch_colors, ylab = "Share of all pitches in period", legend.text = TRUE,
        main = "Rowan Ellis arsenal: 300 pitches per period", ylim = c(0, 1))
inning <- aggregate(speed_mph ~ inning, ff, mean)
plot(inning$inning, inning$speed_mph, type = "b", xlab = "Inning", ylab = "Mean FF speed (mph)",
     main = "Mateo Brooks: FF only; sampled outings pooled")
plot(pitch$movement_x_in, pitch$movement_z_in, pch = 16, cex = .3,
     col = pitch_colors[pitch$pitch_type], asp = 1, xlab = "Horizontal movement (inches, catcher view)",
     ylab = "Vertical movement (inches)", main = "Full sample: 3,600 fictional pitches")
legend("topright", legend = names(pitch_colors), col = pitch_colors, pch = 16)
boxplot(speed_mph ~ pitch_type, pitch, ylab = "mph", main = "Pitch velocity: R Tukey whiskers")
hist(subset(contact, batter == "Casey Morgan")$exit_speed_mph, breaks = seq(70,110,5),
     main = "Casey Morgan tracked contact", xlab = "Exit speed (mph)")
dev.off()
cat("PASS: baseball R: 3600 pitches; arsenal, velocity, whiff and contact checks; PDF and CSVs written.\n")
