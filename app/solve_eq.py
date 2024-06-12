from tqdm import tqdm

import matplotlib.pyplot as plt
import numpy as np

from cmath import sqrt
from typing import Optional
from dataclasses import dataclass

from app_utils import Parameters


@dataclass
class Point:
    x: int | float
    y: int | float

    def to_array(self) -> np.array:
        return np.array([self.x, self.y])


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

        self.t_list = np.arange(0, t_end, eps, dtype=float)
        self.y_list = [self.y]
        self.p_list = [self.p]
        self.W_list = [self.W]
        self.gamma_list = [self.gamma]

        self.A = Point(x=-self.params.l, y=self.y)
        self.B = Point(x=self.params.l, y=self.y)

        self.circle_S = np.pi * (self.params.r ** 2)
        self.V_cylinder = self.circle_S * self.params.h

    def get_cylinder_volume(self,
                            upper_point: Point):

        if upper_point.y <= 0:
            return self.V_cylinder

        if upper_point.y >= self.params.h:
            return 0

        V_upper_part = self.circle_S * (self.params.h - upper_point.y)

        return self.V_cylinder - V_upper_part

    def solve(self):
        for _ in tqdm(self.t_list, total=self.t_list.shape[0]):
            self.current_iteration += 1

            # TODO: dp_dt
            Q_in, Q_out = self.get_Q_in(), self.get_Q_out()
            dp_dt = self.get_dp_dt(self.W, Q_in, Q_out, self.dW_dt) * self.eps
            ###################
            self.p += dp_dt
            self.p = self.clamp(self.p, 600, 2964)
            self.p_list.append(self.p)
            self.W = self.W  # TODO
            self.dW_dt = self.W - self.W_list[-1]
            self.W_list.append(self.W)
            ###################

            # TODO: d2y_dt2
            F_p, F_m = self.get_F_p(), self.get_F_m()
            V = self.get_cylinder_volume(self.A) * 2  # TODO
            F_a = self.get_F_a(V)
            d2y_dt2 = self.get_d2y_dt2(F_p, F_m, F_a) * self.eps
            ###################
            self.y += d2y_dt2
            self.y_list.append(self.y)
            ###################

            # TODO: d2gamma_dt2
            self.A.y += d2y_dt2
            cos_a = self.get_cos_alpha(np.array(self.A.to_array()))
            d2gamma_dt2 = self.get_d2gamma_d2t(F_a, cos_a) * self.eps
            ###################
            self.gamma += d2gamma_dt2
            self.gamma_list.append(self.gamma)
            ###################

    def get_d2y_dt2(self,
                    Fp: int | float,
                    Fm: int | float,
                    Fa: int | float) -> float:
        return (Fp + Fa - Fm) / self.params.m

    def get_dp_dt(self,
                  W: int | float,
                  Q_in: int | float,
                  Q_out: float,
                  dW_dt: int | float) -> float:
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

    def get_F_m(self) -> int | float:
        return self.params.m * self.params.g

    def get_Q_in(self) -> int | float:
        a, b, c = self.params.a, self.params.b, self.params.c

        D = b ** 2 - 4 * a * (c - self.p)
        root1 = (-b - sqrt(D)) / (2 * a)
        root2 = (-b + sqrt(D)) / (2 * a)
        return max(root1, root2, key=lambda x: x.real).real

    @staticmethod
    def get_cos_alpha(v1: np.array,
                      v2: Optional[np.array] = None) -> float:
        v2 = np.array([0, 1]) if v2 is None else v2
        dot_prod = np.dot(v1, v2)
        magnitude1, magnitude2 = np.linalg.norm(v1), np.linalg.norm(v2)

        return dot_prod / (magnitude1 * magnitude2)

    def get_Q_out(self) -> float:
        return self.params.xi * np.sqrt(2 * self.p / self.params.rho) * self.S_gap

    @staticmethod
    def clamp(value: int | float,
              min_value: int | float,
              max_value: int | float) -> int | float:
        return min(max(value, min_value), max_value)

    def __repr__(self) -> str:
        separator = "+" + ("-" * 50) + "\n"
        repr_str = (
            f"{separator}"
            f"| System of Equations\n"
            f"{separator}"
            f"| Params: {self.params}\n"
            f"{separator}"
            f"| Solution (Iteration: {self.current_iteration}):\n"
            f"| p = {self.p}\n"
            f"| y = {self.y}\n"
            f"| γ = {self.gamma}\n"
            f"| W = {self.W}\n"
            f"| A: {self.A}\n"
            f"| B: {self.B}\n"
            f"{separator}"
        )
        return repr_str

    def plot(self) -> None:

        if self.current_iteration == 0:
            raise RuntimeError("Use .solve() method first")

        y = self.y_list
        p = self.p_list
        gamma = self.gamma_list
        W = self.W_list
        t = self.t_list

        plt.figure(figsize=(18, 8))
        plt.subplot(2, 2, 1)
        plt.grid()
        plt.plot(t, y[:-1])
        plt.title('Y')
        plt.xlabel('Time (s)')
        plt.ylabel('Y')

        plt.subplot(2, 2, 2)
        plt.plot(t, gamma[:-1])
        plt.grid()
        plt.title('Gamma')
        plt.xlabel('Time (s)')
        plt.ylabel('Gamma')

        plt.subplot(2, 2, 3)
        plt.plot(t, p[:-1])
        plt.grid()
        plt.title('P')
        plt.xlabel('Time (s)')
        plt.ylabel('P')

        plt.subplot(2, 2, 4)
        plt.plot(t, W[:-1])
        plt.grid()
        plt.title('W')
        plt.xlabel('Time (s)')
        plt.ylabel('W')

        plt.tight_layout()
        plt.show()


def main() -> None:
    equations = SystemOfEquations(Parameters())
    equations.solve()
    equations.plot()
    print(equations)


if __name__ == '__main__':
    main()
