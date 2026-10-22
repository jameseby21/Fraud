# Adapted pitcher-subset / px-pz / pitch-type comparison from owner-supplied
# Ballpark Estimates (2016). Shared by the real-data and synthetic R tracks.
plot_pitcher_locations <- function(pitch, pitcher_name, source_label = "fictional") {
  pitch_subset <- subset(pitch, pitchername == pitcher_name)
  valid <- is.finite(pitch_subset$px) & is.finite(pitch_subset$pz)
  pitch_subset <- pitch_subset[valid, ]
  types <- sort(unique(pitch$pitchtype))
  pitch_colors <- setNames(grDevices::hcl.colors(length(types), "Dark 3"), types)
  if (!nrow(pitch_subset)) { plot.new(); title("No measured locations for this pitcher"); return(invisible(NULL)) }
  plot(pitch_subset$px, pitch_subset$pz, col = pitch_colors[pitch_subset$pitchtype],
       pch = 16, cex = .45, asp = 1, xlim = range(c(-2.5, 2.5, pitch_subset$px)),
       ylim = range(c(0, 5, pitch_subset$pz)), xlab = "Horizontal plate location (source feet)",
       ylab = "Plate height (feet)", main = paste(pitcher_name, "n =", nrow(pitch_subset)),
       sub = paste(source_label, "- source signs preserved; equal scales"))
  if (source_label == "fictional") rect(-.83, 1.5, .83, 3.5, border = "black")
  legend("topright", legend = types, col = pitch_colors, pch = 16, cex = .65)
}
