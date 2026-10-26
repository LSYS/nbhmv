## PPML replication of the four manuscript robustness tables.
## Mirrors analysis/code/mismatch/pxor_*_count_ppml.do.
## Much faster than ppmlhdfe in Stata (~1 hr total vs 1-3 days per table)
## Run from this folder: Rscript ppmlhdfe.R

.libPaths(c(path.expand("~/R/library"), .libPaths()))

library(readstata13)
library(fixest)
library(marginaleffects)

setFixest_nthreads(10)
setFixest_notes(FALSE)
# hypotheses() warns about fixed-effect uncertainty, which does not apply to a test on coefficients
options(marginaleffects_safe = FALSE)

PANEL <- "ppml-panel.dta"
OUT <- "../../../results/tables/ppml/ppml_fixest_results.csv"

##=============================================================================
## Specification
##=============================================================================
DIST <- c(
  "centroid_distance",
  "contiguous"
)
POPDEN <- c(
  "lnpop_origin",
  "lnpop_dest",
  "lndevice_origin",
  "lndevice_dest"
)
LANDAREA <- c(
  "area_o",
  "area_d"
)
DEMO <- c(
  "age_20_o",
  "age_20_d",
  "age20_40_o",
  "age20_40_d",
  "age65__o",
  "age65__d",
  "females_o",
  "females_d"
)
BUSINESS <- c(
  "manufacturing",
  "construction",
  "services"
)
RAIN <- c(
  "rain_dest",
  "rain_origin"
)
POI <- c(
  "libraries",
  "supermarkets",
  "parks",
  "preschools",
  "schzones",
  "silverzones",
  "sport_facilities",
  "transit",
  "tour",
  "schools",
  "hawkers",
  "shopping_malls"
)

SPECS <- list(
  `1` = c(DIST, POPDEN, LANDAREA),
  `2` = c(DIST, POPDEN, LANDAREA, DEMO),
  `3` = c(DIST, POPDEN, LANDAREA, DEMO, BUSINESS),
  `4` = c(DIST, POPDEN, LANDAREA, DEMO, BUSINESS, RAIN),
  `5` = c(DIST, POPDEN, LANDAREA, DEMO, BUSINESS, RAIN, POI)
)

TABLES <- list(
  `pxor-wpsm`           = c("mismatch_p25"),
  `pxor-wpsm-r2p-p2r`   = c("mismatch_p25_p2r", "mismatch_p25_r2p"),
  `pxor-race`           = c("mismatch_race"),
  `pxor-race-asymmetry` = c("mismatch_race_m2c", "mismatch_race_c2m")
)

##=============================================================================
## Estimate
##=============================================================================
t_start <- Sys.time()
d <- read.dta13(PANEL, convert.factors = FALSE)
d$date <- as.integer(d$date)

out <- list()
for (tab in names(TABLES)) {
  xs <- TABLES[[tab]]
  for (s in names(SPECS)) {
    controls <- SPECS[[s]]

    fml <- as.formula(sprintf(
      "inflow_count ~ %s | date^pa_origin + date^pa_dest + date[%s]",
      paste(xs, collapse = " + "), paste(controls, collapse = ", ")
    ))

    cat(sprintf("[%s spec %s] %d controls ... ", tab, s, length(controls)))
    t1 <- Sys.time()
    fit <- fepois(fml, data = d, cluster = ~odid,
                  ssc = ssc(adj = FALSE, cluster.adj = TRUE))
    cat(sprintf("%.0fs\n", difftime(Sys.time(), t1, units = "secs")))

    # t-test of x1 = x2
    joint_p <- NA
    if (length(xs) == 2) {
      h <- hypotheses(fit, hypothesis = sprintf("%s = %s", xs[1], xs[2]))
      joint_p <- h$p.value
    }

    # save results, one row per estimate
    used <- obs(fit)
    out[[paste(tab, s)]] <- data.frame(
      table   = tab,
      spec    = as.integer(s),
      term    = xs,
      coef    = as.numeric(coef(fit)[xs]),
      se      = as.numeric(se(fit)[xs]),
      pvalue  = as.numeric(pvalue(fit)[xs]),
      nobs    = fit$nobs,
      nclust  = length(unique(d$odid[used])),
      ndates  = length(unique(d$date[used])),
      pr2     = as.numeric(fitstat(fit, "pr2")$pr2),
      joint_p = joint_p,
      row.names = NULL
    )

  }
}

write.csv(do.call(rbind, out), OUT, row.names = FALSE)
cat(sprintf("\nwrote %s  (total %.1f min)\n", OUT,
            difftime(Sys.time(), t_start, units = "mins")))
