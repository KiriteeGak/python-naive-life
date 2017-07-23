import numpy as np


def initial_energy_generation():
    e = np.random.normal(0.5, float(1) / 3, size=None)
    return e if 0 < e <= 1 else (0 if e <= 0 else 1)


def get_reduced_energy(current, jump_distance, scaling=0.01):
    e = current - scaling * jump_distance
    return e if e >= 0 else 0
