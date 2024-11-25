library(ggplot2)
library(dplyr)
library(jsonlite)

#############################################################################################
# avg calving interval
# let's just look at the idAnimale =="-9223372036848126976" calving interval
# animal_data from useful_animals_df.csv, 5th row

animal_data <- '{
  "Birth": "2017-01-05",
  "Insemination": ["2018-05-30", "2019-06-14", "2019-06-29", "2020-05-30", "2021-05-24", "2021-06-15", "2022-06-27", "2023-06-04", "2023-08-06"],
  "Pregnancy Diagnosis": [["2020-09-01", "positiva"]],
  "Calving": ["2019-03-21", "2020-03-29", "2021-03-11", "2022-03-28", "2023-04-26"],
  "Dry Period": ["2020-02-07", "2021-01-05", "2022-01-10", "2023-02-14"]
}'

# Parse JSON and extract Calving dates
animal_events <- fromJSON(animal_data)
calving_dates <- as.Date(animal_events$Calving)

# Calculate Calving Intervals
calving_intervals <- diff(calving_dates)

# Create a data frame for plotting
calving_df <- data.frame(
  Date = calving_dates[-1],  # Use dates from the second calving event onward
  Calving_Interval = as.numeric(calving_intervals)  # Convert intervals to numeric
)

head(calving_df)

# Set y-axis limits
y_min <- min(calving_intervals) - 10
y_max <- max(calving_intervals) + 10

output_path <- "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/figure2/"

# plot <- ggplot(calving_df, aes(x = Date, y = Calving_Interval)) +
# #   geom_line(color = "black", linewidth = 1) +
#   geom_point(color = "hot pink", size = 15) +
#   labs(
#     title = "Calving Interval for Animal -9223372036848126976",
#     x = NULL,
#     y = NULL
#   ) +
#   theme_minimal(base_size = 15) + 
#   theme(
#     axis.text.x = element_text(size = 26, angle = 45, hjust = 1),
#     axis.text.y = element_text(size = 24),
#     plot.margin = margin(10, 40, 15, 45)
#   ) +
#   # Ensure only actual data points are shown on the x-axis
#   scale_x_date(date_labels = "%Y-%m-%d", breaks = calving_df$Date) +
#   scale_y_continuous(limits = c(y_min, y_max))

plot <- ggplot(calving_df, aes(x = factor(Date), y = Calving_Interval)) +  # Use factor(Date) for categorical x-axis
  geom_bar(stat = "identity", fill = "hot pink", width = 0.7) +  # Use stat="identity" to map Calving_Interval
  labs(
    title = "Calving Interval for Animal -9223372036848126976",
    x = NULL,
    y = NULL
  ) +
  theme_minimal(base_size = 15) + 
  theme(
    axis.text.x = element_text(size = 26, angle = 45, hjust = 1),
    axis.text.y = element_text(size = 24),
    plot.title = element_text(size = 22, face = "bold", hjust = 0.5),
    plot.margin = margin(10, 40, 15, 45)
  ) +
  coord_cartesian(ylim = c(330, 420)) 



# Save the plot
ggsave(
  filename = paste0(output_path, "calving_interval_plot.png"),
  plot = plot, 
  width = 10, 
  height = 8
)

###############################################################################################################
###############################################################################################################
# idAnimale == "-9223372036848126976" 
# time point:  2024-09-06 ~ 2024-09-13
# siglaProvincia == "BZ"

input_path <- "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/"
output_path <- "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/figure2/"
files <- c("Casein.csv", "Fat.csv", "Protein.csv", "Lactose.csv", 
           "Time to curd firmness (A30).csv", "Time to curd firmness (K20).csv", 
           "Rennet Coagulation time (R).csv")

# Function to calculate population mean for siglaProvincia == "BZ"
calculate_population_mean <- function(file) {
  data <- read.table(paste0(input_path, file), header = TRUE, sep = ",")
  
  population_data <- data %>%
    mutate(full_date = as.Date(full_date)) %>%
    filter(
      full_date >= as.Date("2024-09-06") & full_date <= as.Date("2024-09-13"),
      siglaProvincia == "BZ"
    ) %>%
    group_by(full_date) %>%
    summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")
  
  mean(population_data$valoreMisura, na.rm = TRUE)
}

