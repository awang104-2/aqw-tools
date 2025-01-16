import matplotlib.pyplot as plt
from src.handlers.DataHandler import *


def graph(datafile, x_name, y_name):
    data = load_csv_as_records(datafile)
    fieldnames = list(data[0].keys())
    error_trigger = False
    for name in [x_name, y_name]:
        if not (name in fieldnames):
            error_trigger = True
            print('Error: the following column name was not found:', name)
    if error_trigger:
        return
    else:
        x, y = ([], [])
        for record in data:
            x.append(record[x_name])
            y.append(record[y_name])
        plt.plot(x, y)
        plt.xlabel(x_name)
        plt.ylabel(y_name)
        plt.title(x_name + ' vs. ' + y_name)
        plt.show()


if __name__ == '__main__':
    graph('cpu_data.csv', 'time', 'cpu usage')
