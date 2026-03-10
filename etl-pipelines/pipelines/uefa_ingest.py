import pandas as pd

def load_ufaa_data(file_path: str):
    # Sample ingestion
    df = pd.read_csv(file_path)
    # TODO: Cleaning & normalization
    return df

if __name__ == "__main__":
    data = load_ufaa_data("data_samples/ufaa_sample.csv")
    print(data.head())