for (file in files) {
  # Read data
  data <- read.table(paste0(input_path, file), header = TRUE, sep = ",")
  
  # Filter for specific animal and time range
  filtered_data <- data %>%
    mutate(full_date = as.Date(full_date)) %>%
    filter(
      full_date >= as.Date("2024-09-06") & full_date <= as.Date("2024-09-13"),
      siglaProvincia == "BZ",
      idAnimale == "-9223372036848126976"
    )
  
  filtered_data_averaged <- filtered_data %>%
    group_by(full_date) %>%
    summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")
  
  if (nrow(filtered_data_averaged) == 0) {
    warning("No data available for the specified time frame for trait: ", file)
    next
  }

  # Extract trait name
  trait_name <- gsub("\\.csv", "", file)
  
  # Calculate population mean from BZ province
  population_mean <- calculate_population_mean(file)
  
  if (is.na(population_mean)) {
    warning("Population mean could not be calculated for trait: ", trait_name)
    next
  }

  # Define y-axis range
  y_range <- range(filtered_data_averaged$valoreMisura, na.rm = TRUE)
  y_min <- y_range[1] - ifelse(trait_name %in% c("Casein", "Fat", "Lactose", "Protein"), 0.2, 1)
  y_max <- y_range[2] + ifelse(trait_name %in% c("Casein", "Fat", "Lactose", "Protein"), 0.2, 1)
  
  # Create the plot
  plot <- ggplot(filtered_data_averaged, aes(x = full_date, y = valoreMisura)) +
    geom_line(color = "black", linewidth = 1) +
    geom_point(color = "hot pink", size = 5) +
    geom_hline(yintercept = population_mean, linetype = "dashed", color = "red", linewidth = 3) +
    labs(
      title = paste0(trait_name, " for siglaProvincia BZ"),
      x = NULL,
      y = NULL
    ) +
    theme_minimal(base_size = 15) +
    theme(
      axis.text.x = element_text(size = 26, angle = 45, hjust = 1),
      axis.text.y = element_text(size = 24),
      plot.margin = margin(10, 40, 15, 45)
    ) +
    scale_x_date(date_labels = "%Y-%m-%d", date_breaks = "1 day") +  # Ensure daily breaks
    scale_y_continuous(limits = c(y_min, y_max))
  
  # Save the plot
  ggsave(
    filename = paste0(output_path, trait_name, "_plot.png"),
    plot = plot,
    width = 10,
    height = 8
  )
}


###############################################################################################################
# time point:  2024-09-12 ~ 2024-09-24
# animals living in siglaProvincia == BZ
# 1. use the population mean within the specificed time point (flat line)
# these are codes for the population mean at the time point and the region == BZ

input_path <- "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/"
summary_stats <- read.csv("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/0report/descriptive_statistics_summary.csv")

files <- c("Casein.csv", "Fat.csv", "Protein.csv", "Lactose.csv", 
           "Time to curd firmness (A30).csv", "Time to curd firmness (K20).csv", 
           "Rennet Coagulation time (R).csv")

