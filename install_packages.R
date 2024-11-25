# install_packages.R
required_packages <- c("dplyr", "ggplot2", "jsonlite")

# Install missing packages
for (pkg in required_packages) {
  if (!require(pkg, character.only = TRUE)) {
    install.packages(pkg)
  }
}
