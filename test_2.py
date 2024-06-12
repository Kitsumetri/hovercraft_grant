# import matplotlib.pyplot as plt
# import numpy as np
#
# dt = 0.01
# t0 = 0
# tf = 1_000
#
# time_steps = int((tf - t0) / dt)
#
# t = np.linspace(t0, tf, time_steps, dtype=np.float64)
#
# y = np.array([0.7] + [0.85 for _ in range(time_steps - 1)])
# gamma = np.array([0] + [0.0025 for _ in range(time_steps - 1)])
# p = np.array([1744.0] + [1790 for _ in range(time_steps - 1)])
#
# plt.figure(figsize=(18, 8))
# plt.subplot(2, 2, 1)
# plt.grid()
# plt.plot(t, y)
# plt.title('Y')
# plt.xlabel('Time (s)')
# plt.ylabel('Y')
#
# plt.subplot(2, 2, 2)
# plt.plot(t, gamma)
# plt.grid()
# plt.title('Gamma')
# plt.xlabel('Time (s)')
# plt.ylabel('Gamma')
#
# plt.subplot(2, 2, 3)
# plt.plot(t, p)
# plt.grid()
# plt.title('P')
# plt.xlabel('Time (s)')
# plt.ylabel('P')
#
# plt.tight_layout()
# plt.show()