for (file in files) {
  # Read data
  data <- read.table(paste0(input_path, file), header = TRUE, sep = ",")
  
  # Filter and prepare data
  filtered_data <- data %>%
    mutate(full_date = as.Date(full_date)) %>%  # Convert full_date to Date type
    arrange(full_date) %>%  # Arrange by date
    filter(
      full_date >= as.Date("2024-09-06") & full_date <= as.Date("2024-09-13"),  # Filter date range
      siglaProvincia == "BZ"  # Filter by siglaProvincia
    )
  
  # Average valoreMisura for each full_date
  filtered_data_averaged <- filtered_data %>%
    group_by(full_date) %>%
    summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")  # Calculate daily mean
  
  if (nrow(filtered_data_averaged) == 0) {
    warning("No data available for the specified time frame for trait: ", file)
    next
  }

  # Extract trait name
  trait_name <- gsub("\\.csv", "", file)

  # Calculate the average of filtered_data_averaged for the geom_hline
  average_valoreMisura <- mean(filtered_data_averaged$valoreMisura, na.rm = TRUE)
  
  # Define y-axis range
  y_range <- range(filtered_data_averaged$valoreMisura, na.rm = TRUE)

  if (trait_name %in% c("Casein", "Fat", "Lactose", "Protein")) {
    y_min <- y_range[1] - 0.2
    y_max <- y_range[2] + 0.2
  } else {
    y_min <- y_range[1] - 1
    y_max <- y_range[2] + 1
  }
  
  # Create the plot
  plot <- ggplot(filtered_data_averaged, aes(x = full_date, y = valoreMisura)) +
    geom_line(color = "black", linewidth = 1) +
    geom_point(color = "hot pink", size = 5) +
    geom_hline(yintercept = average_valoreMisura, linetype = "dashed", color = "red", linewidth = 3) +
    labs(
      title = paste0(trait_name, " for siglaProvincia BZ"),
      x = NULL,
      y = NULL
    ) +
    theme_minimal(base_size = 15) +
    theme(
      axis.text.x = element_text(size = 14, angle = 45, hjust = 1),
      axis.text.y = element_text(size = 12),
      plot.margin = margin(10, 20, 15, 20)
    ) +
    scale_x_date(date_labels = "%Y-%m-%d", date_breaks = "1 day") +  # Ensure daily breaks
    scale_y_continuous(limits = c(y_min, y_max))
  
  # Save the plot
  ggsave(
    filename = paste0("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/figure3/", trait_name, "_plot.png"),
    plot = plot,
    width = 10,
    height = 8
  )
}

#################################################################################################################################
#################################################################################################################################
# SCC


# scc <- read.table("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/Somatic Cells Count (SCC).csv", header=T, sep=",")

# head(scc)

# scc <- scc %>%
#   filter(valoreMisura > 0)

# calculate_population_mean <- function(data) {
#   population_data <- data %>%
#     mutate(full_date = as.Date(full_date)) %>%
#     filter(
#       full_date >= as.Date("2024-09-06") & full_date <= as.Date("2024-09-13"),
#       siglaProvincia == "BZ"
#     ) %>%
#     group_by(full_date) %>%
#     summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")
  
#   mean(population_data$valoreMisura, na.rm = TRUE)
# }

# population_mean <- calculate_population_mean(scc)
# print(population_mean)

# filtered_data <- scc %>%
#   mutate(full_date = as.Date(full_date)) %>%
#   arrange(full_date) %>%
#   filter(
#     full_date >= as.Date("2024-09-06") & full_date <= as.Date("2024-09-13"),
#     siglaProvincia == "BZ",
#     idAnimale == "-9223372036848126976"
#   )

# filtered_data_averaged <- filtered_data %>%
#   group_by(full_date) %>%
#   summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")

# if (nrow(filtered_data_averaged) == 0) {
#   warning("No data available for the specified time frame for trait: ", file)
#   next
# }

# y_min <- min(filtered_data_averaged$valoreMisura) - 10
# y_max <- max(filtered_data_averaged$valoreMisura) + 10

# # Plot valoreMisura against full_date
# plot <- ggplot(filtered_data_averaged, aes(x = full_date, y = valoreMisura, group = 1)) +  # Add group = 1
#   geom_line(color = "black", size = 1) +  # Add black line to connect points
#   geom_point(color = "hot pink", size = 5) +
#   geom_hline(yintercept = population_mean, linetype = "dashed", color = "red", size = 3) +  # Add dashed red line at 200
#   labs(
#     title = "SCC plot",
#     x = NULL,
#     y = NULL
#   ) +
#   theme_minimal(base_size = 15) +
#   theme(
#     axis.text.x = element_text(size = 26, angle = 45, hjust = 1),
#     axis.text.y = element_text(size = 24),
#     plot.title = element_text(size = 28, hjust = 0.5),
#     plot.margin = margin(10, 40, 15, 45) 
#   ) + 
#   scale_x_date(date_labels = "%Y-%m-%d", date_breaks = "1 day") +  # Ensure equal spacing of x-axis
#   scale_y_continuous(limits = c(y_min, y_max))

# ggsave(
#   filename = "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/figure2/scc_plot.png",  # Update the file name
#   plot = plot,
#   width = 10,  # Adjust width
#   height = 8  # Adjust height
# )

# I needed to use threshold, not population means
# Load necessary libraries
library(dplyr)
library(ggplot2)

# Read in the data
scc <- read.table("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/Somatic Cells Count (SCC).csv", header = TRUE, sep = ",")

