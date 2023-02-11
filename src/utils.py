from typing import List
import matplotlib.pyplot as plt
import numpy as np
from os import path

def range_is_subset(range1, range2):
    '''Returns True if range1 is a subset of range2'''
    return range1[0] >= range2[0] and range1[-1] <= range2[-1]

def round_to_next_multiple_of_10(number: float or int) -> int:
    rounded = round(int(number)/10)*10
    return rounded if rounded >= number else rounded+10

def plot_great_composite_curve(T: List[float], Q: List[float], dir_path: str) -> None:
    Qutilh = Q[0]
    Qutilc = Q[-1]
    plt.plot(Q, T, 'k', linewidth=0.5)
    if (Qutilh != 0):
        plt.text(Qutilh/2, T[0] - 5, f"QHU = {Qutilh} kW", color='r', ha='center', va='center')
        plt.plot((0, Qutilh), 2*[T[0]], 'r', linewidth=1)
    if (Qutilc != 0):
        plt.text(Qutilc/2, T[-1] + 5, f"QCU = {Qutilc} kW", color='b', ha='center', va='center')
        plt.plot((0, Qutilc), 2*[T[-1]], 'b', linewidth=1)
    plt.xlim(0, round_to_next_multiple_of_10(max(Q)))
    plt.ylim(round_to_next_multiple_of_10(min(T)-10), round_to_next_multiple_of_10(max(T)))
    plt.yticks(np.arange(min(T)-10, max(T)+11, 10))
    plt.xticks(np.arange(min(Q), max(Q)+11, 10))
    plt.xlabel("H (kW)")
    plt.ylabel("T (°C)")
    plt.title("Great Composite Curve")
    plt.grid()
    plt.savefig(path.abspath(path.join(dir_path, "great_composite_curve.jpeg")), dpi=800)
    plt.close()

def plot_composite_curve(hot_Q, hot_T, cold_Q, cold_T, dir_path):
    plt.plot(hot_Q, hot_T, 'r', linewidth=0.5)
    plt.plot(cold_Q, cold_T, 'b', linewidth=0.5)
    plt.xlim(0, round_to_next_multiple_of_10(max(cold_Q)+10))
    plt.ylim(round_to_next_multiple_of_10(min(cold_T)-10), round_to_next_multiple_of_10(max(hot_T)+10))
    plt.xlabel("H (kW)")
    plt.ylabel("T (°C)")
    plt.title("Composite Curve")
    plt.grid()
    plt.savefig(path.abspath(path.join(dir_path, "composite_curve.jpeg")), dpi=800)
    plt.close()