import json
from collections import OrderedDict
from datetime import datetime

import pandas as pd
from tqdm import tqdm
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

BIRTH_FILE: str = "Input/Birth.csv"
ANIMAL_REGISTRY_FILE: str = "Input/Animal registry.csv"
CALVING_FILE: str = "Input/Calving.csv"
INSEMINATION_FILE: str = "Input/Insemination.csv"
PREGNANCY_DIAGNOSIS_FILE: str = "Input/Pregnancy Diagnosis.csv"
DRY_PERIOD_FILE: str = "Input/Dry Period.csv"
SLAUGHTER_FILE: str = "Input/Slaughter.csv"

BIRTH_DF = pd.read_csv(BIRTH_FILE, index_col=None)
ANIMAL_REGISTRY_DF = pd.read_csv(ANIMAL_REGISTRY_FILE, index_col=None)
CALVING_DF = pd.read_csv(CALVING_FILE, index_col=None)
INSEMINATION_DF = pd.read_csv(INSEMINATION_FILE, index_col=None)
PREGNANCY_DIAGNOSIS_DF = pd.read_csv(PREGNANCY_DIAGNOSIS_FILE, index_col=None)
DRY_PERIOD_DF = pd.read_csv(DRY_PERIOD_FILE, index_col=None)
SLAUGHTER_DF = pd.read_csv(SLAUGHTER_FILE, index_col=None)


def get_unique_animal_ids() -> list[str]:
    unique_ids = set()
    for current_df in [BIRTH_DF, ANIMAL_REGISTRY_DF, CALVING_DF, INSEMINATION_DF, PREGNANCY_DIAGNOSIS_DF, DRY_PERIOD_DF]:
        current_file_ids = set(current_df["idAnimale"])
        unique_ids = unique_ids.union(current_file_ids)

    return list(unique_ids)


def get_animal_birth_date(
        animal_id: str,
        birth_df: pd.DataFrame = BIRTH_DF
) -> datetime.date:
    birth_record = birth_df[birth_df["idAnimale"] == animal_id]
    if len(birth_record) == 1:
        birth_date_str = birth_record.iloc[0]["date_formatted"]
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        return birth_date
    else:
        return None


def get_animal_sex(
        animal_id: str,
        animal_registry_df: pd.DataFrame = ANIMAL_REGISTRY_DF
) -> str:
    sex_records = animal_registry_df[animal_registry_df["idAnimale"] == animal_id]
    sex_records = sex_records.fillna("")
    sex_str = ""
    if len(sex_records) == 1:
        sex_str = sex_records.iloc[0]["SessoSoggetto"]
    else:
        for sex_record in sex_records["SessoSoggetto"]:
            if sex_record:
                sex_str += sex_record.lower()
        if "f" in sex_str and "m" in sex_str:
            # print(f"Ambiguous sex: {sex_str} for animal_id: {animal_id}")
            return None
        sex_str = "f" if "f" in sex_str else "m"

    if sex_str.lower() in ["f", "m"]:
        sex = "Female" if sex_str.lower() == "f" else "Male"
        return sex
    else:
        return "Unknown"


def get_animal_insemination_records(
        animal_id: str,
        insemination_df: pd.DataFrame = INSEMINATION_DF,
) -> list[datetime.date]:
    insemination_records_df = insemination_df[insemination_df["idAnimale"] == animal_id]
    # if len(insemination_records_df) == 0:
        # print(f"No insemination record for animal_id: {animal_id}")
    insemination_records_str = insemination_records_df["DataInseminazione"]
    insemination_records = [
        datetime.strptime(insemination_record, "%Y-%m-%d").date()
        for insemination_record in insemination_records_str
    ]

    return sorted(insemination_records)


