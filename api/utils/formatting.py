import math


def format_int(num):
    m = int(math.log10(num) // 3)
    suffixes = ['', 'k', 'M', 'G', 'T', 'P']
    return f'{num / 1000.0 ** m:.{4}f}{suffixes[m]}'
