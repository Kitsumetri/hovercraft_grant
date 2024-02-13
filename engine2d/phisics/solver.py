import numpy as np

def solve_system_euler(m, p, S, g, F_a, n, p_a, W, Q_in, Q_out, I, l, alpha, t_start, t_end, dt):
    num_steps = int((t_end - t_start) / dt)

    # Создаем массивы для хранения значений
    t_values = np.linspace(t_start, t_end, num_steps)
    y_values = np.zeros(num_steps)
    dp_values = np.zeros(num_steps)
    gamm_values = np.zeros(num_steps)

    # Начальные условия
    y_values[0] = 0.0
    dp_values[0] = 0.0
    gamm_values[0] = 0.0

    # Итеративно применяем метод Эйлера для решения системы уравнений
    for i in range(1, num_steps):
        # Рассчитываем новые значения
        y_prime = y_values[i - 1] + dt * (dp_values[i - 1] / m)
        dp_prime = dp_values[i - 1] + dt * (n * p_a / W * (Q_in - Q_out - (dp_values[i - 1] / m)))
        gamm_prime = gamm_values[i - 1] + dt * (F_a * l * np.cos(alpha) / I)

        # Обновляем значения в массивах
        y_values[i] = y_prime
        dp_values[i] = dp_prime
        gamm_values[i] = gamm_prime

    return t_values, y_values, dp_values, gamm_values


# Пример использования функции
t_start = 0
t_end = 100
dt = 0.01
m = 8000
p = 80
S = 40
g = 9.81
F_a = g * 1000 * 40  # ro g V
n = 1.4
p_a = 1013
W = 7.0

# Dynamic
Q_in = 10.0
Q_out = 9.0

I = 1_200_00
l = 6

alpha = np.pi / 4

t_values, y_values, dp_values, gamm_values = solve_system_euler(m, p, S, g, F_a, n, p_a, W, Q_in, Q_out, I, l, alpha, t_start, t_end, dt)

# Визуализация результатов (пример)
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))

plt.subplot(3, 1, 1)
plt.plot(t_values, y_values)
plt.title('y(t)')
plt.xlabel('Time')
plt.ylabel('Position')

plt.subplot(3, 1, 2)
plt.plot(t_values, dp_values)
plt.title('dp/dt')
plt.xlabel('Time')
plt.ylabel('Change in p')

plt.subplot(3, 1, 3)
plt.plot(t_values, gamm_values)
plt.title('gamm(t)')
plt.xlabel('Time')
plt.ylabel('Angular position')

plt.tight_layout()
plt.show()
