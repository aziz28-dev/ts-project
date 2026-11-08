# Installation des packages R du socle classique (cahier §8.1, section 3 en R).
# Usage : Rscript install_packages.R  (R >= 4.3)

# Snapshot CRAN daté (Posit Package Manager) : fige les versions sans renv,
# donc la même installation sur toute machine vierge.
options(repos = c(CRAN = "https://packagemanager.posit.co/cran/2025-10-01"))

if (getRversion() < "4.3.0") stop("R >= 4.3 requis, version trouvée : ", getRversion())

packages <- c(
  # Données et séries temporelles
  "quantmod", "xts", "zoo", "yaml", "here",
  # ARIMA, tests de stationnarité et de résidus
  "forecast", "tseries", "lmtest", "FinTS",
  # VAR, cointégration, VECM
  "vars", "urca",
  # GARCH (rmgarch : DCC-GARCH, extension §7)
  "rugarch", "rmgarch",
  # Rendu
  "ggplot2", "rmarkdown", "knitr"
)

missing <- setdiff(packages, rownames(installed.packages()))
if (length(missing) > 0) install.packages(missing)

# FinTS peut être retiré de CRAN : on le signale au lieu d'échouer, ArchTest
# se recode alors en quelques lignes (régression de e_t^2 sur ses retards).
failed <- setdiff(packages, rownames(installed.packages()))
if (length(failed) > 0) warning("Packages non installés : ", paste(failed, collapse = ", "))

# Versions affichées pour les documenter dans le rapport (critère reproductibilité).
ok <- setdiff(packages, failed)
print(data.frame(package = ok,
                 version = vapply(ok, function(p) as.character(packageVersion(p)), "")),
      row.names = FALSE)
cat("R", as.character(getRversion()), "\n")