# Filter data to remove non-positive values
scc <- scc %>%
  filter(valoreMisura > 0)


# Filter data for specific animal and date range
filtered_data <- scc %>%
  mutate(full_date = as.Date(full_date)) %>%
  arrange(full_date) %>%
  filter(
    full_date >= as.Date("2024-09-06") & full_date <= as.Date("2024-09-13"),
    siglaProvincia == "BZ",
    idAnimale == "-9223372036848126976"
  )

# Group and average data by date
filtered_data_averaged <- filtered_data %>%
  group_by(full_date) %>%
  summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")

# Check if data is available
if (nrow(filtered_data_averaged) == 0) {
  warning("No data available for the specified time frame for trait: ", file)
  next
}

# Calculate y-axis limits
y_min <- min(filtered_data_averaged$valoreMisura) - 10
y_max <- max(filtered_data_averaged$valoreMisura) + 10

# Create plot
plot <- ggplot(filtered_data_averaged, aes(x = full_date, y = valoreMisura, group = 1)) +  # Add group = 1
  geom_line(color = "black", size = 1) +  # Add black line to connect points
  geom_point(color = "hot pink", size = 5) +
  geom_hline(yintercept = 200, linetype = "dashed", color = "red", size = 3) +  # Fixed threshold at 200
  labs(
    title = "SCC plot",
    x = NULL,
    y = NULL
  ) +
  theme_minimal(base_size = 15) +
  theme(
    axis.text.x = element_text(size = 26, angle = 45, hjust = 1),
    axis.text.y = element_text(size = 24),
    plot.title = element_text(size = 28, hjust = 0.5),
    plot.margin = margin(10, 40, 15, 45) 
  ) + 
  scale_x_date(date_labels = "%Y-%m-%d", date_breaks = "1 day") +  # Ensure equal spacing of x-axis
  scale_y_continuous(limits = c(y_min, y_max))

# Save plot
ggsave(
  filename = "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/figure2/scc_plot.png",
  plot = plot,
  width = 10,  # Adjust width
  height = 8   # Adjust height
)




#################################################################################################################################
#################################################################################################################################
# Acetone

# acetone <- read.table("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/Acetone.csv", header=T, sep=",")

# acetone <- acetone %>%
#   filter(valoreMisura > 0)

# calculate_population_mean <- function(data) {
#   population_data <- data %>%
#     mutate(full_date = as.Date(full_date)) %>%
#     filter(
#       full_date >= as.Date("2024-09-06") & full_date <= as.Date("2024-09-13"),
#       siglaProvincia == "BZ"
#     ) %>%
#     group_by(full_date) %>%
#     summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")
  
#   mean(population_data$valoreMisura, na.rm = TRUE)
# }

# population_mean <- calculate_population_mean(acetone)
# print(population_mean)

# filtered_data <- acetone %>%
#   mutate(full_date = as.Date(full_date)) %>%
#   arrange(full_date) %>%
#   filter(
#     full_date >= as.Date("2024-09-06") & full_date <= as.Date("2024-09-13"),
#     siglaProvincia == "BZ",
#     idAnimale == "-9223372036848126976"
#   )

# filtered_data_averaged <- filtered_data %>%
#   group_by(full_date) %>%
#   summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")

# if (nrow(filtered_data_averaged) == 0) {
#   warning("No data available for the specified time frame for trait: ", file)
#   next
# }

# y_min <- min(filtered_data_averaged$valoreMisura) - 0.05
# y_max <- max(filtered_data_averaged$valoreMisura) + 0.05

# # Plot valoreMisura against full_date
# plot <- ggplot(filtered_data_averaged, aes(x = full_date, y = valoreMisura, group = 1)) +  # Add group = 1
#   geom_line(color = "black", size = 1) +  # Add black line to connect points
#   geom_point(color = "hot pink", size = 5) +
#   geom_hline(yintercept = population_mean, linetype = "dashed", color = "red", size = 3) +  # Add dashed red line at 200
#   labs(
#     title = "Acetone plot",
#     x = NULL,
#     y = NULL
#   ) +
#   theme_minimal(base_size = 15) +
#   theme(
#     axis.text.x = element_text(size = 26, angle = 45, hjust = 1),
#     axis.text.y = element_text(size = 24),
#     plot.title = element_text(size = 28, hjust = 0.5),
#     plot.margin = margin(10, 40, 15, 45) 
#   ) + 
#   scale_x_date(date_labels = "%Y-%m-%d", date_breaks = "1 day") +  # Ensure equal spacing of x-axis
#   scale_y_continuous(limits = c(y_min, y_max))

