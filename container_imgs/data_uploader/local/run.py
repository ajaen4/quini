from dotenv import load_dotenv

load_dotenv(".env")

if __name__ == "__main__":
    from f_data_uploader.actions import run_data_uploader

    run_data_uploader()
