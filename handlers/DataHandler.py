import csv


def write_to_csv(data, name='data.csv', location='../data/'):
    path = location + name
    with open(path, 'w', newline='') as csvfile:
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


if __name__ == '__main__':
    test_data = [
        {'time': 1, 'data': 3},
        {'time': 2, 'data': 5},
        {'time': 3, 'data': 6},
        {'time': 4, 'data': 2}
    ]

    write_to_csv(test_data, path='../data/test_data.csv')