# ggsave(
#   filename = "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/figure2/acetone_plot.png",  # Update the file name
#   plot = plot,
#   width = 10,  # Adjust width
#   height = 8  # Adjust height
# )


acetone <- read.table("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/Acetone.csv", header=T, sep=",")

acetone <- acetone %>%
  filter(valoreMisura > 0)

filtered_data <- acetone %>%
  mutate(full_date = as.Date(full_date)) %>%
  arrange(full_date) %>%
  filter(
    full_date >= as.Date("2024-09-06") & full_date <= as.Date("2024-09-13"),
    siglaProvincia == "BZ",
    idAnimale == "-9223372036848126976"
  )

filtered_data_averaged <- filtered_data %>%
  group_by(full_date) %>%
  summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")

if (nrow(filtered_data_averaged) == 0) {
  warning("No data available for the specified time frame for trait: ", file)
  next
}

y_min <- min(filtered_data_averaged$valoreMisura) - 0.05
y_max <- max(filtered_data_averaged$valoreMisura) + 0.5

# Plot valoreMisura against full_date
plot <- ggplot(filtered_data_averaged, aes(x = full_date, y = valoreMisura, group = 1)) +  # Add group = 1
  geom_line(color = "black", size = 1) +  # Add black line to connect points
  geom_point(color = "hot pink", size = 5) +
  geom_hline(yintercept = 0.7, linetype = "dashed", color = "red", size = 3) +  # Add dashed red line at 200
  labs(
    title = "Acetone plot",
    x = NULL,
    y = NULL
  ) +
  theme_minimal(base_size = 15) +
  theme(
    axis.text.x = element_text(size = 26, angle = 45, hjust = 1),
    axis.text.y = element_text(size = 24),
    plot.title = element_text(size = 28, hjust = 0.5),
    plot.margin = margin(10, 40, 15, 45) 
  ) + 
  scale_x_date(date_labels = "%Y-%m-%d", date_breaks = "1 day") +  # Ensure equal spacing of x-axis
  scale_y_continuous(limits = c(y_min, y_max))

ggsave(
  filename = "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/figure2/acetone_plot.png",  # Update the file name
  plot = plot,
  width = 10,  # Adjust width
  height = 8  # Adjust height
)



#################################################################################################################################
#################################################################################################################################
# BHBA

# bhba <- read.table("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/Î²-hydroxybutyrate (BHBA).csv", header=T, sep=",")

# bhba <- bhba %>%
#   filter(valoreMisura > 0)

# calculate_population_mean <- function(data) {
#   population_data <- data %>%
#     mutate(full_date = as.Date(full_date)) %>%
#     filter(
#       full_date >= as.Date("2024-09-06") & full_date <= as.Date("2024-09-13"),
#       siglaProvincia == "BZ"
#     ) %>%
#     group_by(full_date) %>%
#     summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")
  
#   mean(population_data$valoreMisura, na.rm = TRUE)
# }

# population_mean <- calculate_population_mean(acetone)
# print(population_mean)

# filtered_data <- bhba %>%
#   mutate(full_date = as.Date(full_date)) %>%
#   arrange(full_date) %>%
#   filter(
#     full_date >= as.Date("2024-09-06") & full_date <= as.Date("2024-09-13"),
#     siglaProvincia == "BZ",
#     idAnimale == "-9223372036848126976"
#   )

# filtered_data_averaged <- filtered_data %>%
#   group_by(full_date) %>%
#   summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")

# if (nrow(filtered_data_averaged) == 0) {
#   warning("No data available for the specified time frame for trait: ", file)
#   next
# }

# y_min <- min(filtered_data_averaged$valoreMisura) - 0.05
# y_max <- max(filtered_data_averaged$valoreMisura) + 0.05

