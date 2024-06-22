from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Any
from dataclasses import dataclass

from app_utils import Parameters
from numba import jit, njit
from math import sqrt


@jit(nopython=True, fastmath=True)
def F_x_jit(A, B, x):
    up = (B[1] - A[1]) * (x ** 2 / 2 - A[0] * x)
    down = B[0] - A[0]
    return up / down + A[1] * x


@jit(nopython=True, fastmath=True)
def get_S_gap_jit(UP, h):
    return max(0, UP[1] - h)


@jit(fastmath=True)
def get_Q_in_jit(a, b, c, p):
    D = b ** 2 - 4 * a * (c - p)
    root1 = (-b - sqrt(D)) / (2 * a)
    root2 = (-b + sqrt(D)) / (2 * a)
    return max(root1, root2)


@jit(fastmath=True)
def get_Q_out_jit(xi, p, rho, S_gap):
    return xi * np.sqrt(2 * p / rho) * S_gap


@jit(fastmath=True)
def get_cylinder_volume_jit(up_y, V_c, S, h):
    if up_y <= 0:
        return V_c

    if up_y >= h:
        return 0

    V_upper_part = S * (h - up_y)
    return V_c - V_upper_part


@jit(fastmath=True)
def get_d2y_dt2_jit(Fp, Fa, Fm, m):
    return (Fp + Fa - Fm) / m


@dataclass
class Point:
    x: int | float
    y: int | float

    def to_array(self) -> np.array:
        return np.array([self.x, self.y], dtype=np.float32)


