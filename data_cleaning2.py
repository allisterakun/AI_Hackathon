# remove NA's for the column of interest

import os
import pandas as pd
from tqdm.auto import tqdm

# Define the path to the folder containing the CSV files
COMBINED_DATA_FOLDER = r"C:\Users\holic\Box\AI Hackathon\AI_Hackathon\combined_data"
OUTPUT_FOLDER = r"C:\Users\holic\Box\AI Hackathon\AI_Hackathon\cleaned_data"
REPORT_FILE = os.path.join(OUTPUT_FOLDER, "cleaning_report.csv")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# file names : the important variable (column name of interest)
file_column_mapping = {
    "Urea.csv": "valoreMisura",
    "Rennet Coagulation time (R).csv": "valoreMisura",
    "Time to curd firmness (K20).csv": "valoreMisura",
    "Time to curd firmness (A30).csv": "valoreMisura",
    "Index of dairy attitude (IAC).csv": "valoreMisura",
    "Î²-hydroxybutyrate (BHBA).csv": "valoreMisura",
    "Acetone.csv": "valoreMisura",
    "Saturated Fatty acid (SFA).csv": "valoreMisura",
    "Total unsaturated Fatty Acid (UFA).csv": "valoreMisura",
    "Electrical conductivity.csv": "valoreMisura",
    "Newly synthesised fatty acids.csv": "valoreMisura",
    "Mixed Fatty Acids.csv": "valoreMisura",
    "Preformed Fatty Acids.csv": "valoreMisura",
    "PH.csv": "valoreMisura",
    "Stearic Acid (C18_0).csv": "valoreMisura",
    "Vaccenic acid (C18_1).csv": "valoreMisura",
    "Freezing Point.csv": "valoreMisura",
    "Casein.csv": "valoreMisura",
    "Lactose.csv": "valoreMisura",
    "Milk IBR analysis.csv": "Ibr",
    "DISCC analysis.csv": "CelluleSomaticheDifferenzialiDscc",
    "Progesterone Milk Analysis.csv": "PagDiagnosiDiGravidanza",
    "Citric Acid.csv": "valoreMisura",
    "Fat.csv": "valoreMisura",
    "Protein.csv": "valoreMisura",
    "Somatic Cells Count (SCC).csv": "valoreMisura",
    "Somatic Cells Index.csv": "IcssIndiceCelluleSomatiche",
    "Days Open Index.csv": "IdoIndiceDaysOpen",
    "Index Longevity.csv": "IlvIndiceLongevita",
    "Index Persistence Lactation.csv": "IpersIndicePersistenzaLattazione",
    "Calving Interval index.csv": "IpIndiceInterparto",
    "Dual purpose Index.csv": "IcdaIndiceComplessivoDupliceAttitudine",
    "Dry Period.csv": "DataAsciutta",
    "Culling.csv": "DataEliminazione",
    "Pregnancy Diagnosis.csv": "DataDiagnosiGravidanza",
    "Calving.csv": "DataParto",
    "Insemination.csv": "DataInseminazione",
    "Slaughter.csv": "PesoCarcassa",
    "Birth.csv": "idAnimale",
    "Animal registry.csv": "idAnimale",
    "Daily milking.csv": "Mungitura",
    "Average conductivity.csv": "ConducibilitaMedia",
    "Unique Identification.csv": "IdentificazioneSoggetto"
}

def clean_data_files(folder: str, output_folder: str, file_column_map: dict):
    report = []  # List to store report data for each file

    for filename, important_var in tqdm(file_column_map.items(), desc="Processing Files"):
        file_path = os.path.join(folder, filename)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"File {filename} not found in {folder}")
            continue
        
        # Load the CSV file
        df = pd.read_csv(file_path, low_memory=False)
        
        # Check if the important variable column exists in the DataFrame
        if important_var not in df.columns:
            print(f"Column {important_var} not found in {filename}")
            continue

        # Count the initial rows and rows with any form of missing data (NaN, "NA", or empty string)
        initial_count = len(df)
        na_count = df[important_var].isna().sum() + (df[important_var] == "NA").sum() + (df[important_var] == "").sum()
        
        df = df[~df[important_var].isna() & (df[important_var] != "NA") & (df[important_var] != "")]
        
        # Calculate the cleaned row count and proportion removed
        cleaned_count = len(df)
        proportion_removed = na_count / initial_count if initial_count > 0 else 0

        # Save the cleaned data to the output folder
        output_path = os.path.join(output_folder, filename)
        df.to_csv(output_path, index=False)

        # Append report data
        report.append({
            "file_name": filename,
            "initial_count": initial_count,
            "na_count": na_count,
            "cleaned_count": cleaned_count,
            "proportion_removed": round(proportion_removed, 4)
        })
        print(f"Cleaned {filename} and saved to {output_path}")

    # Create a DataFrame for the report and save it as a CSV
    report_df = pd.DataFrame(report)
    report_df.to_csv(REPORT_FILE, index=False)
    print(f"Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    clean_data_files(COMBINED_DATA_FOLDER, OUTPUT_FOLDER, file_column_mapping)

    
## Need to check ##
# file Vaccenic acid (C18:1).csv not found in C:\Users\holic\Box\AI Hackathon\AI_Hackathon\combined_data -> was Vaccenic acid (C18_1).csv
# file Stearic Acid (C18:0).csv not found in C:\Users\holic\Box\AI Hackathon\AI_Hackathon\combined_data -> was Stearic Acid (C18_0).csv
# file β-idrossibutirrato (BHBA).csv not found in C:\Users\holic\Box\AI Hackathon\AI_Hackathon\combined_data -> was Î²-hydroxybutyrate (BHBA).csv
# Column DataAsciutta: DryOffDate not found in Dry Period.csv -> only DataAsciutta column
# Column MotivoDiIngresso not found in Animal registry.csv -> idAnimale
# Calving.csv -> DataParto column was used
# Birth.csv -> idAnimale column was used