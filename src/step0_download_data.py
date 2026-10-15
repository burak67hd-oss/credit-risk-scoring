"""Step 0 — Download the dataset (UCI "Default of Credit Card Clients", CC BY 4.0).

The CSV is not stored in the repository: this script fetches it once into data/.
"""
import urllib.request

from utils import DATA_CSV

URL = ("https://raw.githubusercontent.com/MatteoM95/Default-of-Credit-Card-Clients-Dataset-Analisys/"
       "main/dataset/default_of_credit_card_clients.csv")


def download_data() -> None:
    if DATA_CSV.exists():
        print(f"{DATA_CSV.name} already present")
        return
    DATA_CSV.parent.mkdir(exist_ok=True)
    urllib.request.urlretrieve(URL, DATA_CSV)
    print(f"Downloaded {DATA_CSV.name}")


if __name__ == "__main__":
    download_data()
