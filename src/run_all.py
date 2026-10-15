"""Run the full pipeline: download -> database -> SQL analysis -> models."""
from step0_download_data import download_data
from step1_build_database import build_database
from step2_sql_analysis import run_analysis
from step3_model import run_models

if __name__ == "__main__":
    download_data()
    build_database()
    run_analysis()
    run_models()
