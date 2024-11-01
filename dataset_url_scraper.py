import collections
from typing import TypedDict
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver

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


def setup_driver(headless: bool = True) -> webdriver:
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


def scrape_dataset_urls(url: str, headless: bool = True) -> list[DatasetURL]:
    results: list[DatasetURL] = []

    driver = setup_driver(headless=headless)
    try:
        driver.get(url)

        driver = change_language_to_english(driver)
        current_page_results = scrape_current_page(driver)

        for dataset in current_page_results:
            result_dataset_names = [ds["dataset_name"] for ds in results]
            if dataset["dataset_name"] in result_dataset_names:
                dataset["dataset_name"] = f"{dataset['dataset_name']}_2"
                print(dataset)
            results.append(dataset)
        # results += current_page_results

        for _ in range(14):
            driver = go_to_next_page(driver)

            current_page_results = scrape_current_page(driver)

            for dataset in current_page_results:
                result_dataset_names = [ds["dataset_name"] for ds in results]
                if dataset["dataset_name"] in result_dataset_names:
                    dataset["dataset_name"] = f"{dataset['dataset_name']}_2"
                    print(dataset)
                results.append(dataset)

    finally:
        driver.quit()
    return results


if __name__ == "__main__":
    res = scrape_dataset_urls(DATASETS_URL)
    dataset_names = [ds["dataset_name"] for ds in res]

    counter = collections.Counter(dataset_names)
    print(counter)

    print(len(set(dataset_names)), len(set(INTERESTED_DATASETS)))