class SystemOfEquations:
    def __init__(self,
                 params: Parameters,
                 t_end: int | float = 1_000,
                 eps: float = 0.01) -> None:

        self.params = params
        self.eps = eps
        self.current_iteration = 0

        self.p = (params.m * params.g) / params.S
        self.gamma = 0
        self.y = params.k
        self.W = params.S * params.k
        self.S_gap = 0

        self.dW_dt = 0

        self.t_array = np.arange(0, t_end, eps)

        self.y_array = np.zeros_like(self.t_array)
        self.y_array[0] = self.y

        self.p_array = np.zeros_like(self.t_array)
        self.p_array[0] = self.p

        self.w_array = np.zeros_like(self.t_array)
        self.w_array[0] = self.W

        self.gamma_array = np.zeros_like(self.t_array)
        self.gamma_array[0] = self.gamma

        self.A = Point(x=-self.params.l, y=self.y)
        self.B = Point(x=self.params.l, y=self.y)

        self.circle_S = np.pi * (self.params.r ** 2)
        self.V_cylinder = self.circle_S * self.params.h

    @staticmethod
    def F_x(A: Point, B: Point, x: int | float) -> int | float:
        return F_x_jit(A.to_array(), B.to_array(), x)

    def get_W(self, A: Point, B: Point, down: int | float, up: int | float) -> int | float:
        return self.F_x(A, B, up) - self.F_x(A, B, down)

    def get_cylinder_volume(self, upper_point: Point) -> int | float:
        return get_cylinder_volume_jit(upper_point.y, self.V_cylinder, self.circle_S, self.params.h)

    def get_S_gap(self, upper_point: Point) -> int | float:
        return get_S_gap_jit(upper_point.to_array(), self.params.h)

    def solve(self):
        self.current_iteration = self.t_array.shape[0]
        for idx in tqdm(range(1, self.current_iteration)):
            ###################
            dp_dt = self.get_dp_dt(W=self.W,
                                   Q_in=self.get_Q_in(),
                                   Q_out=self.get_Q_out(),
                                   dW_dt=self.dW_dt) * self.eps

            self.p = self.clamp(value=self.p + dp_dt,
                                min_value=600,
                                max_value=2964)

            self.W = self.get_W(A=self.A,
                                B=self.B,
                                down=self.A.x + self.params.r,
                                up=self.B.x - self.params.r)

            self.dW_dt = self.W - self.w_array[idx - 1]
            self.S_gap = (get_S_gap_jit(self.A.to_array(), self.params.h) +
                          get_S_gap_jit(self.B.to_array(), self.params.h))

            self.w_array[idx] = self.W
            self.p_array[idx] = self.p
            ###################

            V = self.get_cylinder_volume(self.A) + self.get_cylinder_volume(self.B)
            d2y_dt2 = self.get_d2y_dt2(Fp=self.get_F_p(),
                                       Fm=self.params.m * self.params.g,
                                       Fa=self.get_F_a(V)) * self.eps
            self.y += d2y_dt2
            self.y_array[idx] = self.y
            ###################

            d2gamma_dt2 = self.get_d2gamma_d2t(Fa=self.get_F_a(V),
                                               cos_a=self.get_cos_alpha(self.A.to_array())) * self.eps

            # FIXME: нужно крутить точки
            self.A.y += d2y_dt2
            self.B.y += d2y_dt2
            # #########

            self.gamma += d2gamma_dt2
            self.gamma_array[idx] = self.gamma

    def get_d2y_dt2(self,
                    Fp: int | float,
                    Fm: int | float,
                    Fa: int | float) -> float:
        return get_d2y_dt2_jit(Fp, Fa, Fm, self.params.m)

    def get_dp_dt(self,
                  W: int | float,
                  Q_in: int | float,
                  Q_out: float,
                  dW_dt: int | float | Any) -> float:
        first_half = (self.params.n * self.params.p_a) / W
        second_half = Q_in - Q_out - dW_dt
        return first_half * second_half

    def get_d2gamma_d2t(self,
                        Fa: int | float,
                        cos_a: float) -> float:
        return (Fa * self.params.l * cos_a) / self.params.I

    def get_F_p(self) -> int | float:
        return self.params.S * self.p

    def get_F_a(self, V: int | float) -> int | float:
        return self.params.rho * self.params.g * V

    def get_Q_in(self) -> int | float:
        return get_Q_in_jit(self.params.a, self.params.b, self.params.c, self.p)

    @staticmethod
    @njit(fastmath=True)
    def get_cos_alpha(v1: np.array,
                      v2: Optional[np.array] = None) -> float:
        v2 = np.array([0, 1], dtype=np.float32) if v2 is None else v2
        dot_prod = np.dot(v1, v2)
        magnitude1, magnitude2 = np.linalg.norm(v1), np.linalg.norm(v2)

        return dot_prod / (magnitude1 * magnitude2)

    def get_Q_out(self) -> float:
        return get_Q_out_jit(self.params.xi, self.p, self.params.rho, self.S_gap)

    @staticmethod
    @jit(fastmath=True)
    def clamp(value: int | float,
              min_value: int | float,
              max_value: int | float) -> int | float:
        return min(max(value, min_value), max_value)

    def __repr__(self) -> str:
        separator = "\n" + "+" + ("-" * 50) + "\n"
        repr_str = (
            f"{separator}"
            f"| System of Equations"
            f"{separator}"
            f"| Params: {self.params}"
            f"{separator}"
            f"| Solution (Iteration: {self.current_iteration}):"
            f"{separator}"
            f"| p = {self.p}\n"
            f"| y = {self.y}\n"
            f"| γ = {self.gamma}\n"
            f"| W = {self.W}\n"
            f"| A: {self.A}\n"
            f"| B: {self.B}\n"
            f"| S_gap: {self.S_gap}"
            f"{separator}"
        )
        return repr_str

    def plot(self, max_elem: Optional[int] = None) -> None:

        if self.current_iteration == 0:
            raise RuntimeError("Use .solve() method first")

        if max_elem is None:
            max_elem = self.t_array.shape[0]

        y = self.y_array[:max_elem]
        p = self.p_array[:max_elem]
        gamma = self.gamma_array[:max_elem]
        W = self.w_array[:max_elem]
        t = self.t_array[:max_elem]

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


def main() -> None:
    equations = SystemOfEquations(Parameters(h=1, r=0.9),
                                  t_end=10,
                                  eps=1e-4)
    print(equations)
    equations.solve()
    print(equations)
    equations.plot()


if __name__ == '__main__':
    main()
