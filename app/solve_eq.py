from tqdm import tqdm
import numpy as np
from utils import Parameters
import matplotlib.pyplot as plt
from cmath import sqrt


# TESTED
def get_single_balloon_V(r, h, y, k):
    # r - радиус цилиндра
    # h - высота цилиндра
    # y - координата Y центра масс судна
    # k - клиренс (расстояние между судном и водой)

    def cylinder_volume(h_full):
        return np.pi * (r ** 2) * h_full

    if y <= 0:  # баллоны полностью под водой
        return cylinder_volume(h)
    elif y >= h:  # баллоны полностью над водой
        return 0
    else:  # баллоны частично над водой
        return cylinder_volume(h - k)


def get_F_a(k, y, r, L, rho, g):
    h = 10
    V1 = get_single_balloon_V(r, h, y, k)
    V2 = get_single_balloon_V(r, h, y, k)

    V_total = (V1 + V2) * L

    F_arch = rho * g * V_total
    return F_arch


# TESTED
def get_cos_alpha(u, v=np.array([0, 1])):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))


# TESTED
def Q_in(p, params):
    a, b, c = params.a, params.b, params.c

    D = b ** 2 - 4 * a * (c - p)
    root1 = (-b - sqrt(D)) / (2 * a)
    root2 = (-b + sqrt(D)) / (2 * a)
    return max(root1, root2, key=lambda x: x.real).real


def Q_out(p, params, S_gap):
    return params.xi * np.sqrt(2 * p / params.rho) * S_gap


# TESTED
def clamp(value, borders: tuple[int | float, int | float]) -> int | float:
    if value < borders[0]:
        return borders[0]

    if value > borders[1]:
        return borders[1]
    return value


def calculate_S_gap(k, y, r):
    # Для каждого баллона проверяем, находится ли он полностью или частично над водой
    if y <= -r + k:  # Баллон касается воды или полностью погружен
        S_a_gap = 0
        S_b_gap = 0
    else:  # Баллон полностью или частично над водой
        # Расстояние от самой нижней точки баллона до уровня воды
        S_a_gap = max(0, k + y - r)
        S_b_gap = S_a_gap  # Предполагаем симметричное расположение баллонов

    # Общее S_gap - сумма для обоих баллонов
    S_gap = S_a_gap + S_b_gap
    return S_gap


def calculate_W(k, y, r, L, S_gap):
    h_balloons = 2 * r
    if y <= k - r:  # Если баллоны полностью погружены или касаются воды
        W = 0
    else:
        a = L - 2 * r
        b = L - 2 * (r - S_gap)  # Уменьшаем на высоту воды, если баллоны не полностью погружены
        b = max(0, b)
        W = (a + b) / 2 * (h_balloons - S_gap)  # Площадь трапеции
    return W


# TESTED
def get_F_m(params: Parameters):
    return params.m * params.g


def system_of_equations(y_p_g, params, k=0.7, r=1.5, L=10.0):
    y, p, gamma, W_prev = y_p_g
    S_gap = calculate_S_gap(k, y, r)

    F_a = get_F_a(k, y, r, L, params.rho, params.g)

    p = clamp(p, (600, 2964))

    Fm = get_F_m(params)

    Q_in_current = Q_in(p, params)
    Q_out_current = Q_out(p, params, S_gap)

    W = calculate_W(k, y, r, L, S_gap)
    dW_dt = (W - W_prev) / 0.01

    F_p = p * params.S
    dy2_dt2 = (F_p - Fm + F_a) / params.m

    dp_dt = (params.n * params.p_a) / W * (Q_in_current - Q_out_current - dW_dt)

    cos_alpha = get_cos_alpha(np.array([0, y]))
    d_gamma2_dt2 = (F_a * params.l * cos_alpha) / params.I

    return np.array([dy2_dt2, dp_dt, d_gamma2_dt2, dW_dt])


def euler_method(system_func, y0, t0, tf, dt, params):
    time_steps = int((tf - t0) / dt)
    t = np.linspace(t0, tf, time_steps, dtype=np.float64)
    y_p_g = np.zeros((time_steps, 4), dtype=np.float64)  # [y, p, gamma, W]
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
    W = params.S * k
    initial_conditions = np.array([k, p, 0, W])  # [y, p, gamma, W]
    dt = 0.01
    t0 = 0
    tf = 1_000
    t, y_v_p = euler_method(system_of_equations, initial_conditions, t0, tf, dt, params)
    plot(t, y_v_p)


def plot(t, y_p_g):
    y = y_p_g[:, 0]
    p = y_p_g[:, 1]
    gamma = y_p_g[:, 2]
    W = y_p_g[:, 3]

    plt.figure(figsize=(18, 8))
    plt.subplot(2, 2, 1)
    plt.grid()
    plt.plot(t, y)
    plt.title('Y')
    plt.xlabel('Time (s)')
    plt.ylabel('Y')

    plt.subplot(2, 2, 2)
    plt.plot(t, gamma)
    plt.grid()
    plt.title('Gamma')
    plt.xlabel('Time (s)')
    plt.ylabel('Gamma')

    plt.subplot(2, 2, 3)
    plt.plot(t, p)
    plt.grid()
    plt.title('P')
    plt.xlabel('Time (s)')
    plt.ylabel('P')

    plt.subplot(2, 2, 4)
    plt.plot(t, W)
    plt.grid()
    plt.title('W')
    plt.xlabel('Time (s)')
    plt.ylabel('W')

    plt.tight_layout()
    plt.show()
