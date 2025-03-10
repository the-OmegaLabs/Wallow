import math


def _create_gaussian_kernel(radius):
    size = 2 * radius + 1
    kernel = []
    sigma = radius / 3
    s = 2 * sigma ** 2
    total = 0.0

    for y in range(-radius, radius + 1):
        row = []
        for x in range(-radius, radius + 1):
            val = (1 / (math.pi * s)) * math.exp(-(x ** 2 + y ** 2) / s)
            row.append(val)
            total += val
        kernel.append(row)

    return [[val / total for val in row] for row in kernel]
