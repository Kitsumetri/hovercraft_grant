import numpy as np
import matplotlib.pyplot as plt

np.set_printoptions(formatter={'float_kind': '{:f}'.format})

data = {
    "Q": [0, 5.583299446, 11.16659889, 16.74989834, 22.33319779, 25.12484751, 27.91649723, 33.49979668, 37.96643624],
    "P": [2808.802744, 2964.847341, 2902.429503, 2715.175986, 2496.713551, 2325.064494, 2059.788679, 1279.565695, 592.9694683]
}

Q = np.array(data["Q"])
P = np.array(data["P"])

coefficients = np.polyfit(Q, P, 2)
p = np.poly1d(coefficients)

Q_fit = np.linspace(min(Q), max(Q), 100)
P_fit = p(Q_fit)

print(*coefficients)
plt.scatter(Q, P, label='Исходные данные', color='blue')
plt.plot(Q_fit, P_fit, label='Аппроксимирующая парабола', color='red')
plt.legend()
plt.grid(True)
plt.show()


