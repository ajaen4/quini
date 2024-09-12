from f_scrapper.actions import run_scrapper
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv("../../.env")
    run_scrapper()
