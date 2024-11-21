from dotenv import load_dotenv
import os

load_dotenv(".env")
os.environ["ENV"] = "dev"

if __name__ == "__main__":
    from f_data_uploader.actions import run_data_uploader

    run_data_uploader()