def get_animal_pregnancy_diagnosis_records(
        animal_id: str,
        pregnancy_diagnosis_df: pd.DataFrame = PREGNANCY_DIAGNOSIS_DF,
) -> list[datetime.date]:
    pregnancy_diagnosis_records_df = pregnancy_diagnosis_df[pregnancy_diagnosis_df["idAnimale"] == animal_id]
    # if pregnancy_diagnosis_records_df.empty:
        # print(f"No Pregnancy Diagnosis record for animal_id: {animal_id}")
    pregnancy_diagnosis_records_str = zip(
        pregnancy_diagnosis_records_df["DataDiagnosiGravidanza"],
        pregnancy_diagnosis_records_df["EsitoDiagnosiGravidanza"]
    )

    pregnancy_diagnosis_records = [
        (
            datetime.strptime(pregnancy_diagnosis_record, "%Y-%m-%d").date(),
            pregnancy_diagnosis_result.lower()
        ) for
        pregnancy_diagnosis_record, pregnancy_diagnosis_result in pregnancy_diagnosis_records_str
    ]

    return sorted(pregnancy_diagnosis_records)


def get_animal_dry_period_records(
        animal_id: str,
        dry_period_df: pd.DataFrame = DRY_PERIOD_DF,
) -> list[datetime.date]:
    dry_period_records_df = dry_period_df[dry_period_df["idAnimale"] == animal_id]
    # if dry_period_records_df.empty:
    #     print(f"No Dry Period record for animal_id: {animal_id}")
    dry_period_records_str = dry_period_records_df["DataAsciutta"]
    dry_period_records = [datetime.strptime(dry_period_record, "%Y-%m-%d").date() for dry_period_record in
                          dry_period_records_str]
    return sorted(dry_period_records)


def get_animal_calving_records(
        animal_id: str,
        calving_df: pd.DataFrame = CALVING_DF,
) -> list[datetime.date]:
    calving_records_df = calving_df[calving_df["idAnimale"] == animal_id]
    # if calving_records_df.empty:
    #     print(f"No Calving record for animal_id: {animal_id}")
    calving_records_str = calving_records_df["DataParto"]
    calving_records = [datetime.strptime(record_date, "%Y-%m-%d").date() for record_date in calving_records_str]

    return sorted(calving_records)

def get_animal_parity(
        animal_id: str,
        calving_df: pd.DataFrame = CALVING_DF,
) -> int:
    calving_record = calving_df[calving_df["idAnimale"] == animal_id]
    return len(calving_record)


def get_calf_mortality_rate(
        animal_id: str,
        calving_df: pd.DataFrame = CALVING_DF,
) -> float:
    calving_record = calving_df[calving_df["idAnimale"] == animal_id].infer_objects(copy=False).fillna(0.0)

    total_born_calves = (sum(calving_record["NumeroFemmineNateVive"]) + sum(calving_record["NumeroMaschiNatiVivi"]) +
                         sum(calving_record["NumeroFemmineNateMorte"]) + sum(calving_record["NumeroMaschiNatiMorti"]))
    total_dead_calves = sum(calving_record["NumeroFemmineNateMorte"]) + sum(calving_record["NumeroMaschiNatiMorti"])

    return total_dead_calves / total_born_calves if total_born_calves > 0 else None


def get_first_calving_age(
        birth_date: datetime.date,
        ordered_animal_life_events: OrderedDict[datetime.date, str]
) -> int:
    first_calving_age = None
    calving_dates = [calving_date for calving_date, event in ordered_animal_life_events.items() if event == "Calving"]
    if calving_dates and birth_date:
        first_calving_age = (calving_dates[0] - birth_date).days
    return first_calving_age


def get_average_calving_interval(
        ordered_animal_life_events: OrderedDict[datetime.date, str]
) -> float:
    calving_dates = [calving_date for calving_date, event in ordered_animal_life_events.items() if event == "Calving"]
    if len(calving_dates) > 1:
        calving_interval_sum = 0
        for i in range(len(calving_dates) - 1):
            calving_interval_sum += (calving_dates[i + 1] - calving_dates[i]).days
        return calving_interval_sum / (len(calving_dates) - 1)
    elif len(calving_dates) == 1:
        # print("Only one calving event for")
        return 0.0
    else:
        return None


