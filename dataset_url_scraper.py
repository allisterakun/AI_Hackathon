import csv
import os
from typing import TypedDict
from time import sleep
from zipfile import ZipFile

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver

import pandas as pd

DATASETS_URL = "https://opendata.leo-italy.eu/portale/dataset/search"
INTERESTED_DATASETS = [
    "Urea",
    "Rennet Coagulation time (R)",
    "Time to curd firmness (K20)",
    "Time to curd firmness (A30)",
    "Index of dairy attitude (IAC)",
    "β-hydroxybutyrate (BHBA)",
    "Acetone",
    "Saturated Fatty acid (SFA)",
    "Total unsaturated Fatty Acid (UFA)",
    "Electrical conductivity",
    "Newly synthesised fatty acids",
    "Mixed Fatty Acids",
    "Preformed Fatty Acids",
    "PH",
    "Stearic Acid (C18:0)",
    "Vaccenic acid (C18:1)",
    "Freezing Point",
    "Casein",
    "Lactose",
    "Milk IBR analysis",
    "DISCC analysis",
    "Progesterone Milk Analysis",
    "Citric Acid",
    "Fat",
    "Protein",
    "Somatic Cells Count (SCC)",
    "Somatic Cells Index",
    "Days Open Index",
    "Index Longevity",
    "Index Persistence Lactation",
    "Female Fertility Index",
    "Genetic Index Prolificity",
    "Calving Interval index",
    "Dual purpose Index",
    "Udder Health Index",
    "Indirect Feed Efficiency Index",
    "Heat Tolerance Index",
    "Milkability index",
    "Enteric Disease Resistance Index",
    "Respiratory Diseases Resistance Index",
    "Locomotion Index",
    "Fitness Index",
    "Dual purpose Index",
    "Productivity Index Functionality and Type (genomic)",
    "Health Economic Index",
    "Parmesan Cheese Sustainability and Cheesemaking Index",
    "Mammal Composite Index",
    "Mungibility Index",
    "Milk performance recordings",
    "Lactation",
    "Average conductivity",
    "Daily milking",
    "Daily Weather Recording",
    "Dry Period",
    "Abortion",
    "Culling",
    "Unique Identification",
    "Pregnancy Diagnosis",
    "Calving",
    "Insemination",
    "Slaughter",
    "Birth",
    "Animal registry",
    "Mother-relatedweeding"
]


class DatasetURL(TypedDict):
    dataset_name: str
    dataset_url: str


def setup_scraping_driver(headless: bool = True) -> webdriver:
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang=en")
    options.add_experimental_option(
        "prefs",
        {
            "safebrowsing.enabled": True,
        },
    )
    driver = webdriver.Chrome(
        options=options
    )
    return driver


def setup_download_driver(dataset_name: str, headless: bool = True) -> tuple[webdriver, str]:
    if ":" in dataset_name:
        dataset_name = "_".join(dataset_name.split(":"))

    options = webdriver.ChromeOptions()
    download_directory = os.path.join(os.getcwd(), dataset_name)
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_directory,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )
    driver = webdriver.Chrome(
        options=options
    )
    return driver, download_directory


def change_language_to_english(driver: webdriver) -> webdriver:
    language_dropdown_button = driver.find_element(
        By.XPATH,
        "/html/body/app-root/app-header/header/div/nav/div[2]/div/div/div/div/div/div/a"
    )
    WebDriverWait(driver, 20).until(expected_conditions.element_to_be_clickable(language_dropdown_button))
    driver.execute_script("return arguments[0].scrollIntoView(true);", language_dropdown_button)
    language_dropdown_button.click()
    sleep(1)

    english_button = driver.find_element(
        By.XPATH,
        "/html/body/app-root/app-header/header/div/nav/div[2]/div/div/div/div/div/div/div/div/div/div/ul/li[2]/a"
    )
    WebDriverWait(driver, 20).until(expected_conditions.element_to_be_clickable(english_button))
    driver.execute_script("return arguments[0].scrollIntoView(true);", english_button)
    english_button.click()
    sleep(1)

    return driver


def scrape_current_page(driver: webdriver) -> list[DatasetURL]:
    results: list[DatasetURL] = []

    current_page_datasets = driver.find_elements(By.TAG_NAME, "h5")

    for dataset in current_page_datasets:
        dataset_name, dataset_url = dataset.text, dataset.find_element(By.TAG_NAME, "a").get_attribute("href")

        if dataset_name not in INTERESTED_DATASETS:
            continue

        results.append(DatasetURL(
            dataset_name=dataset.text,
            dataset_url=dataset.find_element(By.TAG_NAME, "a").get_attribute("href")
        ))
    return results


def go_to_next_page(driver: webdriver) -> webdriver:
    page_buttons_ul = driver.find_element(By.CLASS_NAME, "pagination").find_elements(By.TAG_NAME, "li")
    next_page_button = page_buttons_ul[-1].find_element(By.TAG_NAME, "a")
    WebDriverWait(driver, 20).until(expected_conditions.element_to_be_clickable(next_page_button))
    driver.execute_script("return arguments[0].scrollIntoView(true);", next_page_button)
    next_page_button.click()
    sleep(1)
    return driver


