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

    def distance_to(self, other) -> float:
        return np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


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

    @staticmethod
    def F_x(A: Point, B: Point, x: int | float) -> int | float:
        up = (B.y - A.y) * (x ** 2 / 2 - A.x * x)
        down = B.x - A.x
        return up / down + A.y * x

    def get_area(self, A: Point, B: Point, down: int | float, up: int | float) -> int | float:
        return self.F_x(A, B, up) - self.F_x(A, B, down)

    def get_cylinder_volume(self, upper_point: Point) -> int | float:

        if upper_point.y <= 0:
            return self.V_cylinder

        if upper_point.y >= self.params.h:
            return 0

        V_upper_part = self.circle_S * (self.params.h - upper_point.y)

        return self.V_cylinder - V_upper_part

    def get_S_gap(self, upper_point: Point) -> int | float:
        return max(0, upper_point.y - self.params.h)

    def solve(self):
        for _ in tqdm(self.t_list):
            self.current_iteration += 1

            # TODO: dp_dt
            self.S_gap = self.get_S_gap(self.A) + self.get_S_gap(self.B)
            Q_in, Q_out = self.get_Q_in(), self.get_Q_out()
            dp_dt = self.get_dp_dt(self.W, Q_in, Q_out, self.dW_dt) * self.eps
            ###################
            self.p += dp_dt
            self.p = self.clamp(self.p, 600, 2964)
            self.p_list.append(self.p)
            self.W = self.get_area(self.A, self.B,
                                   down=self.A.x + self.params.r,
                                   up=self.B.x - self.params.r) * 10

            self.dW_dt = (self.W - self.W_list[-1]) / (2 * self.eps)
            self.W_list.append(self.W)
            ###################

            # TODO: d2y_dt2
            F_p, F_m = self.get_F_p(), self.get_F_m()
            V = self.get_cylinder_volume(self.A) + self.get_cylinder_volume(self.B)
            F_a = self.get_F_a(V)
            d2y_dt2 = self.get_d2y_dt2(F_p, F_m, F_a) * self.eps
            ###################
            self.y += d2y_dt2
            self.y_list.append(self.y)
            ###################

            # TODO: d2gamma_dt2
            if 0 <= self.gamma % 360 <= 90:
                self.B.y += d2y_dt2
            else:
                self.A.y += d2y_dt2

            # self.A.y += d2y_dt2
            # self.B.y += d2y_dt2

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
            max_elem = self.t_list.shape[0]

        y = self.y_list[:max_elem]
        p = self.p_list[:max_elem]
        gamma = self.gamma_list[:max_elem]
        W = self.W_list[:max_elem]
        t = self.t_list[:max_elem]

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
    equations = SystemOfEquations(Parameters(h=2, r=1.1),
                                  t_end=100,
                                  eps=1e-3)
    print(equations)
    equations.solve()
    print(equations)
    equations.plot()


if __name__ == '__main__':
    main()