# # Plot valoreMisura against full_date
# plot <- ggplot(filtered_data_averaged, aes(x = full_date, y = valoreMisura, group = 1)) +  # Add group = 1
#   geom_line(color = "black", size = 1) +  # Add black line to connect points
#   geom_point(color = "hot pink", size = 5) +
#   geom_hline(yintercept = population_mean, linetype = "dashed", color = "red", size = 3) +  # Add dashed red line at 200
#   labs(
#     title = "bhba plot",
#     x = NULL,
#     y = NULL
#   ) +
#   theme_minimal(base_size = 15) +
#   theme(
#     axis.text.x = element_text(size = 26, angle = 45, hjust = 1),
#     axis.text.y = element_text(size = 24),
#     plot.title = element_text(size = 28, hjust = 0.5),
#     plot.margin = margin(10, 40, 15, 45) 
#   ) + 
#   scale_x_date(date_labels = "%Y-%m-%d", date_breaks = "1 day") +  # Ensure equal spacing of x-axis
#   scale_y_continuous(limits = c(y_min, y_max))

# ggsave(
#   filename = "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/figure2/bhba_plot.png",  # Update the file name
#   plot = plot,
#   width = 10,  # Adjust width
#   height = 8  # Adjust height
# )


bhba <- read.table("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/Î²-hydroxybutyrate (BHBA).csv", header=T, sep=",")

bhba <- bhba %>%
  filter(valoreMisura > 0)

filtered_data <- bhba %>%
  mutate(full_date = as.Date(full_date)) %>%
  arrange(full_date) %>%
  filter(
    full_date >= as.Date("2024-09-06") & full_date <= as.Date("2024-09-13"),
    siglaProvincia == "BZ",
    idAnimale == "-9223372036848126976"
  )

filtered_data_averaged <- filtered_data %>%
  group_by(full_date) %>%
  summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")

if (nrow(filtered_data_averaged) == 0) {
  warning("No data available for the specified time frame for trait: ", file)
  next
}

y_min <- min(filtered_data_averaged$valoreMisura) - 0.05
y_max <- max(filtered_data_averaged$valoreMisura) + 0.8

# Plot valoreMisura against full_date
plot <- ggplot(filtered_data_averaged, aes(x = full_date, y = valoreMisura, group = 1)) +  # Add group = 1
  geom_line(color = "black", size = 1) +  # Add black line to connect points
  geom_point(color = "hot pink", size = 5) +
  geom_hline(yintercept = 1, linetype = "dashed", color = "red", size = 3) +  # Add dashed red line at 200
  labs(
    title = "bhba plot",
    x = NULL,
    y = NULL
  ) +
  theme_minimal(base_size = 15) +
  theme(
    axis.text.x = element_text(size = 26, angle = 45, hjust = 1),
    axis.text.y = element_text(size = 24),
    plot.title = element_text(size = 28, hjust = 0.5),
    plot.margin = margin(10, 40, 15, 45) 
  ) + 
  scale_x_date(date_labels = "%Y-%m-%d", date_breaks = "1 day") +  # Ensure equal spacing of x-axis
  scale_y_continuous(limits = c(y_min, y_max))

ggsave(
  filename = "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/figure2/bhba_plot.png",  # Update the file name
  plot = plot,
  width = 10,  # Adjust width
  height = 8  # Adjust height
)

################################################################################################################################################
# fat/lactose ratio
library(data.table)

fat = read.table("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/Fat.csv", header=T, sep=",")
lactose = read.table("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/Lactose.csv", header=T, sep=",")

filter_data <- function(data, start_date, end_date, province, animal_id) {
  data %>%
    mutate(full_date = as.Date(full_date)) %>%
    arrange(full_date) %>%
    filter(
      full_date >= as.Date(start_date) & full_date <= as.Date(end_date),
      siglaProvincia == province,
      idAnimale == animal_id
    )
}

calculate_daily_average <- function(filtered_data) {
  filtered_data %>%
    group_by(full_date) %>%
    summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")
}

# Filter data for specific criteria
filtered_data <- filter_data(
  data = fat, 
  start_date = "2024-09-06", 
  end_date = "2024-09-13", 
  province = "BZ", 
  animal_id = "-9223372036848126976"
)

# Calculate daily average from filtered data
averaged_fat <- calculate_daily_average(filtered_data)

# Filter data for specific criteria
filtered_data <- filter_data(
  data = fat, 
  start_date = "2024-09-06", 
  end_date = "2024-09-13", 
  province = "BZ", 
  animal_id = "-9223372036848126976"
)

