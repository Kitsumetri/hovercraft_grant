from tqdm import tqdm
import numpy as np
from utils import Parameters
import matplotlib.pyplot as plt
from cmath import sqrt

S_gap = 5
W = 2


def F_arch(params):
    return params.m * params.g + 300


# DONE
def cos_alpha(OA):
    OA_vector = np.array(OA)
    F_arc_vector = np.array([0, 1])
    return np.dot(OA_vector, F_arc_vector)


# DONE
def Q_in(p, params):
    a, b, c = params.a, params.b, params.c

    D = b ** 2 - 4 * a * (c - p)
    root1 = (-b - sqrt(D)) / (2 * a)
    root2 = (-b + sqrt(D)) / (2 * a)
    return max(root1, root2, key=lambda x: x.real)


# DONE
def Q_out(p, params):
    return params.xi * np.sqrt(2 * p / params.rho) * S_gap


def system_of_equations(y_p_g, params):
    y, p, gamma = y_p_g
    Fm = params.m * params.g

    F_arch_current = F_arch(params)
    Q_in_current = Q_in(p, params)
    Q_out_current = Q_out(p, params)
    dW_dt = 0.5

    dy2_dt2 = (p * params.S - Fm + F_arch_current) / params.m

    dp_dt = (params.n * params.p_a) / W * (Q_in_current - Q_out_current - dW_dt)

    d_gamma2_dt2 = (F_arch_current * params.l * cos_alpha((0, y))) / params.I

    return np.array([dy2_dt2, dp_dt, d_gamma2_dt2])  # [y, p, gamma]


def euler_method(system_func, y0, t0, tf, dt, params):
    time_steps = int((tf - t0) / dt)
    t = np.linspace(t0, tf, time_steps, dtype=np.float64)
    y_p_g = np.zeros((time_steps, 3), dtype=np.float64)  # [y, p, gamma]
    y_p_g[0] = y0

    i = 1
    with tqdm(total=time_steps - 1) as pbar:
        while i < time_steps:
            y_p_g[i] = y_p_g[i - 1] + system_func(y_p_g[i - 1], params) * dt
            i += 1
            pbar.update(1)

    return t, y_p_g


def solve(params: Parameters):
    k = 0.7
    p = params.m * params.g / params.S
    initial_conditions = np.array([k, p, 0])  # [y, p, gamma]
    dt = 0.01
    t0 = 0
    tf = 1_000
    t, y_v_p = euler_method(system_of_equations, initial_conditions, t0, tf, dt, params)
    plot(t, y_v_p)


def plot(t, y_p_g):
    y = y_p_g[:, 0]
    p = y_p_g[:, 1]
    gamma = y_p_g[:, 2]

    plt.figure(figsize=(14, 4))
    plt.subplot(1, 3, 1)
    plt.grid()
    plt.plot(t, y)
    plt.title('Y')
    plt.xlabel('Time (s)')
    plt.ylabel('Y')

    plt.subplot(1, 3, 2)
    plt.plot(t, gamma)
    plt.grid()
    plt.title('Gamma')
    plt.xlabel('Time (s)')
    plt.ylabel('Gamma')

    # График давления
    plt.subplot(1, 3, 3)
    plt.plot(t, p)
    plt.grid()
    plt.title('P')
    plt.xlabel('Time (s)')
    plt.ylabel('P')

    plt.tight_layout()
    plt.show()
