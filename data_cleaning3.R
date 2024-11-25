library(dplyr)

# Define the file path
input_path <- "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/"
output_path <- "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/single_record/"
report_path <- paste0(output_path, "0report/")

if (!dir.exists(output_path)) {
  dir.create(output_path)
}
if (!dir.exists(report_path)) {
  dir.create(report_path)
}

# Initialize a data frame to store the report
report <- data.frame(
  File = character(),
  Original_row_number = integer(),
  Unique_row_number = integer(),
  Proportion_unique_id = numeric(),
  stringsAsFactors = FALSE
)

# List of files
files <- c("Index Longevity.csv", 
           "Index Persistence Lactation.csv", 
           "Dual purpose Index.csv", 
           "Culling.csv", 
           "Slaughter.csv",
           "Unique Identification.csv")

# Loop through files to read and process
for (file in files) {
    # Read the file
    data <- read.table(paste0(input_path, file), header = TRUE, sep = ",")
    
    original_row_number <- nrow(data)
    
    # Count unique ids
    count <- data %>% 
        group_by(idAnimale) %>%
        summarise(count = n())
    
    # Find entries with a unique id
    unique_ids <- count %>% 
    filter(count == 1) %>% 
    pull(idAnimale)
  
  # Subset data to only include rows with unique idAnimale
    data_unique <- data %>% 
    filter(idAnimale %in% unique_ids)

    unique_row_number <- nrow(data_unique)
    proportion_unique_id <- unique_row_number / original_row_number
    
    write.csv(data_unique, 
            file = paste0(output_path, file), 
            row.names = FALSE)

    # Print file name and number of unique ids
    cat("Processed file saved as:", paste0(output_path, file), "\n")
    
    # Append the results to the report data frame
    report <- rbind(report, data.frame(
    File = file,
    Original_row_number = original_row_number,
    Unique_row_number = unique_row_number,
    Proportion_unique_id = round(proportion_unique_id, 4)
  ))
}

# Save the report as a CSV file in the report directory
write.csv(report, file = paste0(report_path, "unique_id_report.csv"), row.names = FALSE, quote=FALSE)

cat("Report saved as:", paste0(report_path, "unique_id_report.csv"), "\n")


#################################################################
#################################################################
# Birth.csv -> cannot remove all of duplicated animals even though there are multiple entries for one animal
# -> need to decide whether we keep the first entry or last entry or what

birth = read.table("C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/Birth.csv", header=T, sep=",") #43,206

count = birth %>%
group_by(idAnimale) %>%
summarise(count = n())

birth$date_formatted <- as.Date(paste(birth$anno, birth$mese, birth$giorno, sep = "-"), format = "%Y-%m-%d")

birth_unique <- birth %>%
  arrange(date_formatted) %>%
  distinct(idAnimale, .keep_all = TRUE)

# nrow(birth_unique) #5,112

write.csv(birth_unique, 
            file = paste0(output_path, "Birth.csv"), 
            row.names = FALSE)

unique_row_number <- nrow(birth_unique)
proportion_unique_id <- unique_row_number / original_row_number

report <- rbind(report, data.frame(
  File = "Birth.csv",
  Original_row_number = original_row_number,
  Unique_row_number = unique_row_number,
  Proportion_unique_id = round(proportion_unique_id, 4)
))

write.csv(report, file = paste0(report_path, "unique_id_report.csv"), row.names = FALSE, quote=FALSE)


# #validation
# birth_unique[which(birth_unique$idAnimale == "-9223372036799170560"),]