averaged_lactose <- calculate_daily_average(filtered_data)

# View the result
print(averaged_lactose)
print(averaged_fat)

colnames(averaged_lactose)[2] <- "lactose"
colnames(averaged_fat)[2] <- "fat"

fat1_dt <- as.data.table(averaged_fat)
lactose1_dt <- as.data.table(averaged_lactose)

fat1_dt[, full_date := as.Date(full_date)]
lactose1_dt[, full_date := as.Date(full_date)]

s <- merge(fat1_dt, lactose1_dt, by = "full_date")
head(s)
# fat lactose ratio
s[, fat_lactose_ratio := fat / lactose]

plot <- ggplot(s, aes(x = as.Date(full_date), y = fat_lactose_ratio)) +
  geom_line(color = "black", size = 1) +  # Black line connecting the points
  geom_point(color = "hot pink", size = 5) +
  geom_hline(yintercept = 0.82, linetype = "dashed", color = "red", size = 3) +  # Add dashed red line at y = 0.82
  labs(
    title = "Fat-to-Lactose Ratio (Last 5 Days)",
    x = NULL,
    y = NULL
  ) +
  theme_minimal(base_size = 15) +
  theme(
    axis.text.x = element_text(size = 26, angle = 45, hjust = 1),  # Rotate x-axis labels
    axis.text.y = element_text(size = 24),  # Adjust y-axis text size
    plot.title = element_text(size = 22, hjust = 0.5),
    plot.margin = margin(t = 10, r = 10, b = 30, l = 30)) +
  scale_x_date(date_labels = "%Y-%m-%d", breaks = s$full_date)  # Show only relevant dates on x-axis

plot

ggsave(
  filename = "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/figure2/fat_lac_ratio_plot.png",
  plot = plot,
  width = 10,
  height = 8
)






























































##############################
##############################
# to check the values 
files <- c("Casein.csv", "Fat.csv", "Protein.csv", "Lactose.csv", 
           "Time to curd firmness (A30).csv", "Time to curd firmness (K20).csv", 
           "Rennet Coagulation time (R).csv")

#######
casein = read.table("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/Rennet Coagulation time (R).csv", header=T, sep=",")


casein_filtered <- casein %>%
  mutate(full_date = as.Date(full_date)) %>%  # Convert full_date to Date type
  arrange(full_date) %>%  # Arrange by full_date
  filter(
    full_date == as.Date("2024-09-07"),
    # full_date >= as.Date("2024-09-12") & full_date <= as.Date("2024-09-24"),  # Filter by date range
    siglaProvincia == "BZ",
    idAnimale == "-9223372036848126976"
      )
summary(casein_filtered$valoreMisura)

# casein_filtered_averaged <- casein_filtered %>%
# #   filter(full_date >= as.Date("2024-09-12") & full_date <= as.Date("2024-09-24")) %>%
#   group_by(full_date) %>%
#   summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop")


# # View the arranged data
# tail(casein_filtered_averaged, 7)

summary(casein_filtered$valoreMisura)







input_path <- "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/"
output_path <- "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/figure2/"
summary_stats <- read.csv("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/0report/descriptive_statistics_summary.csv")

files <- c("Casein.csv", "Fat.csv", "Protein.csv", "Lactose.csv", 
           "Time to curd firmness (A30).csv", "Time to curd firmness (K20).csv", 
           "Rennet Coagulation time (R).csv")

for (file in files) {
  # Read data
  data <- read.table(paste0(input_path, file), header = TRUE, sep = ",")
  
  # Filter and prepare data
  filtered_data <- data %>%
    mutate(full_date = as.Date(full_date)) %>%  # Convert full_date to Date type
    arrange(full_date) %>%  # Arrange by date
    filter(
      full_date >= as.Date("2024-09-12") & full_date <= as.Date("2024-09-24"),  # Filter date range
      siglaProvincia == "BZ",
      idAnimale == "-9223372036848126976"
    )
  
  # Average valoreMisura for each full_date
  filtered_data_averaged <- filtered_data %>%
    filter(valoreMisura > 0) %>%  # Exclude non-positive values
    group_by(full_date) %>%
    summarise(valoreMisura = mean(valoreMisura, na.rm = TRUE), .groups = "drop") 

}
#######################################################################

