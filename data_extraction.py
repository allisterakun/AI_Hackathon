import os.path

import numpy as np
import pandas as pd
from tqdm import tqdm

INPUT_DIR = "cleaned_data/multiple_records/"
OUTPUT_DIR = "extracted_data/"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_interested_columns(file_path: str = "Unnecessary files.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path, sheet_name="Sheet1", index_col=None)

    df = df[df["variable1"].notnull()]
    df.drop(["Num of unique_ids"], axis=1, inplace=True)

    return df


def extract_data(file_name: str, interested_column: str) -> None:
    df = pd.read_csv(os.path.join(INPUT_DIR, file_name), index_col=None)
    if interested_column in ["valoreMisura", "IcssIndiceCelluleSomatiche"]:
        df = df[["idAnimale", interested_column]]

        result_df = pd.DataFrame(columns=["idAnimale", "mean", "std", "count"])

        unique_animal_ids = list(set(df["idAnimale"]))
        for animal_id in unique_animal_ids:
            temp_df = df[df["idAnimale"] == animal_id]
            data_entries = temp_df[interested_column]

            result_df.loc[len(result_df)] = {
                "idAnimale": animal_id,
                "mean": np.mean(data_entries),
                "std": np.std(data_entries),
                "count": len(data_entries)
            }
        result_df.to_csv(os.path.join(OUTPUT_DIR, file_name), index=False)
        # raise KeyboardInterrupt

    elif file_name == "Pregnancy Diagnosis.csv":
        df = df[["idAnimale", interested_column]]

        result_df = pd.DataFrame(columns=["idAnimale", "num_positive_diagnoses"])

        unique_animal_ids = list(set(df["idAnimale"]))
        for animal_id in unique_animal_ids:
            temp_df = df[df["idAnimale"] == animal_id]
            positive_diagnoses = len(temp_df[temp_df[interested_column] == "POSITIVA"])

            result_df.loc[len(result_df)] = {
                "idAnimale": animal_id,
                "num_positive_diagnoses": positive_diagnoses
            }
        result_df.to_csv(os.path.join(OUTPUT_DIR, file_name), index=False)
    elif "," in interested_column:
        interested_columns = ["idAnimale"] + interested_column.replace(" ", "").split(",")
        df = df[interested_columns]

        result_df = pd.DataFrame(columns=["idAnimale", "num_successful_pregnancy", "num_problematic_pregnancy"])

        unique_animal_ids = list(set(df["idAnimale"]))
        for animal_id in unique_animal_ids:
            temp_df = df[df["idAnimale"] == animal_id]
            temp_df = temp_df.fillna(0)

            sum_male_calves_born_alive = sum(temp_df["NumeroMaschiNatiVivi"])
            sum_female_calves_born_alive = sum(temp_df["NumeroFemmineNateVive"])
            sum_male_calves_born_dead = sum(temp_df["NumeroMaschiNatiMorti"])
            sum_female_calves_born_dead = sum(temp_df["NumeroFemmineNateMorte"])

            result_df.loc[len(result_df)] = {
                "idAnimale": animal_id,
                "num_successful_pregnancy": int(sum_male_calves_born_alive + sum_female_calves_born_alive),
                "num_problematic_pregnancy": int(sum_male_calves_born_dead + sum_female_calves_born_dead)
            }
        result_df.to_csv(os.path.join(OUTPUT_DIR, file_name), index=False)


if __name__ == "__main__":
    file_mapping = load_interested_columns()
    for _, row_data in tqdm(file_mapping.iterrows(),
                            total=file_mapping.shape[0],
                            desc="Extracting data... "
                            ):
        extract_data(row_data["File"], row_data["variable1"])
