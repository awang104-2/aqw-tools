import csv
import pandas as pd


def write_to_csv(data, name='data.csv', location='../data/'):
    path = location + name
    with open(path, 'w', newline='') as csvfile:
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def load_csv_as_dataframe(name, location='../data/'):
    path = location + name
    df = pd.read_csv(path)
    return df


def load_csv_as_records(name, location='../data/'):
    path = location + name
    df = pd.read_csv(path)
    return df.to_dict(orient='records')
