from scipy.optimize import curve_fit
from scipy.stats import binomtest
from handlers.DataHandler import load_csv_as_dataframe
import matplotlib.pyplot as plt
import numpy as np


def multivar(x, a, b, c):
    return a * x[0] + b * x[1] / 100 + c


def linear(x, a, b):
    return a * x + b


def get_fit_params(func, xdata, ydata):
    popt, pcov = curve_fit(func, xdata, ydata)
    return popt


def graph(func, xdata, ydata):
    popt = get_fit_params(func, xdata, ydata)
    x = np.linspace(0, 1, 100)
    y = linear(x, popt[0], popt[1])
    plt.plot(xdata, ydata, linestyle='', marker='.')
    plt.plot(x, x)
    plt.plot(x, y, linestyle='--')
    plt.show()


def t_test(k, n, p):
    return binomtest(k, n, p, 'two-sided')


def run_fits():
    df = load_csv_as_dataframe('combat_sample_data.csv', '../../tests/tests')
    x = (df.get('pexp').values, df.get('level').values)
    y = df.get('p').values
    print(get_fit_params(multivar, x, y))
    print(get_fit_params(linear, df.get('pexp').values, df.get('p').values))
    graph(linear, df.get('pexp').values, df.get('p').values)


def run_test():
    df = load_csv_as_dataframe('combat_sample_data.csv', '../../tests/tests')
    xdata, ydata = (df.get('pexp').values, df.get('level').values), df.get('p').values
    a, b, c = get_fit_params(multivar, xdata, ydata)
    print(f'{a:.5} * p + {b:.4} * levels + {c:.4}')
    for index in range(len(df)):
        ''''''
        x = df.get('pexp').values[index], df.get('level').values[index]
        p = multivar(x, a, b, c)
        '''
        xdata, ydata = df.get('pexp').values, df.get('p').values
        a, b = get_fit_params(linear, xdata, ydata)
        x = df.get('pexp').values[index]
        p = linear(x, a, b)
        '''
        k, n = df.get('crit').values[index], df.get('total').values[index]
        pvalue = t_test(k, n, p).pvalue
        print(f'{p} - {ydata[index]} - {pvalue > 0.05}')


run_test()