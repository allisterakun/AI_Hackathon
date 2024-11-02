import os

import pandas as pd
from tqdm.auto import tqdm

RAW_DATA_FOLDER = "raw_data/"
OUTPUT_FOLDER = "combined_data/"


def load_and_filter_all_csvs_in_folder(folder: str, specie: str, breed: str) -> pd.DataFrame:
    result = pd.DataFrame()

    all_csv_files = os.listdir(folder)

    for j in tqdm(range(len(all_csv_files)), desc=f"{folder}", position=1, leave=False):
        csv_path = os.path.join(folder, all_csv_files[j])
        if not all_csv_files[j].endswith(".csv"):
            print(f"Unexpected file {csv_path}")
            continue
        temp_df = pd.read_csv(csv_path, low_memory=False, index_col=None)
        columns = list(temp_df.columns)
        if "codiceSpecieAIA" not in columns or "codiceRazzaAIA" not in columns:
            print(folder, all_csv_files[j])
            continue

        temp_df['codiceRazzaAIA'] = temp_df['codiceRazzaAIA'].astype(str)
        temp_df = temp_df[(temp_df["codiceSpecieAIA"] == specie) & (temp_df["codiceRazzaAIA"] == str(breed))]

        result = pd.concat([result, temp_df], ignore_index=True)

    return result


if __name__ == "__main__":
    dataset_folders = os.listdir(RAW_DATA_FOLDER)

    for i in tqdm(range(len(dataset_folders)), desc="All Datasets", position=0):
        dataset = dataset_folders[i]
        dataset_folder = os.path.join(RAW_DATA_FOLDER, dataset)
        if os.path.isdir(dataset_folder):
            cleaned = load_and_filter_all_csvs_in_folder(dataset_folder, "C4", "11")
            cleaned.to_csv(os.path.join(OUTPUT_FOLDER, f"{dataset}.csv"), index=False)