if __name__ == "__main__":
    animals_df = pd.DataFrame(columns=[
        "idAnimale",
        "Sex",
        "Parity",
        "Calf_mortality_rate",
        "First Calving Age",
        "Average Calving Interval",
        "Animal Records",
        "Animal Life Events"
    ])
    useful_animals_df = pd.DataFrame(columns=[
        "idAnimale",
        "Sex",
        "Parity",
        "Calf_mortality_rate",
        "First Calving Age",
        "Average Calving Interval",
        "Animal Records",
        "Animal Life Events"
    ])

    unique_ids: list[str] = get_unique_animal_ids()
    # unique_ids = unique_ids[:100]
    for animal_id in tqdm(unique_ids, total=len(unique_ids), desc="Processing animals"):
        sex= get_animal_sex(animal_id)
        parity = get_animal_parity(animal_id)
        calf_mortality_rate = get_calf_mortality_rate(animal_id)

        animal_records = {
            "Birth": get_animal_birth_date(animal_id),
            "Insemination": get_animal_insemination_records(animal_id),
            "Pregnancy Diagnosis": get_animal_pregnancy_diagnosis_records(animal_id),
            "Calving": get_animal_calving_records(animal_id),
            "Dry Period": get_animal_dry_period_records(animal_id)
        }

        animal_life_events: dict[datetime.date, str] = {}
        if birth_date := animal_records["Birth"]:
            animal_life_events[birth_date] = "Birth"
        if insemination_records := animal_records["Insemination"]:
            for insemination_record in insemination_records:
                animal_life_events[insemination_record] = "Insemination"
        if pregnancy_diagnosis_records := animal_records["Pregnancy Diagnosis"]:
            for pregnancy_diagnosis_record, pregnancy_diagnosis_result in pregnancy_diagnosis_records:
                animal_life_events[pregnancy_diagnosis_record] = f"Pregnancy Diagnosis - {pregnancy_diagnosis_result}"
        if calving_records := animal_records["Calving"]:
            for calving_record in calving_records:
                animal_life_events[calving_record] = "Calving"
        if dry_period_records := animal_records["Dry Period"]:
            for dry_period_record in dry_period_records:
                animal_life_events[dry_period_record] = "Dry Period"
        ordered_animal_life_events: OrderedDict[datetime.date, str] = OrderedDict(sorted(animal_life_events.items()))

        animal_records_str = json.dumps({
            "Birth": animal_records["Birth"].isoformat() if animal_records["Birth"] else None,
            "Insemination": [
                record_date.isoformat() for record_date in animal_records["Insemination"]
            ] if animal_records["Insemination"] else None,
            "Pregnancy Diagnosis": [
                (record_date.isoformat(), record_result) for (record_date, record_result) in animal_records["Pregnancy Diagnosis"]
            ] if animal_records["Pregnancy Diagnosis"] else None,
            "Calving": [
                record_date.isoformat() for record_date in animal_records["Calving"]
            ] if animal_records["Calving"] else None,
            "Dry Period": [
                record_date.isoformat() for record_date in animal_records["Dry Period"]
            ] if animal_records["Dry Period"] else None
        })
        ordered_animal_life_events_str = {}
        for key, value in ordered_animal_life_events.items():
            ordered_animal_life_events_str[key.isoformat()] = value
        ordered_animal_life_events_str = json.dumps(ordered_animal_life_events_str)

        first_calving_age = get_first_calving_age(birth_date, ordered_animal_life_events)
        average_calving_interval = get_average_calving_interval(ordered_animal_life_events)

        animal = {
            "idAnimale": animal_id,
            "Sex": sex,
            "Parity": parity,
            "Calf_mortality_rate": calf_mortality_rate,
            "First Calving Age": first_calving_age,
            "Average Calving Interval": average_calving_interval,
            "Animal Records": animal_records_str,
            "Animal Life Events": ordered_animal_life_events_str,
        }
        animals_df.loc[len(animals_df)] = animal

        if (animal_records["Birth"] and animal_records["Insemination"] and animal_records["Pregnancy Diagnosis"] and
                animal_records["Calving"] and animal_records["Dry Period"]):
            print(animal_id, animal_records, ordered_animal_life_events, sep="\n")
            useful_animals_df.loc[len(useful_animals_df)] = animal

    animals_df.to_csv("animal_df.csv", index=None)
    useful_animals_df.to_csv("useful_animals_df.csv", index=None)
