import csv
import pandas as pd
import os


def write_to_csv(data, name='logs.csv', location='../logs/'):
    path = os.path.join(location, name)
    with open(path, 'w', newline='') as csvfile:
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def load_csv_as_dataframe(name, location='../logs/'):
    path = os.path.join(location, name)
    df = pd.read_csv(path)
    return df


def load_csv_as_records(name, location='../logs/'):
    path = os.path.join(location, name)
    df = pd.read_csv(path)
    return df.to_dict(orient='records')


def fillna_values(series, fill_values):
    if len(fill_values) == 0:
        raise ValueError('Parameter \'fill_values\' cannot be an empty set.')
    fill_i = 0
    series = series.copy(deep=True)
    for i in range(len(series)):
        if pd.isna(series.loc[i]):
            series.loc[i] = fill_values[fill_i]
            fill_i += 1
            if fill_i == len(fill_values):
                break
    return series


def add_to_csv_column(name, column_name, new_values, location='../logs/', print_log=False):
    path = os.path.join(location, name)
    df = pd.read_csv(path)
    n_missing = df[column_name].isna().sum()
    if n_missing > 0:
        df[column_name] = fillna_values(df[column_name], new_values[:n_missing])
    df = pd.concat([df, pd.DataFrame({column_name: new_values[n_missing:]})], ignore_index=True)
    df.to_csv(path, index=False)
    if print_log:
        print(f"Updated {column_name} in {path}\n{df}")


def add_data_to_csv(filename: str, location: str, data: dict):
    path = os.path.join(location, filename)
    df = pd.read_csv(path)
    data = pd.DataFrame(data)
    df = pd.concat([df, data], ignore_index=True)
    df.to_csv(path, index=False)


if __name__ == '__main__':
    add_to_csv_column('combat_sample_data.csv', 'SC-52', tuple([1, 2]), '../../tests/tests/')
