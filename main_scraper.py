# from config import COUNTRY, COUNTRY_CODE, KEYWORDS
# from scrapper.job_scraper import get_all_data
# from scrapper.api_scraper import enrich_dataset
# import pandas as pd
# import os

# def main():
#     all_jobs = []
#     for kw in KEYWORDS:
#         print(f"Scraping for keyword: {kw}")
#         df = get_all_data(kw, COUNTRY, COUNTRY_CODE)
#         all_jobs.append(df)

#     df_links = pd.concat(all_jobs).reset_index(drop=True)
#     df_details = enrich_dataset(df_links)

#     os.makedirs("data", exist_ok=True)
#     df_details.to_csv("data/data.csv", index=False)
#     print("Export terminé : data/data.csv")
#     print(f"Nombre total d'offres collectées : {len(jobs)}")

# if __name__ == "__main__":
#     main()
from config import COUNTRY, COUNTRY_CODE, KEYWORDS
from scrapper.job_scraper import get_all_data
from scrapper.api_scraper import enrich_dataset
import pandas as pd
import os

def main():
    all_jobs = []
    for kw in KEYWORDS:
        print(f"Scraping for keyword: {kw}")
        df = get_all_data(kw, COUNTRY, COUNTRY_CODE)
        all_jobs.append(df)

    df_links = pd.concat(all_jobs).reset_index(drop=True)
    df_details = enrich_dataset(df_links)

    os.makedirs("data", exist_ok=True)
    df_details.to_csv("data/data.csv", index=False)
    print("Export terminé : data/data.csv")
    print(f"Nombre total d'offres collectées : {len(df_details)}")

if __name__ == "__main__":
    main()
