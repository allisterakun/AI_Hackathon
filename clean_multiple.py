import os.path

import pandas as pd

CLEANED_DATA_FOLDER = "cleaned_data/"
OUTPUT_FOLDER = "cleaned_data/multiple_records/"

file_mapping = {
    "Urea": "anno",
    "Rennet Coagulation time (R)": "anno",
    "Time to curd firmness (K20)": "anno",
    "Time to curd firmness (A30)": "anno",
    "Index of dairy attitude (IAC)": "anno",
    "Î²-hydroxybutyrate (BHBA)": "anno",
    "Acetone": "anno",
    "Saturated Fatty acid (SFA)": "anno",
    "Total unsaturated Fatty Acid (UFA)": "anno",
    "Electrical conductivity": "anno",
    "Newly synthesised fatty acids": "anno",
    "Mixed Fatty Acids": "anno",
    "Preformed Fatty Acids": "anno",
    "PH": "anno",
    "Stearic Acid (C18_0)": "anno",
    "Vaccenic acid (C18_1)": "anno",
    "Freezing Point": "anno",
    "Casein": "anno",
    "Lactose": "anno",
    "Milk IBR analysis": "DataAnalisiIbr",
    "DISCC analysis": "DataAnalisiDscc",
    "Progesterone Milk Analysis": "DataAnalisiPag",
    "Citric Acid": "anno",
    "Fat": "anno",
    "Protein": "anno",
    "Somatic Cells Count (SCC)": "anno",
    "Somatic Cells Index": "AnnoDiRiferimento",
    "Dry Period": "DataAsciutta",
    "Abortion": "DataAborto",
    "Pregnancy Diagnosis": "DataDiagnosiGravidanza",
    "Calving": "DataParto",
    "Insemination": "DataInseminazione",
    "Animal registry": "?",   # ?
    "Daily milking": "DataSessioneMungitura",
    "Average conductivity": "DataRilevamentoConducibilita"
}


def clean_data(file_name: str) -> tuple[int, int, int, float]:
    file_path = os.path.join(CLEANED_DATA_FOLDER, f"{file_name}.csv")
    df = pd.read_csv(file_path, index_col=None)

    original_num_records = len(df)

    df["full_date"] = [f"{anno}-{mese:02d}-{giorno:02d}" for anno, mese, giorno in zip(
        df["anno"], df["mese"], df["giorno"]
    )]
    df["identifying_column"] = [f"{_id}_{full_date}" for _id, full_date in zip(
        df["idAnimale"], df["full_date"])]

    new_df = df.drop_duplicates(subset=["identifying_column"], keep=False)
    new_df.to_csv(os.path.join(OUTPUT_FOLDER, f"{file_name}.csv"))

    unique_num_records = len(new_df)

    unique_ids = len(new_df.drop_duplicates(subset=["idAnimale"], keep='first'))

    return original_num_records, unique_num_records, unique_ids, unique_ids / unique_num_records


if __name__ == "__main__":
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    report_output_folder = os.path.join(OUTPUT_FOLDER, "0report/")
    os.makedirs(report_output_folder, exist_ok=True)

    files = list(file_mapping.keys())
    report = pd.DataFrame(columns=["File", "Original_row_number", "After_row_number", "Unique_ids",
                                   "Proportion_unique_id"])

    for file in files:
        original, after, unique, proportion = clean_data(file)
        report.loc[len(report)] = [f"{file}.csv", original, after, unique, proportion]

    report.to_csv(os.path.join(report_output_folder, "unique_id_report.csv"))