def get_total_csv_number(driver: webdriver) -> int:
    return int(driver.find_element(
        By.XPATH,
        '//*[@id="it-it-dataset-distribuzioni-value"]/div[1]/div[1]/div[1]/div/div[2]'
    ).text)


def get_year_options(driver: webdriver) -> list:
    select_element = driver.find_element(
        By.XPATH,
        '//*[@id="it-it-dataset-distribuzioni-value"]/div[1]/div[2]/div[1]/div/select'
    )
    options = select_element.find_elements(By.TAG_NAME, "option")[1:]

    return options


def go_to_year_option(driver: webdriver, year_option) -> webdriver:
    WebDriverWait(driver, 20).until(expected_conditions.element_to_be_clickable(year_option))
    driver.execute_script("return arguments[0].scrollIntoView(true);", year_option)
    year_option.click()
    sleep(1)

    return driver


def download_zip(driver: webdriver, li_element, download_directory: str) -> str:
    download_csv_button = li_element.find_elements(By.TAG_NAME, "a")[0]
    download_csv_href: str = download_csv_button.get_attribute("href")

    zip_file_name = download_csv_href.split("/")[-1]
    zip_file_path = os.path.join(download_directory, zip_file_name)
    if zip_file_name.startswith("CM_"):
        return ""

    WebDriverWait(driver, 20).until(expected_conditions.element_to_be_clickable(download_csv_button))
    driver.execute_script("return arguments[0].scrollIntoView(true);", download_csv_button)
    download_csv_button.click()

    while not os.path.exists(zip_file_path):
        sleep(1)
    return zip_file_path


def unzip_file(download_directory: str, zip_file_path: str) -> None:
    with ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(download_directory)
    zip_ref.close()
    os.remove(zip_file_path)


def scrape_dataset_urls(url: str, headless: bool = True) -> list[DatasetURL]:
    results: list[DatasetURL] = []

    driver = setup_scraping_driver(headless=headless)
    try:
        driver.get(url)

        driver = change_language_to_english(driver)

        current_page_results = scrape_current_page(driver)
        results += current_page_results

        # for dataset in current_page_results:
        #     result_dataset_names = [ds["dataset_name"] for ds in results]
        #     if dataset["dataset_name"] in result_dataset_names:
        #         dataset["dataset_name"] = f"{dataset['dataset_name']}_2"
        #         print(dataset)
        #     results.append(dataset)

        for _ in range(14):
            driver = go_to_next_page(driver)

            current_page_results = scrape_current_page(driver)
            results += current_page_results

            # for dataset in current_page_results:
            #     result_dataset_names = [ds["dataset_name"] for ds in results]
            #     if dataset["dataset_name"] in result_dataset_names:
            #         dataset["dataset_name"] = f"{dataset['dataset_name']}_2"
            #         print(dataset)
            #     results.append(dataset)

    finally:
        driver.quit()
    return results


def load_dataset_urls(file_path: str) -> list[DatasetURL]:
    results = []
    with open(file_path) as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)
        for row in csv_reader:
            results.append(DatasetURL(
                dataset_name=row[0],
                dataset_url=row[1]
            ))

    return results


def download_current_page_csvs(driver: webdriver, download_directory: str) -> bool:
    current_page_ul = driver.find_element(By.XPATH, '//*[@id="it-it-dataset-distribuzioni-value"]/div[2]/ul')
    list_li = current_page_ul.find_elements(By.TAG_NAME, "li")
    for li in list_li:
        zip_file_path = download_zip(driver, li, download_directory)

        if zip_file_path and os.path.isfile(zip_file_path):
            unzip_file(download_directory, zip_file_path)
        else:
            return False
    return True


def download_csvs(dataset: DatasetURL) -> None:
    dataset_name, dataset_url = dataset["dataset_name"], dataset["dataset_url"]

    driver, download_dir = setup_download_driver(dataset_name)
    try:
        driver.get(dataset_url)
        change_language_to_english(driver)
        total_files = get_total_csv_number(driver)
        year_options = get_year_options(driver)
        year_options_int = [year_option.text for year_option in year_options]

        print(f"Scraping {dataset_name}.\t\tTotal files: {total_files} with years: {year_options_int}")

        for option in year_options:
            print(f"\tScraping year {option.text}")
            driver = go_to_year_option(driver, option)
            download_status = download_current_page_csvs(driver, download_dir)
            if not download_status:
                print(f"{dataset_name} has files starting with 'CM_', moving on to the next dataset.")
                break

    finally:
        driver.quit()

    print(f"{dataset_name} complete!")


if __name__ == "__main__":
    # dataset_urls = scrape_dataset_urls(DATASETS_URL)
    # dataset_urls_df = pd.DataFrame.from_records(dataset_urls)
    # dataset_urls_df.to_csv("dataset_urls.csv", index=False)

    dataset_urls = load_dataset_urls("dataset_urls.csv")
    dataset_urls = dataset_urls[14:]

    for dataset in dataset_urls:
        download_csvs(dataset)

